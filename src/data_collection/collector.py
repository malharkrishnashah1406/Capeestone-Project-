import requests
from newspaper import Article
import time
from datetime import datetime, timedelta
import random
from typing import List, Dict, Optional
import logging
from src.data_collection.database import Database
import json
import os
from bs4 import BeautifulSoup
import re
from fake_useragent import UserAgent
import backoff

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsCollector:
    def __init__(self):
        self.db = Database()
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Load existing article URLs
        self.existing_urls = self._load_existing_urls()
        
        # Initialize retry settings
        self.max_retries = 3
        self.retry_delay = 2
        
        # Initialize rate limiting
        self.rate_limit_delay = 1
        self.last_request_time = 0
        
        # Set API key
        self.api_key = os.getenv('NEWS_API_KEY', 'malhar1234')
        if not self.api_key:
            logger.warning("No News API key found. Using default key. Please set NEWS_API_KEY environment variable for better results.")

    def _load_existing_urls(self) -> set:
        """Load existing article URLs from database."""
        try:
            self.db.cur.execute("SELECT url FROM articles")
            return {row['url'] for row in self.db.cur.fetchall()}
        except Exception as e:
            logger.error(f"Error loading existing URLs: {e}")
            return set()

    @backoff.on_exception(backoff.expo, 
                         (requests.exceptions.RequestException, 
                          requests.exceptions.HTTPError),
                         max_tries=3)
    def _make_request(self, url: str, params: Dict = None) -> Optional[requests.Response]:
        """Make HTTP request with retry logic and rate limiting."""
        # Rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)
        
        # Update headers with new random user agent
        self.session.headers.update({'User-Agent': self.ua.random})
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            self.last_request_time = time.time()
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed for {url}: {e}")
            return None

    def _extract_content_with_bs4(self, url: str) -> Optional[str]:
        """Extract article content using BeautifulSoup as fallback."""
        try:
            response = self._make_request(url)
            if not response:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Try different content extraction strategies
            content = None
            
            # Strategy 1: Look for article content
            article = soup.find('article')
            if article:
                content = article.get_text(separator=' ', strip=True)
            
            # Strategy 2: Look for main content
            if not content:
                main = soup.find('main')
                if main:
                    content = main.get_text(separator=' ', strip=True)
            
            # Strategy 3: Look for content divs
            if not content:
                content_divs = soup.find_all('div', class_=re.compile(r'content|article|story|post'))
                if content_divs:
                    content = ' '.join(div.get_text(separator=' ', strip=True) for div in content_divs)
            
            # Strategy 4: Get all text from body
            if not content:
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True)
            
            if content:
                # Clean up the content
                content = re.sub(r'\s+', ' ', content)
                content = content.strip()
                
                # Ensure minimum content length
                if len(content) < 100:
                    return None
                    
                return content
                
        except Exception as e:
            logger.warning(f"BeautifulSoup extraction failed for {url}: {e}")
            return None

    def _extract_article_content(self, url: str) -> Optional[str]:
        """Extract article content with multiple fallback methods."""
        # Try newspaper3k first
        try:
            article = Article(url)
            article.download()
            article.parse()
            if article.text and len(article.text) > 100:
                return article.text
        except Exception as e:
            logger.warning(f"Newspaper3k extraction failed for {url}: {e}")
        
        # Try BeautifulSoup as fallback
        content = self._extract_content_with_bs4(url)
        if content:
            return content
            
        # If both methods fail, try direct request
        try:
            response = self._make_request(url)
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
                if len(text) > 100:
                    return text
        except Exception as e:
            logger.warning(f"Direct request extraction failed for {url}: {e}")
            
        return None

    def _fetch_news_from_api(self, category: str) -> List[Dict]:
        """Fetch news from News API with error handling."""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
            # Format dates for API
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            # Make API request
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': category,
                'from': start_date_str,
                'to': end_date_str,
                'language': 'en',
                'sortBy': 'publishedAt',
                'apiKey': self.api_key
            }
            
            response = self._make_request(url, params=params)
            if not response:
                logger.warning(f"Failed to fetch news for category: {category}")
                return []
                
            data = response.json()
            
            if data.get('status') != 'ok':
                error_msg = data.get('message', 'Unknown error')
                logger.error(f"News API error: {error_msg}")
                
                # If API key is invalid, try alternative sources
                if 'apiKey' in error_msg.lower():
                    logger.warning("API key issue detected. Using alternative news sources...")
                    return self._fetch_news_from_alternative_sources(category)
                    
                return []
                
            return data.get('articles', [])
            
        except Exception as e:
            logger.error(f"Error fetching news from API: {e}")
            return self._fetch_news_from_alternative_sources(category)

    def _fetch_news_from_alternative_sources(self, category: str) -> List[Dict]:
        """Fetch news from alternative sources when News API fails."""
        try:
            # List of alternative news sources
            sources = [
                f"https://www.reuters.com/business/{category}",
                f"https://www.bloomberg.com/{category}",
                f"https://www.ft.com/{category}",
                f"https://www.wsj.com/news/{category}"
            ]
            
            articles = []
            for source in sources:
                try:
                    response = self._make_request(source)
                    if response:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        # Extract articles based on common patterns
                        article_elements = soup.find_all(['article', 'div'], class_=re.compile(r'article|story|post'))
                        
                        for element in article_elements:
                            title = element.find(['h1', 'h2', 'h3'])
                            link = element.find('a')
                            
                            if title and link:
                                articles.append({
                                    'title': title.get_text(strip=True),
                                    'url': link.get('href'),
                                    'source': {'name': source.split('/')[2]},
                                    'publishedAt': datetime.now().isoformat(),
                                    'category': category
                                })
                except Exception as e:
                    logger.warning(f"Failed to fetch from {source}: {e}")
                    continue
                    
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching from alternative sources: {e}")
            return []

    def _process_article(self, article: Dict) -> Optional[Dict]:
        """Process a single article with error handling."""
        try:
            url = article.get('url')
            if not url or url in self.existing_urls:
                return None
                
            # Extract content
            content = self._extract_article_content(url)
            if not content:
                logger.warning(f"Could not extract content for {url}")
                return None
                
            # Create article record
            article_record = {
                'title': article.get('title', ''),
                'content': content,
                'url': url,
                'source': article.get('source', {}).get('name', ''),
                'published_at': article.get('publishedAt'),
                'category': article.get('category', 'general')
            }
            
            # Store in database
            self.db.store_article(article_record)
            self.existing_urls.add(url)
            
            logger.info(f"Added article: {article_record['title']} - {article_record['source']} (Category: {article_record['category']})")
            logger.info(f"Content length: {len(content)} characters")
            
            return article_record
            
        except Exception as e:
            logger.error(f"Error processing article {url}: {e}")
            return None

    def collect_news(self):
        """Collect news articles with comprehensive error handling."""
        logger.info("Starting news collection...")
        logger.info(f"Loaded {len(self.existing_urls)} existing article URLs")
        
        # Calculate date range for logging
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        logger.info(f"Fetching news from {start_date} to {end_date}")
        
        # Categories to fetch
        categories = ['business', 'technology', 'finance', 'economy']
        
        for category in categories:
            logger.info(f"Fetching {category} news...")
            
            # Fetch articles from API
            articles = self._fetch_news_from_api(category)
            logger.info(f"Found {len(articles)} articles for {category}")
            
            # Process each article
            for article in articles:
                self._process_article(article)
                
            # Add delay between categories
            time.sleep(self.rate_limit_delay)
            
        logger.info("News collection completed")

def main():
    collector = NewsCollector()
    collector.collect_news()

if __name__ == "__main__":
    main() 