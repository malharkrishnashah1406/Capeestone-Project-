import os
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Set
import requests
from newspaper import Article
from bs4 import BeautifulSoup
from multiprocessing import Pool, cpu_count
import urllib3
from src.data_collection.database import Database
from config.config import NEWS_API_KEY, NEWS_SOURCES, SCRAPING_CONFIG

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_news(category: str, start_time: datetime, end_time: datetime) -> List[Dict]:
    """Fetch news articles for a specific category using News API."""
    articles = []
    if not NEWS_API_KEY:
        print("News API key not configured. Skipping news collection.")
        return articles

    try:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            'category': category,
            'language': 'en',
            'apiKey': NEWS_API_KEY,
            'pageSize': 20,
            'from': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'to': end_time.strftime('%Y-%m-%dT%H:%M:%S')
        }
        
        print(f"Fetching {category} news...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                articles_data = data.get('articles', [])
                print(f"Found {len(articles_data)} articles for {category}")
                
                for article in articles_data:
                    if article.get('url'):
                        articles.append({
                            'title': article.get('title', ''),
                            'url': article.get('url', ''),
                            'published_at': article.get('publishedAt', ''),
                            'source': article.get('source', {}).get('name', ''),
                            'description': article.get('description', ''),
                            'content': article.get('content', '')
                        })
            else:
                print(f"News API returned error for {category}: {data.get('message', 'Unknown error')}")
        elif response.status_code == 429:
            print("Rate limit exceeded. Waiting before next request...")
            time.sleep(30)
        else:
            print(f"Request failed with status code {response.status_code}")
            
    except Exception as e:
        print(f"Error fetching {category} news: {str(e)}")
        
    return articles

def extract_article_content(url: str) -> str:
    """Extract article content with improved error handling and retries."""
    max_retries = 2
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            # Try newspaper3k first
            article = Article(url)
            article.download()
            article.parse()
            
            if article.text and len(article.text.strip()) >= 15000:
                return article.text
                
            # If newspaper3k fails, try direct content extraction
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript']):
                    element.decompose()
                
                # Try to find main content
                main_content = (
                    soup.find('main') or 
                    soup.find('article') or 
                    soup.find('div', class_=['content', 'article', 'post', 'story', 'entry-content', 'article-body'])
                )
                
                if main_content:
                    text = main_content.get_text()
                else:
                    text = soup.get_text()
                
                # Clean up the text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                if text and len(text.strip()) >= 15000:
                    return text
                    
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print(f"Error extracting content from {url}: {str(e)}")
    
    return None

def fetch_category_news(args):
    """Fetch news for a specific category."""
    category, start_time, end_time, existing_urls = args
    try:
        print(f"Fetching {category} news...")
        articles = fetch_news(category, start_time, end_time)
        
        if articles:
            print(f"Found {len(articles)} articles for {category}")
            new_articles = []
            
            for article in articles:
                if article['url'] not in existing_urls:
                    try:
                        content = extract_article_content(article['url'])
                        if content and len(content) >= 15000:
                            article['content'] = content
                            article['category'] = category
                            new_articles.append(article)
                            print(f"Added article: {article['title']} - {article['source']} (Category: {category})")
                            print(f"Content length: {len(content)} characters")
                        else:
                            print(f"Skipping article {article['url']} - insufficient content")
                    except Exception as e:
                        print(f"Error in article extraction for {article['url']}: {str(e)}")
            
            return new_articles
    except Exception as e:
        print(f"Error fetching {category} news: {str(e)}")
        return []

def main():
    """Main function to run the news collector."""
    print("Starting news collection...")
    
    # Initialize database
    db = Database()
    
    # Load existing URLs
    existing_urls = set(db.get_all_article_urls())
    print(f"Loaded {len(existing_urls)} existing article URLs")
    
    # Set up parallel processing
    num_processes = min(cpu_count(), 4)
    pool = Pool(processes=num_processes)
    
    while True:
        try:
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=30)
            print(f"Fetching news from {start_time} to {end_time}")
            
            # Fetch news for each category in parallel
            categories = ['business', 'technology', 'science', 'health', 'entertainment', 'sports', 'general']
            results = pool.map(fetch_category_news, [(cat, start_time, end_time, existing_urls) for cat in categories])
            
            # Process results
            new_articles = []
            for category_results in results:
                if category_results:
                    new_articles.extend(category_results)
            
            # Store new articles
            if new_articles:
                print(f"Storing {len(new_articles)} new articles")
                for article in new_articles:
                    try:
                        db.insert_article(article)
                        existing_urls.add(article['url'])
                        print(f"Successfully stored article: {article['title']}")
                    except Exception as e:
                        print(f"Error inserting article {article.get('url', 'Unknown URL')}: {str(e)}")
            
            # Wait before next cycle
            wait_time = 30
            print(f"Waiting {wait_time} seconds for next collection cycle...")
            time.sleep(wait_time)
            
        except KeyboardInterrupt:
            print("\nStopping news collection...")
            pool.close()
            pool.join()
            break
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            time.sleep(30)

if __name__ == "__main__":
    main() 