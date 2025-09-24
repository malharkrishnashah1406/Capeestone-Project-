from typing import List, Optional
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from .models import Event, EventType
import re

class EventCollector:
    def __init__(self):
        # Download required NLTK data
        nltk.download('punkt')
        nltk.download('stopwords')
        
        # Initialize stopwords
        self.stop_words = set(stopwords.words('english'))
        
        # News API endpoints and keys (to be configured)
        self.news_api_key = None
        self.news_sources = [
            "reuters.com",
            "bloomberg.com",
            "economictimes.indiatimes.com",
            "livemint.com",
            "moneycontrol.com"
        ]
        
        # Event type keywords
        self.event_type_keywords = {
            EventType.POLICY_CHANGE: [
                "policy", "regulation", "law", "bill", "government",
                "RBI", "SEBI", "interest rate", "tax", "subsidy"
            ],
            EventType.MARKET_SHIFT: [
                "funding", "investment", "VC", "venture capital",
                "market trend", "consumer spending", "demand"
            ],
            EventType.REGULATORY_UPDATE: [
                "regulation", "compliance", "law", "rule", "standard",
                "guideline", "requirement", "mandate"
            ],
            EventType.COMPETITOR_ACTION: [
                "competitor", "rival", "competition", "market share",
                "acquisition", "merger", "partnership"
            ],
            EventType.TECHNOLOGY_TREND: [
                "technology", "innovation", "disruption", "AI",
                "blockchain", "startup", "digital"
            ],
            EventType.ECONOMIC_INDICATOR: [
                "economy", "GDP", "inflation", "interest rate",
                "market", "growth", "recession"
            ],
            EventType.INDUSTRY_NEWS: [
                "industry", "sector", "market", "trend",
                "development", "change", "shift"
            ],
            EventType.FUNDING_ANNOUNCEMENT: [
                "funding", "investment", "raise", "round",
                "series", "venture", "capital"
            ],
            EventType.PARTNERSHIP: [
                "partnership", "collaboration", "alliance",
                "joint venture", "agreement", "deal"
            ],
            EventType.PRODUCT_LAUNCH: [
                "launch", "product", "service", "release",
                "introduction", "announcement", "new"
            ]
        }
    
    def set_news_api_key(self, api_key: str) -> None:
        """Set the News API key"""
        self.news_api_key = api_key
    
    def _classify_event_type(self, text: str) -> EventType:
        """Classify the event type based on keywords"""
        text_lower = text.lower()
        max_matches = 0
        event_type = EventType.INDUSTRY_NEWS  # Default
        
        for ev_type, keywords in self.event_type_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > max_matches:
                max_matches = matches
                event_type = ev_type
                
        return event_type
    
    def _calculate_severity(self, text: str) -> float:
        """Calculate event severity based on keywords and sentiment"""
        severity_indicators = {
            "high": ["crisis", "crash", "emergency", "urgent", "critical"],
            "medium": ["change", "shift", "trend", "update", "announcement"],
            "low": ["minor", "slight", "gradual", "expected", "planned"]
        }
        
        text_lower = text.lower()
        severity = 0.5  # Default
        
        for level, keywords in severity_indicators.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if level == "high" and matches > 0:
                severity = min(1.0, severity + 0.3)
            elif level == "medium" and matches > 0:
                severity = min(1.0, severity + 0.1)
            elif level == "low" and matches > 0:
                severity = max(0.0, severity - 0.1)
                
        return severity
    
    def _calculate_confidence(self, text: str, source: str) -> float:
        """Calculate confidence score based on source reliability and content"""
        source_reliability = {
            "reuters.com": 0.9,
            "bloomberg.com": 0.9,
            "economictimes.indiatimes.com": 0.8,
            "livemint.com": 0.8,
            "moneycontrol.com": 0.8
        }
        
        # Base confidence on source
        confidence = source_reliability.get(source, 0.5)
        
        # Adjust based on content quality
        sentences = sent_tokenize(text)
        if len(sentences) >= 3:  # More detailed articles are more reliable
            confidence = min(1.0, confidence + 0.1)
            
        if any(char.isdigit() for char in text):  # Articles with numbers are more reliable
            confidence = min(1.0, confidence + 0.1)
            
        return confidence
    
    def collect_news_events(
        self,
        query: str,
        days: int = 7,
        location: Optional[str] = None
    ) -> List[Event]:
        """Collect events from news sources"""
        if not self.news_api_key:
            raise ValueError("News API key not set")
            
        events = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Format dates for API
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = end_date.strftime("%Y-%m-%d")
        
        # Prepare query
        base_query = f"startup OR technology OR business OR economy"
        if query:
            base_query += f" AND {query}"
            
        # Make API request
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": base_query,
            "from": from_date,
            "to": to_date,
            "sources": ",".join(self.news_sources),
            "apiKey": self.news_api_key,
            "language": "en",
            "sortBy": "relevancy"
        }
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"News API request failed: {response.text}")
            
        data = response.json()
        
        # Process articles
        for article in data.get("articles", []):
            # Extract location
            location = "Global"  # Default
            if "India" in article.get("title", "") or "India" in article.get("description", ""):
                location = "India"
                
            # Create event
            event = Event(
                event_type=self._classify_event_type(article["title"]),
                title=article["title"],
                description=article["description"],
                source=article["source"]["name"],
                date=datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"),
                location=location,
                severity=self._calculate_severity(article["title"]),
                confidence=self._calculate_confidence(
                    article["description"],
                    article["url"]
                ),
                raw_text=article["content"]
            )
            
            events.append(event)
            
        return events
    
    def collect_rss_events(self, rss_urls: List[str]) -> List[Event]:
        """Collect events from RSS feeds"""
        events = []
        
        for url in rss_urls:
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "xml")
                
                for item in soup.find_all("item"):
                    # Extract location
                    location = "Global"  # Default
                    if "India" in item.title.text or "India" in item.description.text:
                        location = "India"
                        
                    # Create event
                    event = Event(
                        event_type=self._classify_event_type(item.title.text),
                        title=item.title.text,
                        description=item.description.text,
                        source=url,
                        date=datetime.strptime(
                            item.pubDate.text,
                            "%a, %d %b %Y %H:%M:%S %z"
                        ),
                        location=location,
                        severity=self._calculate_severity(item.title.text),
                        confidence=self._calculate_confidence(
                            item.description.text,
                            url
                        ),
                        raw_text=item.description.text
                    )
                    
                    events.append(event)
                    
            except Exception as e:
                print(f"Error processing RSS feed {url}: {str(e)}")
                
        return events

def main():
    # Example usage
    collector = EventCollector()
    collector.set_news_api_key("your-api-key")
    
    # Collect events
    events = collector.collect_news_events(
        query="Indian startup"
    )
    
    # Print events
    for event in events:
        print(f"\nEvent: {event.title}")
        print(f"Type: {event.event_type}")
        print(f"Date: {event.date}")
        print(f"Location: {event.location}")
        print(f"Severity: {event.severity}")
        print(f"Confidence: {event.confidence}")
        print(f"Description: {event.description}")

if __name__ == "__main__":
    main() 