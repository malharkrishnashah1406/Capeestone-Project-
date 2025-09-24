"""
News Collector Module.

This module provides news collection capabilities from various sources
for the startup performance prediction system.
"""

from typing import List, Dict, Any, Optional
import requests
import logging
from datetime import datetime, timedelta
import time
import random

logger = logging.getLogger(__name__)


class NewsCollector:
    """Collects news from various sources."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "demo_key"  # Use demo key if none provided
        self.base_url = "https://newsapi.org/v2"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'StartupPerformancePredictor/1.0'
        })
    
    def collect_startup_news(self, startup_name: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Collect news about a specific startup.
        
        Args:
            startup_name: Name of the startup
            days_back: Number of days to look back
            
        Returns:
            List of news articles
        """
        try:
            # For demo purposes, return mock data
            return self._generate_mock_news(startup_name, "startup", days_back)
        except Exception as e:
            logger.error(f"Error collecting startup news for {startup_name}: {e}")
            return []
    
    def collect_industry_news(self, keywords: List[str], days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Collect industry news based on keywords.
        
        Args:
            keywords: List of keywords to search for
            days_back: Number of days to look back
            
        Returns:
            List of news articles
        """
        try:
            # For demo purposes, return mock data
            return self._generate_mock_news(" ".join(keywords), "industry", days_back)
        except Exception as e:
            logger.error(f"Error collecting industry news: {e}")
            return []
    
    def collect_government_releases(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Collect government policy releases.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List of government releases
        """
        try:
            # For demo purposes, return mock data
            return self._generate_mock_news("government policy", "government", days_back)
        except Exception as e:
            logger.error(f"Error collecting government releases: {e}")
            return []
    
    def collect_global_events(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Collect global events and news.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List of global events
        """
        try:
            # For demo purposes, return mock data
            return self._generate_mock_news("global events", "global", days_back)
        except Exception as e:
            logger.error(f"Error collecting global events: {e}")
            return []
    
    def _generate_mock_news(self, query: str, category: str, days_back: int) -> List[Dict[str, Any]]:
        """Generate mock news data for demo purposes."""
        mock_articles = []
        
        # Generate 3-8 mock articles
        num_articles = random.randint(3, 8)
        
        for i in range(num_articles):
            # Generate random date within the specified range
            days_ago = random.randint(0, days_back)
            article_date = datetime.now() - timedelta(days=days_ago)
            
            # Generate mock article
            article = {
                "title": f"Mock {category.title()} News Article {i+1} about {query}",
                "description": f"This is a mock description for a {category} news article about {query}. "
                              f"It contains relevant information that would be useful for analysis.",
                "content": f"This is the full content of a mock {category} news article about {query}. "
                          f"It provides detailed information about recent developments and their potential impact. "
                          f"The article discusses various aspects of the topic and provides insights for stakeholders.",
                "url": f"https://mock-news.com/{category}/{i+1}",
                "published_at": article_date.isoformat(),
                "source": {
                    "name": f"Mock {category.title()} News",
                    "url": "https://mock-news.com"
                },
                "author": f"Mock Author {i+1}",
                "category": category,
                "keywords": [query, category, "mock", "demo"],
                "sentiment": random.uniform(-0.5, 0.5),  # Random sentiment between -0.5 and 0.5
                "relevance_score": random.uniform(0.3, 1.0),  # Random relevance score
                "impact_score": random.uniform(0.1, 0.9)  # Random impact score
            }
            
            mock_articles.append(article)
        
        return mock_articles
    
    def search_news(self, query: str, language: str = "en", 
                   sort_by: str = "publishedAt", page_size: int = 20) -> List[Dict[str, Any]]:
        """
        Search for news articles.
        
        Args:
            query: Search query
            language: Language code
            sort_by: Sort order
            page_size: Number of articles to return
            
        Returns:
            List of news articles
        """
        try:
            # For demo purposes, return mock data
            return self._generate_mock_news(query, "search", 7)
        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return []
    
    def get_article_content(self, url: str) -> Optional[str]:
        """
        Extract content from a news article URL.
        
        Args:
            url: Article URL
            
        Returns:
            Article content or None if failed
        """
        try:
            # For demo purposes, return mock content
            return f"Mock article content from {url}. This would be the actual content extracted from the URL."
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def analyze_article_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of article text.
        
        Args:
            text: Article text
            
        Returns:
            Sentiment analysis results
        """
        try:
            # Simple mock sentiment analysis
            # In a real implementation, this would use NLP libraries
            words = text.lower().split()
            positive_words = ['good', 'great', 'excellent', 'positive', 'success', 'growth', 'profit']
            negative_words = ['bad', 'terrible', 'negative', 'loss', 'decline', 'crisis', 'problem']
            
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            total_words = len(words)
            if total_words == 0:
                return {"sentiment": 0.0, "confidence": 0.0}
            
            sentiment = (positive_count - negative_count) / total_words
            confidence = min(1.0, (positive_count + negative_count) / total_words * 10)
            
            return {
                "sentiment": max(-1.0, min(1.0, sentiment)),
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {"sentiment": 0.0, "confidence": 0.0}
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of keywords
        """
        try:
            # Simple mock keyword extraction
            # In a real implementation, this would use NLP libraries
            words = text.lower().split()
            
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
            
            filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
            
            # Count word frequency
            word_count = {}
            for word in filtered_words:
                word_count[word] = word_count.get(word, 0) + 1
            
            # Sort by frequency and return top keywords
            sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
            keywords = [word for word, count in sorted_words[:max_keywords]]
            
            return keywords
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []