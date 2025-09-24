import requests
from newspaper import Article
import pandas as pd
from datetime import datetime, timedelta
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
from collections import defaultdict
import os
from typing import List, Dict, Any
import json
import time
import random
import socket
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Download required NLTK data
try:
    nltk.download('punkt')
    nltk.download('vader_lexicon')
    nltk.download('stopwords')
except Exception as e:
    print(f"Warning: Could not download NLTK data: {e}")

class TariffAnalyzer:
    def __init__(self):
        # Use the specific API key
        self.api_key = '3a028cb39f384ca48b335ad35aad974d'
        self.base_url = "https://newsapi.org/v2"
        self.headers = {
            "X-Api-Key": self.api_key,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.sia = SentimentIntensityAnalyzer()
        
        # Reduced keywords to minimize API calls
        self.tariff_keywords = [
            'tariff', 'trade war'  # Only using the most important keywords
        ]
        
        # Impact categories
        self.impact_categories = {
            'economic': ['economy', 'market', 'trade', 'tariff', 'price', 'cost', 'inflation', 'gdp'],
            'business': ['company', 'business', 'industry', 'sector', 'manufacturing', 'production'],
            'political': ['policy', 'government', 'administration', 'diplomacy', 'negotiation'],
            'consumer': ['consumer', 'price', 'cost', 'inflation', 'purchasing', 'retail'],
            'international': ['international', 'global', 'foreign', 'trade', 'export', 'import']
        }

    def fetch_tariff_articles(self, days: int = 3) -> List[Dict[str, Any]]:  # Reduced days to 3
        """Fetch tariff-related articles from NewsAPI"""
        articles = []
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        # Format dates as strings
        from_date_str = from_date.strftime("%Y-%m-%d")
        to_date_str = to_date.strftime("%Y-%m-%d")

        print(f"Fetching articles from {from_date_str} to {to_date_str}")

        # Use a single keyword to minimize API calls
        keyword = 'tariff'  # Using just one keyword
        
        try:
            params = {
                "q": keyword,
                "from": from_date_str,
                "to": to_date_str,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20  # Reduced page size
            }

            # Add retry logic with longer delays
            max_retries = 5  # Increased retries
            base_delay = 5   # Increased base delay
            
            for attempt in range(max_retries):
                try:
                    print(f"Attempt {attempt + 1} of {max_retries}...")
                    
                    response = requests.get(
                        f"{self.base_url}/everything",
                        headers=self.headers,
                        params=params,
                        timeout=10,
                        verify=False
                    )
                    
                    if response.status_code == 429:  # Rate limit exceeded
                        retry_after = int(response.headers.get('Retry-After', base_delay))
                        wait_time = retry_after * (attempt + 1)  # Progressive waiting
                        print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    elif response.status_code == 401:
                        print("Error: Invalid API key. Please check your NewsAPI key.")
                        return []
                        
                    response.raise_for_status()
                    
                    # Add articles to list
                    new_articles = response.json().get("articles", [])
                    articles.extend(new_articles)
                    print(f"Successfully fetched {len(new_articles)} articles")
                    break
                    
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        print(f"Error fetching articles after {max_retries} attempts: {e}")
                    else:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                        time.sleep(delay)
            
        except Exception as e:
            print(f"Error processing articles: {e}")

        return articles

    def process_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single article to extract relevant information"""
        try:
            # Download and parse the article
            news_article = Article(article["url"])
            news_article.headers = self.headers
            news_article.download()
            news_article.parse()
            news_article.nlp()

            # Get sentiment scores
            sentiment_scores = self.sia.polarity_scores(news_article.text)
            
            # Analyze impact categories
            impact_scores = self._analyze_impact_categories(news_article.text)
            
            # Extract key information
            processed_article = {
                "title": article["title"],
                "url": article["url"],
                "published_at": article["publishedAt"],
                "source": article["source"]["name"],
                "content": news_article.text,
                "summary": news_article.summary,
                "keywords": news_article.keywords,
                "sentiment": {
                    "compound": sentiment_scores["compound"],
                    "positive": sentiment_scores["pos"],
                    "negative": sentiment_scores["neg"],
                    "neutral": sentiment_scores["neu"]
                },
                "impact_categories": impact_scores,
                "entities": self._extract_entities(news_article.text)
            }
            
            return processed_article
            
        except Exception as e:
            print(f"Error processing article: {e}")
            return {}

    def _analyze_impact_categories(self, text: str) -> Dict[str, float]:
        """Analyze text for impact in different categories"""
        impact_scores = {}
        
        for category, keywords in self.impact_categories.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    score += 1
            impact_scores[category] = min(1.0, score / len(keywords))
            
        return impact_scores

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract key entities from text"""
        entities = {
            "countries": [],
            "companies": [],
            "industries": []
        }
        
        # Simple entity extraction
        sentences = sent_tokenize(text)
        for sentence in sentences:
            # Look for country indicators
            if any(word in sentence.lower() for word in ['in', 'from', 'to', 'between']):
                entities["countries"].append(sentence)
            
            # Look for company indicators
            if any(word in sentence.lower() for word in ['announced', 'reported', 'said', 'according to']):
                entities["companies"].append(sentence)
            
            # Look for industry indicators
            if any(word in sentence.lower() for word in ['industry', 'sector', 'market']):
                entities["industries"].append(sentence)
        
        return entities

    def analyze_tariff_impact(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall impact of tariff-related news"""
        analysis = {
            "total_articles": len(articles),
            "sentiment_summary": {
                "positive": 0,
                "negative": 0,
                "neutral": 0
            },
            "impact_summary": defaultdict(float),
            "key_events": [],
            "trending_topics": defaultdict(int),
            "affected_countries": defaultdict(int),
            "affected_industries": defaultdict(int)
        }
        
        for article in articles:
            # Update sentiment summary
            sentiment = article["sentiment"]["compound"]
            if sentiment > 0.1:
                analysis["sentiment_summary"]["positive"] += 1
            elif sentiment < -0.1:
                analysis["sentiment_summary"]["negative"] += 1
            else:
                analysis["sentiment_summary"]["neutral"] += 1
            
            # Update impact summary
            for category, score in article["impact_categories"].items():
                analysis["impact_summary"][category] += score
            
            # Update trending topics
            for keyword in article["keywords"]:
                analysis["trending_topics"][keyword] += 1
            
            # Update affected countries and industries
            for country in article["entities"]["countries"]:
                analysis["affected_countries"][country] += 1
            for industry in article["entities"]["industries"]:
                analysis["affected_industries"][industry] += 1
            
            # Add significant events
            if abs(article["sentiment"]["compound"]) > 0.5:
                analysis["key_events"].append({
                    "title": article["title"],
                    "date": article["published_at"],
                    "impact": article["impact_categories"],
                    "sentiment": article["sentiment"]["compound"]
                })
        
        # Calculate averages
        for category in analysis["impact_summary"]:
            analysis["impact_summary"][category] /= len(articles)
        
        return analysis

    def save_analysis(self, analysis: Dict[str, Any], filename: str = "tariff_analysis.json"):
        """Save analysis results to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=4)

def main():
    analyzer = TariffAnalyzer()
    
    # Fetch articles
    print("Fetching tariff-related articles...")
    articles = analyzer.fetch_tariff_articles(days=3)  # Using 3 days instead of 7
    print(f"Found {len(articles)} articles")
    
    if not articles:
        print("No articles found. Please check your API key or try again later.")
        return
    
    # Process articles
    processed_articles = []
    for article in articles:
        processed = analyzer.process_article(article)
        if processed:
            processed_articles.append(processed)
    
    if processed_articles:
        # Analyze all processed articles
        analysis = analyzer.analyze_tariff_impact(processed_articles)
        
        # Save the analysis
        analyzer.save_analysis(analysis)
        
        # Print summary
        print("\nAnalysis Summary:")
        print(f"Total Articles Analyzed: {analysis['total_articles']}")
        print("\nSentiment Distribution:")
        print(f"Positive: {analysis['sentiment_summary']['positive']}")
        print(f"Negative: {analysis['sentiment_summary']['negative']}")
        print(f"Neutral: {analysis['sentiment_summary']['neutral']}")
        
        print("\nImpact Categories:")
        for category, score in analysis['impact_summary'].items():
            print(f"{category.capitalize()}: {score:.2f}")
        
        print("\nTop 5 Trending Topics:")
        sorted_topics = sorted(analysis['trending_topics'].items(), key=lambda x: x[1], reverse=True)[:5]
        for topic, count in sorted_topics:
            print(f"{topic}: {count}")
    else:
        print("No articles were successfully processed.")

if __name__ == "__main__":
    main() 