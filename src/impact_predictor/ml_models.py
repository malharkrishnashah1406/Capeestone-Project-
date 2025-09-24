import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from textblob import TextBlob
import emoji
import joblib
from typing import Dict, List, Tuple, Optional

class MLModels:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.model = LinearRegression()
        
    def analyze_sentiment_advanced(self, text: str) -> Dict:
        """Analyze sentiment using TextBlob and emoji analysis."""
        try:
            # Convert emojis to text for better sentiment analysis
            text = emoji.demojize(text)
            
            # Create TextBlob object
            blob = TextBlob(text)
            
            # Get polarity and subjectivity
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Calculate sentiment score (normalized to 0-10)
            sentiment_score = (polarity + 1) * 5
            
            # Calculate confidence based on subjectivity
            confidence = 1 - subjectivity
            
            return {
                'sentiment_score': sentiment_score,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'confidence': confidence
            }
        except Exception as e:
            print(f"Error in sentiment analysis: {str(e)}")
            return {
                'sentiment_score': 5.0,
                'polarity': 0.0,
                'subjectivity': 0.5,
                'confidence': 0.5
            }
            
    def predict_price(self, historical_data: pd.DataFrame, days: int = 30) -> Tuple[float, float]:
        """Predict future stock price using linear regression."""
        try:
            # Prepare data
            X = np.array(range(len(historical_data))).reshape(-1, 1)
            y = historical_data['Close'].values
            
            # Scale the data
            X_scaled = self.scaler.fit_transform(X)
            
            # Train the model
            self.model.fit(X_scaled, y)
            
            # Make prediction
            future_X = np.array(range(len(historical_data), len(historical_data) + days)).reshape(-1, 1)
            future_X_scaled = self.scaler.transform(future_X)
            prediction = self.model.predict(future_X_scaled)[-1]
            
            # Calculate confidence (R-squared score)
            confidence = self.model.score(X_scaled, y)
            
            return prediction, confidence
            
        except Exception as e:
            print(f"Error in price prediction: {str(e)}")
            return 0.0, 0.0
            
    def train_model(self, historical_data: pd.DataFrame) -> bool:
        """Train the price prediction model."""
        try:
            # Prepare data
            X = np.array(range(len(historical_data))).reshape(-1, 1)
            y = historical_data['Close'].values
            
            # Scale the data
            X_scaled = self.scaler.fit_transform(X)
            
            # Train the model
            self.model.fit(X_scaled, y)
            
            return True
            
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return False
            
    def save_model(self, path: str) -> bool:
        """Save the trained model to disk."""
        try:
            model_data = {
                'scaler': self.scaler,
                'model': self.model
            }
            joblib.dump(model_data, path)
            return True
        except Exception as e:
            print(f"Error saving model: {str(e)}")
            return False
            
    def load_model(self, path: str) -> bool:
        """Load a trained model from disk."""
        try:
            model_data = joblib.load(path)
            self.scaler = model_data['scaler']
            self.model = model_data['model']
            return True
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False 