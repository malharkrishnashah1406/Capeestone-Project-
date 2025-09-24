import os
from typing import Dict, Any, List
from .data_collection.news_collector import NewsCollector
from .event_detection.event_classifier import EventClassifier
from .modeling.financial_predictor import FinancialPredictor
from .visualization.dashboard import StartupDashboard
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

class StartupPredictionSystem:
    def __init__(self):
        self.news_collector = NewsCollector()
        self.event_classifier = EventClassifier()
        self.financial_predictor = FinancialPredictor()
        self.dashboard = StartupDashboard()

    def collect_data(self, startup_name: str) -> Dict[str, Any]:
        """
        Collect all necessary data for a startup
        """
        # Collect news articles
        startup_news = self.news_collector.collect_startup_news(startup_name)
        industry_news = self.news_collector.collect_industry_news(
            ["startup", "venture capital", "tech industry"]
        )
        government_releases = self.news_collector.collect_government_releases()
        global_events = self.news_collector.collect_global_events()

        # Combine all news
        all_news = (
            startup_news +
            industry_news +
            government_releases +
            global_events
        )

        return {
            "startup_name": startup_name,
            "news_articles": all_news
        }

    def process_events(self, news_articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process news articles to extract and classify events
        """
        # Process articles in batches
        processed_articles = self.event_classifier.process_batch(news_articles)

        # Add impact scores to events
        for article in processed_articles:
            article["impact_score"] = self.event_classifier.get_event_impact(article)

        return processed_articles

    def predict_financials(self, startup_data: Dict[str, Any], events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Make financial predictions based on events
        """
        return self.financial_predictor.predict_financials(startup_data, events)

    def run(self, startup_name: str):
        """
        Run the complete prediction system
        """
        # Collect data
        st.info("Collecting data...")
        startup_data = self.collect_data(startup_name)

        # Process events
        st.info("Processing events...")
        events = self.process_events(startup_data["news_articles"])

        # Make predictions
        st.info("Making predictions...")
        predictions = self.predict_financials(startup_data, events)

        # Store results in session state
        st.session_state.startup_data = startup_data
        st.session_state.events = events
        st.session_state.predictions = predictions

        # Run dashboard
        self.dashboard.run()

def main():
    st.title("Startup Performance Prediction System")
    
    # Initialize system
    system = StartupPredictionSystem()
    
    # Get startup name input
    startup_name = st.text_input(
        "Enter Startup Name",
        placeholder="e.g., Paytm, Zomato, Ola"
    )
    
    if startup_name:
        try:
            system.run(startup_name)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 