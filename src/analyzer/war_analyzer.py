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

class WarAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY', '3a028cb39f384ca48b335ad35aad974d')
        self.base_url = "https://newsapi.org/v2"
        self.headers = {
            "X-Api-Key": self.api_key,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.sia = SentimentIntensityAnalyzer()
        
        # War-related keywords
        self.war_keywords = [
            'war', 'conflict', 'military', 'attack', 'battle',
            'invasion', 'defense', 'troops', 'casualties',
            'peace', 'treaty', 'ceasefire', 'diplomacy',
            'sanctions', 'weapons', 'nuclear', 'missile',
            'terrorism', 'terrorist', 'militant', 'rebel',
            'insurgency', 'civil war', 'proxy war'
        ]
        
        # Impact categories
        self.impact_categories = {
            'economic': ['economy', 'market', 'trade', 'sanctions', 'oil', 'gas', 'currency', 'inflation'],
            'humanitarian': ['refugee', 'displaced', 'casualties', 'civilian', 'humanitarian', 'aid'],
            'political': ['diplomacy', 'treaty', 'alliance', 'sanctions', 'resolution', 'united nations'],
            'military': ['troops', 'weapons', 'attack', 'defense', 'military', 'casualties'],
            'social': ['protest', 'demonstration', 'refugee', 'displacement', 'humanitarian']
        }

    def fetch_war_articles(self, days: int = 7) -> List[Dict[str, Any]]:
        """Fetch war-related articles from NewsAPI"""
        articles = []
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        # Format dates as strings
        from_date_str = from_date.strftime("%Y-%m-%d")
        to_date_str = to_date.strftime("%Y-%m-%d")

        print(f"Fetching articles from {from_date_str} to {to_date_str}")

        # Fetch articles for each keyword
        for keyword in self.war_keywords:
            try:
                params = {
                    "q": keyword,
                    "from": from_date_str,
                    "to": to_date_str,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 10  # Limit results per keyword
                }

                # Add retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = requests.get(
                            f"{self.base_url}/everything",
                            headers=self.headers,
                            params=params,
                            timeout=10,
                            verify=False  # Disable SSL verification
                        )
                        response.raise_for_status()
                        
                        # Add articles to list
                        new_articles = response.json().get("articles", [])
                        articles.extend(new_articles)
                        print(f"Successfully fetched {len(new_articles)} articles for keyword '{keyword}'")
                        break
                        
                    except requests.exceptions.RequestException as e:
                        if attempt == max_retries - 1:
                            print(f"Error fetching articles for keyword {keyword} after {max_retries} attempts: {e}")
                        else:
                            print(f"Attempt {attempt + 1} failed for keyword {keyword}, retrying...")
                            time.sleep(2)  # Wait before retrying
                
            except Exception as e:
                print(f"Error processing keyword {keyword}: {e}")
                continue

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
            "locations": [],
            "organizations": [],
            "people": []
        }
        
        # Simple entity extraction (can be enhanced with NER)
        sentences = sent_tokenize(text)
        for sentence in sentences:
            # Look for location indicators
            if any(word in sentence.lower() for word in ['in', 'at', 'from', 'to']):
                entities["locations"].append(sentence)
            
            # Look for organization indicators
            if any(word in sentence.lower() for word in ['announced', 'reported', 'said', 'according to']):
                entities["organizations"].append(sentence)
            
            # Look for people indicators
            if any(word in sentence.lower() for word in ['said', 'announced', 'reported', 'according to']):
                entities["people"].append(sentence)
        
        return entities

    def analyze_war_impact(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall impact of war-related news"""
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
            "geographic_distribution": defaultdict(int)
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
            
            # Update geographic distribution
            for location in article["entities"]["locations"]:
                analysis["geographic_distribution"][location] += 1
            
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

    def save_analysis(self, analysis: Dict[str, Any], filename: str = "war_analysis.json"):
        """Save analysis results to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=4)

def main():
    analyzer = WarAnalyzer()
    
    # Fetch articles
    print("Fetching war-related articles...")
    articles = analyzer.fetch_war_articles(days=7)
    print(f"Found {len(articles)} articles")
    
    # Process just one article for demonstration
    if articles:
        print("\nProcessing a single article for demonstration...")
        article = random.choice(articles)  # Pick a random article
        processed = analyzer.process_article(article)
        
        if processed:
            print("\nArticle Details:")
            print(f"Title: {processed['title']}")
            print(f"Source: {processed['source']}")
            print(f"Published: {processed['published_at']}")
            print("\nSummary:")
            print(processed['summary'])
            print("\nSentiment Analysis:")
            print(f"Compound Score: {processed['sentiment']['compound']:.2f}")
            print(f"Positive: {processed['sentiment']['positive']:.2f}")
            print(f"Negative: {processed['sentiment']['negative']:.2f}")
            print(f"Neutral: {processed['sentiment']['neutral']:.2f}")
            print("\nImpact Categories:")
            for category, score in processed['impact_categories'].items():
                print(f"{category.capitalize()}: {score:.2f}")
            print("\nKeywords:")
            print(", ".join(processed['keywords']))
        else:
            print("Failed to process the selected article. Please try another one.")
    else:
        print("No articles found.")

if __name__ == "__main__":
    main() 