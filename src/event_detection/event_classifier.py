"""
Event Classifier Module.

This module provides event classification and analysis capabilities.
"""

from typing import List, Dict, Any
import logging
import random
from datetime import datetime

logger = logging.getLogger(__name__)


class EventClassifier:
    """Classifies and analyzes news events."""
    
    def __init__(self):
        self.categories = [
            'funding', 'acquisition', 'ipo', 'partnership', 'product_launch',
            'regulation', 'policy_change', 'rate_hike', 'monetary_policy',
            'market_crash', 'recession', 'competition', 'technology',
            'cybersecurity', 'fraud', 'pandemic', 'trade_war', 'political_instability'
        ]
    
    def process_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of articles to extract and classify events."""
        processed_articles = []
        
        for article in articles:
            try:
                processed_article = self._process_single_article(article)
                processed_articles.append(processed_article)
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                article['event_category'] = 'unknown'
                article['sentiment'] = 0.0
                article['confidence'] = 0.0
                processed_articles.append(article)
        
        return processed_articles
    
    def _process_single_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single article to extract event information."""
        title = article.get('title', '')
        description = article.get('description', '')
        content = article.get('content', '')
        
        full_text = f"{title} {description} {content}".lower()
        
        # Classify event category
        event_category = self._classify_event_category(full_text)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(full_text)
        
        # Calculate confidence
        confidence = self._calculate_confidence(full_text, event_category)
        
        # Add event information to article
        article['event_category'] = event_category
        article['sentiment'] = sentiment
        article['confidence'] = confidence
        article['processed_at'] = datetime.now().isoformat()
        
        return article
    
    def _classify_event_category(self, text: str) -> str:
        """Classify the event category based on text content."""
        category_scores = {}
        
        for category in self.categories:
            score = 0
            
            if category == 'funding':
                keywords = ['funding', 'investment', 'raise', 'series', 'round', 'capital']
            elif category == 'acquisition':
                keywords = ['acquisition', 'acquire', 'buyout', 'merger', 'purchase']
            elif category == 'regulation':
                keywords = ['regulation', 'regulatory', 'compliance', 'policy', 'rule']
            elif category == 'market_crash':
                keywords = ['crash', 'plunge', 'drop', 'fall', 'decline', 'crisis']
            elif category == 'technology':
                keywords = ['technology', 'tech', 'innovation', 'digital', 'software']
            else:
                keywords = []
            
            for keyword in keywords:
                if keyword in text:
                    score += 1
            
            category_scores[category] = score
        
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        return 'general'
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of the text."""
        positive_words = ['growth', 'success', 'profit', 'increase', 'rise', 'gain']
        negative_words = ['decline', 'loss', 'decrease', 'fall', 'drop', 'crisis']
        
        words = text.split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_words = len(words)
        if total_words == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / total_words
        return max(-1.0, min(1.0, sentiment * 10))
    
    def _calculate_confidence(self, text: str, category: str) -> float:
        """Calculate confidence score for the classification."""
        if category == 'general':
            return 0.3
        
        # Simple confidence based on text length and category
        base_confidence = min(0.8, len(text) / 1000)
        category_confidence = 0.5 if category in self.categories else 0.3
        
        return (base_confidence + category_confidence) / 2
    
    def get_event_impact(self, article: Dict[str, Any]) -> float:
        """Calculate impact score for an event."""
        try:
            confidence = article.get('confidence', 0.0)
            sentiment = abs(article.get('sentiment', 0.0))
            category = article.get('event_category', 'general')
            
            category_multipliers = {
                'funding': 0.8,
                'acquisition': 0.9,
                'ipo': 1.0,
                'market_crash': 1.0,
                'recession': 1.0,
                'regulation': 0.7,
                'general': 0.3
            }
            
            multiplier = category_multipliers.get(category, 0.5)
            impact = (confidence * 0.6 + sentiment * 0.4) * multiplier
            
            return max(0.0, min(1.0, impact))
        except Exception as e:
            logger.error(f"Error calculating event impact: {e}")
            return 0.0