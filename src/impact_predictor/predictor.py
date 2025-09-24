from typing import List, Dict, Optional
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .models import Event, EventType, FinancialMetric, ImpactPrediction
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import re
from textblob import TextBlob

class ImpactPredictor:
    def __init__(self):
        # Download required NLTK data
        nltk.download('punkt')
        nltk.download('stopwords')
        
        # Initialize stopwords
        self.stop_words = set(stopwords.words('english'))
        
        # Impact direction keywords
        self.impact_direction_keywords = {
            "positive": [
                "growth", "increase", "rise", "boost", "improve",
                "success", "profit", "gain", "surge", "expansion"
            ],
            "negative": [
                "decline", "fall", "drop", "loss", "decrease",
                "struggle", "challenge", "risk", "threat", "pressure"
            ]
        }
        
        # Impact magnitude keywords
        self.impact_magnitude_keywords = {
            "high": [
                "significant", "major", "substantial", "dramatic",
                "considerable", "huge", "massive", "enormous"
            ],
            "medium": [
                "moderate", "noticeable", "measurable", "appreciable",
                "reasonable", "fair", "adequate"
            ],
            "low": [
                "slight", "minor", "marginal", "minimal", "small",
                "limited", "negligible"
            ]
        }
        
        # Timeframe keywords
        self.timeframe_keywords = {
            "short_term": [
                "immediate", "near-term", "short-term", "quick",
                "soon", "rapid", "fast", "urgent"
            ],
            "medium_term": [
                "medium-term", "coming months", "next quarter",
                "next few months", "in the near future"
            ],
            "long_term": [
                "long-term", "future", "years to come", "over time",
                "eventually", "in the long run"
            ]
        }
    
    def _calculate_impact_direction(self, text: str) -> float:
        """Calculate impact direction score (-1 to 1)"""
        text_lower = text.lower()
        score = 0.0
        
        # Count positive and negative keywords
        positive_matches = sum(1 for keyword in self.impact_direction_keywords["positive"]
                             if keyword in text_lower)
        negative_matches = sum(1 for keyword in self.impact_direction_keywords["negative"]
                             if keyword in text_lower)
        
        # Calculate score
        total_matches = positive_matches + negative_matches
        if total_matches > 0:
            score = (positive_matches - negative_matches) / total_matches
            
        return score
    
    def _calculate_impact_magnitude(self, text: str) -> float:
        """Calculate impact magnitude score (0 to 1)"""
        text_lower = text.lower()
        score = 0.5  # Default
        
        # Count magnitude keywords
        high_matches = sum(1 for keyword in self.impact_magnitude_keywords["high"]
                          if keyword in text_lower)
        medium_matches = sum(1 for keyword in self.impact_magnitude_keywords["medium"]
                           if keyword in text_lower)
        low_matches = sum(1 for keyword in self.impact_magnitude_keywords["low"]
                         if keyword in text_lower)
        
        # Calculate score
        if high_matches > 0:
            score = 1.0
        elif medium_matches > 0:
            score = 0.7
        elif low_matches > 0:
            score = 0.3
            
        return score
    
    def _calculate_timeframe(self, text: str) -> str:
        """Determine impact timeframe"""
        text_lower = text.lower()
        
        # Count timeframe keywords
        short_matches = sum(1 for keyword in self.timeframe_keywords["short_term"]
                          if keyword in text_lower)
        medium_matches = sum(1 for keyword in self.timeframe_keywords["medium_term"]
                           if keyword in text_lower)
        long_matches = sum(1 for keyword in self.timeframe_keywords["long_term"]
                         if keyword in text_lower)
        
        # Determine timeframe
        if short_matches > 0:
            return "short_term"
        elif medium_matches > 0:
            return "medium_term"
        elif long_matches > 0:
            return "long_term"
        else:
            return "medium_term"  # Default
    
    def _calculate_confidence(self, text: str, event: Event) -> float:
        """Calculate prediction confidence score (0 to 1)"""
        confidence = event.confidence  # Start with event confidence
        
        # Adjust based on text quality
        sentences = sent_tokenize(text)
        if len(sentences) >= 3:  # More detailed analysis
            confidence = min(1.0, confidence + 0.1)
            
        if any(char.isdigit() for char in text):  # Quantitative analysis
            confidence = min(1.0, confidence + 0.1)
            
        # Adjust based on event type
        if event.event_type in [EventType.POLICY_CHANGE, EventType.MARKET_SHIFT]:
            confidence = min(1.0, confidence + 0.1)
            
        return confidence
    
    def predict_impact(
        self,
        event: Event,
        metric: FinancialMetric,
        historical_data: Optional[pd.DataFrame] = None
    ) -> ImpactPrediction:
        """Predict the impact of an event on a financial metric"""
        # Analyze event description
        direction = self._calculate_impact_direction(event.description)
        magnitude = self._calculate_impact_magnitude(event.description)
        timeframe = self._calculate_timeframe(event.description)
        confidence = self._calculate_confidence(event.description, event)
        
        # Calculate impact score
        impact_score = direction * magnitude
        
        # Generate explanation
        explanation = self._generate_explanation(
            event,
            metric,
            direction,
            magnitude,
            timeframe
        )
        
        # Create prediction
        prediction = ImpactPrediction(
            event=event,
            metric=metric,
            impact_score=impact_score,
            confidence=confidence,
            timeframe=timeframe,
            explanation=explanation
        )
        
        return prediction
    
    def _generate_explanation(
        self,
        event: Event,
        metric: FinancialMetric,
        direction: float,
        magnitude: float,
        timeframe: str
    ) -> str:
        """Generate a human-readable explanation of the impact"""
        # Determine impact direction
        if direction > 0.3:
            direction_str = "positive"
        elif direction < -0.3:
            direction_str = "negative"
        else:
            direction_str = "neutral"
            
        # Determine impact magnitude
        if magnitude > 0.7:
            magnitude_str = "significant"
        elif magnitude > 0.3:
            magnitude_str = "moderate"
        else:
            magnitude_str = "minor"
            
        # Generate explanation
        explanation = (
            f"The {event.event_type.name.lower()} event '{event.title}' is expected to have a "
            f"{magnitude_str} {direction_str} impact on {metric.name.lower()}. "
            f"This impact is likely to manifest in the {timeframe.replace('_', ' ')}. "
            f"The prediction is based on the event's severity ({event.severity:.2f}) and "
            f"the presence of relevant keywords in the event description."
        )
        
        return explanation

def main():
    # Example usage
    predictor = ImpactPredictor()
    
    # Create example event
    event = Event(
        event_type=EventType.POLICY_CHANGE,
        title="RBI Announces Interest Rate Cut",
        description="The Reserve Bank of India has announced a 25 basis point cut in interest rates, which is expected to boost lending and stimulate economic growth.",
        source="RBI Press Release",
        date=datetime.now(),
        location="India",
        severity=0.8,
        confidence=0.9,
        raw_text="The Reserve Bank of India has announced a 25 basis point cut in interest rates..."
    )
    
    # Create example metric
    metric = FinancialMetric(
        name="Funding Availability",
        description="The ease with which startups can access funding",
        category="Funding"
    )
    
    # Predict impact
    prediction = predictor.predict_impact(event, metric)
    
    # Print prediction
    print(f"\nImpact Prediction for {metric.name}")
    print(f"Event: {event.title}")
    print(f"Impact Score: {prediction.impact_score:.2f}")
    print(f"Confidence: {prediction.confidence:.2f}")
    print(f"Timeframe: {prediction.timeframe}")
    print(f"Explanation: {prediction.explanation}")

if __name__ == "__main__":
    main() 