import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import yfinance as yf
from bs4 import BeautifulSoup
import tweepy
from textblob import TextBlob
import json
from pathlib import Path
import os

class DataSources:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self._setup_apis()
        
    def _load_config(self) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _setup_apis(self):
        """Setup API clients."""
        # Twitter API setup
        if 'twitter' in self.config:
            auth = tweepy.OAuthHandler(
                self.config['twitter']['api_key'],
                self.config['twitter']['api_secret']
            )
            auth.set_access_token(
                self.config['twitter']['access_token'],
                self.config['twitter']['access_token_secret']
            )
            self.twitter_api = tweepy.API(auth)
        else:
            self.twitter_api = None
            
        # News API setup
        self.news_api_key = self.config.get('news_api', {}).get('api_key')
        
    def get_news_articles(self, company: str, days: int = 7) -> List[Dict]:
        """Get news articles from various sources."""
        articles = []
        
        # Get news from News API
        if self.news_api_key:
            try:
                url = f"https://newsapi.org/v2/everything"
                params = {
                    'q': company,
                    'from': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                    'sortBy': 'publishedAt',
                    'apiKey': self.news_api_key
                }
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    news_data = response.json()
                    articles.extend(news_data.get('articles', []))
            except Exception as e:
                print(f"Error fetching news: {str(e)}")
        
        # Get news from Yahoo Finance
        try:
            stock = yf.Ticker(company)
            news = stock.news
            articles.extend(news)
        except Exception as e:
            print(f"Error fetching Yahoo Finance news: {str(e)}")
            
        return articles
    
    def get_social_media_sentiment(self, company: str, days: int = 7) -> Dict:
        """Get social media sentiment analysis."""
        sentiment_data = {
            'twitter': [],
            'overall_sentiment': 0,
            'sentiment_count': 0
        }
        
        if self.twitter_api:
            try:
                # Search tweets
                tweets = self.twitter_api.search_tweets(
                    q=company,
                    lang="en",
                    count=100,
                    tweet_mode="extended"
                )
                
                # Analyze sentiment
                for tweet in tweets:
                    analysis = TextBlob(tweet.full_text)
                    sentiment_data['twitter'].append({
                        'text': tweet.full_text,
                        'sentiment': analysis.sentiment.polarity,
                        'date': tweet.created_at
                    })
                    sentiment_data['overall_sentiment'] += analysis.sentiment.polarity
                    sentiment_data['sentiment_count'] += 1
                
                if sentiment_data['sentiment_count'] > 0:
                    sentiment_data['overall_sentiment'] /= sentiment_data['sentiment_count']
                    
            except Exception as e:
                print(f"Error fetching Twitter data: {str(e)}")
                
        return sentiment_data
    
    def get_sec_filings(self, ticker: str) -> List[Dict]:
        """Get SEC filings data."""
        filings = []
        try:
            stock = yf.Ticker(ticker)
            # Get recent SEC filings
            if hasattr(stock, 'get_sec_filings'):
                filings = stock.get_sec_filings()
        except Exception as e:
            print(f"Error fetching SEC filings: {str(e)}")
        return filings
    
    def get_earnings_calls(self, ticker: str) -> List[Dict]:
        """Get earnings call transcripts."""
        calls = []
        try:
            stock = yf.Ticker(ticker)
            # Get earnings call transcripts
            if hasattr(stock, 'get_earnings_call_transcripts'):
                calls = stock.get_earnings_call_transcripts()
        except Exception as e:
            print(f"Error fetching earnings calls: {str(e)}")
        return calls
    
    def get_market_data(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """Get comprehensive market data."""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            
            # Add technical indicators
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            data['RSI'] = self._calculate_rsi(data['Close'])
            data['MACD'] = self._calculate_macd(data['Close'])
            
            return data
        except Exception as e:
            print(f"Error fetching market data: {str(e)}")
            return pd.DataFrame()
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, prices: pd.Series) -> pd.Series:
        """Calculate Moving Average Convergence Divergence."""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        return exp1 - exp2
    
    def get_company_info(self, ticker: str) -> Dict:
        """Get comprehensive company information."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Add additional data
            info['sector'] = info.get('sector', '')
            info['industry'] = info.get('industry', '')
            info['market_cap'] = info.get('marketCap', 0)
            info['pe_ratio'] = info.get('trailingPE', 0)
            info['dividend_yield'] = info.get('dividendYield', 0)
            
            return info
        except Exception as e:
            print(f"Error fetching company info: {str(e)}")
            return {} 