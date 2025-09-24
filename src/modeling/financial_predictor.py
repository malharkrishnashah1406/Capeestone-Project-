"""
Financial Predictor Module.

This module provides financial prediction capabilities for startups.
"""

from typing import Dict, List, Any, Optional
import logging
import random
# import numpy as np  # Commented out for compatibility
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FinancialPredictor:
    """Predicts financial performance for startups."""
    
    def __init__(self):
        self.models = {
            'xgboost': self._xgboost_predict,
            'lightgbm': self._lightgbm_predict,
            'prophet': self._prophet_predict,
            'neural_network': self._neural_network_predict
        }
    
    def predict_financials(self, startup_data: Dict[str, Any], events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict financial performance based on startup data and events.
        
        Args:
            startup_data: Startup information and historical data
            events: List of events that may impact performance
            
        Returns:
            Financial predictions
        """
        try:
            # Extract features
            features = self._extract_features(startup_data, events)
            
            # Generate predictions using ensemble of models
            predictions = {}
            
            for model_name, model_func in self.models.items():
                try:
                    model_predictions = model_func(features)
                    predictions[model_name] = model_predictions
                except Exception as e:
                    logger.warning(f"Model {model_name} failed: {e}")
                    predictions[model_name] = self._default_predictions()
            
            # Combine predictions using ensemble
            ensemble_predictions = self._ensemble_predictions(predictions)
            
            # Add metadata
            ensemble_predictions['prediction_date'] = datetime.now().isoformat()
            ensemble_predictions['model_versions'] = list(self.models.keys())
            ensemble_predictions['confidence'] = self._calculate_confidence(predictions)
            
            return ensemble_predictions
            
        except Exception as e:
            logger.error(f"Error predicting financials: {e}")
            return self._default_predictions()
    
    def _extract_features(self, startup_data: Dict[str, Any], events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract features for prediction."""
        features = {}
        
        # Basic startup features
        features['startup_name'] = startup_data.get('startup_name', 'unknown')
        features['industry'] = startup_data.get('industry', 'technology')
        features['stage'] = startup_data.get('stage', 'early')
        features['founding_year'] = startup_data.get('founding_year', 2020)
        
        # Financial features
        features['revenue'] = startup_data.get('revenue', 0.0)
        features['profit'] = startup_data.get('profit', 0.0)
        features['valuation'] = startup_data.get('valuation', 0.0)
        features['funding_raised'] = startup_data.get('funding_raised', 0.0)
        features['employees'] = startup_data.get('employees', 0)
        
        # Event features
        features['num_events'] = len(events)
        features['avg_event_sentiment'] = sum(e.get('sentiment', 0.0) for e in events) / len(events) if events else 0.0
        features['avg_event_impact'] = sum(e.get('impact_score', 0.0) for e in events) / len(events) if events else 0.0
        
        # Event category counts
        event_categories = [e.get('event_category', 'unknown') for e in events]
        for category in ['funding', 'acquisition', 'regulation', 'market_crash', 'technology']:
            features[f'events_{category}'] = event_categories.count(category)
        
        return features
    
    def _xgboost_predict(self, features: Dict[str, Any]) -> Dict[str, float]:
        """XGBoost model prediction (mock implementation)."""
        # Mock XGBoost prediction
        base_revenue = features.get('revenue', 1000000)
        base_profit = features.get('profit', 100000)
        base_valuation = features.get('valuation', 10000000)
        
        # Apply some random variation
        revenue_growth = random.uniform(0.8, 1.3)
        profit_growth = random.uniform(0.7, 1.4)
        valuation_growth = random.uniform(0.9, 1.2)
        
        return {
            'revenue': base_revenue * revenue_growth,
            'profit': base_profit * profit_growth,
            'valuation': base_valuation * valuation_growth,
            'market_share': random.uniform(0.01, 0.1),
            'customer_acquisition_cost': random.uniform(50, 500),
            'funding_availability': random.uniform(0.3, 0.9),
            'operating_expenses': base_revenue * random.uniform(0.6, 0.9),
            'employee_retention': random.uniform(0.7, 0.95)
        }
    
    def _lightgbm_predict(self, features: Dict[str, Any]) -> Dict[str, float]:
        """LightGBM model prediction (mock implementation)."""
        # Mock LightGBM prediction
        base_revenue = features.get('revenue', 1000000)
        base_profit = features.get('profit', 100000)
        base_valuation = features.get('valuation', 10000000)
        
        # Apply some random variation
        revenue_growth = random.uniform(0.85, 1.25)
        profit_growth = random.uniform(0.75, 1.35)
        valuation_growth = random.uniform(0.95, 1.15)
        
        return {
            'revenue': base_revenue * revenue_growth,
            'profit': base_profit * profit_growth,
            'valuation': base_valuation * valuation_growth,
            'market_share': random.uniform(0.02, 0.12),
            'customer_acquisition_cost': random.uniform(45, 480),
            'funding_availability': random.uniform(0.35, 0.85),
            'operating_expenses': base_revenue * random.uniform(0.65, 0.85),
            'employee_retention': random.uniform(0.72, 0.92)
        }
    
    def _prophet_predict(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Prophet model prediction (mock implementation)."""
        # Mock Prophet prediction
        base_revenue = features.get('revenue', 1000000)
        base_profit = features.get('profit', 100000)
        base_valuation = features.get('valuation', 10000000)
        
        # Apply some random variation
        revenue_growth = random.uniform(0.9, 1.2)
        profit_growth = random.uniform(0.8, 1.3)
        valuation_growth = random.uniform(0.95, 1.1)
        
        return {
            'revenue': base_revenue * revenue_growth,
            'profit': base_profit * profit_growth,
            'valuation': base_valuation * valuation_growth,
            'market_share': random.uniform(0.015, 0.08),
            'customer_acquisition_cost': random.uniform(55, 520),
            'funding_availability': random.uniform(0.4, 0.8),
            'operating_expenses': base_revenue * random.uniform(0.7, 0.8),
            'employee_retention': random.uniform(0.75, 0.9)
        }
    
    def _neural_network_predict(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Neural network model prediction (mock implementation)."""
        # Mock Neural Network prediction
        base_revenue = features.get('revenue', 1000000)
        base_profit = features.get('profit', 100000)
        base_valuation = features.get('valuation', 10000000)
        
        # Apply some random variation
        revenue_growth = random.uniform(0.88, 1.28)
        profit_growth = random.uniform(0.78, 1.38)
        valuation_growth = random.uniform(0.92, 1.18)
        
        return {
            'revenue': base_revenue * revenue_growth,
            'profit': base_profit * profit_growth,
            'valuation': base_valuation * valuation_growth,
            'market_share': random.uniform(0.018, 0.09),
            'customer_acquisition_cost': random.uniform(48, 490),
            'funding_availability': random.uniform(0.38, 0.82),
            'operating_expenses': base_revenue * random.uniform(0.68, 0.82),
            'employee_retention': random.uniform(0.73, 0.91)
        }
    
    def _ensemble_predictions(self, predictions: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Combine predictions from multiple models."""
        if not predictions:
            return self._default_predictions()
        
        # Get all metric names
        all_metrics = set()
        for model_preds in predictions.values():
            all_metrics.update(model_preds.keys())
        
        ensemble = {}
        
        for metric in all_metrics:
            values = []
            for model_preds in predictions.values():
                if metric in model_preds:
                    values.append(model_preds[metric])
            
            if values:
                # Use mean as ensemble method
                ensemble[metric] = sum(values) / len(values)
            else:
                ensemble[metric] = 0.0
        
        return ensemble
    
    def _calculate_confidence(self, predictions: Dict[str, Dict[str, float]]) -> float:
        """Calculate confidence score for predictions."""
        if not predictions:
            return 0.0
        
        # Calculate variance across models for each metric
        all_metrics = set()
        for model_preds in predictions.values():
            all_metrics.update(model_preds.keys())
        
        total_variance = 0.0
        metric_count = 0
        
        for metric in all_metrics:
            values = []
            for model_preds in predictions.values():
                if metric in model_preds:
                    values.append(model_preds[metric])
            
            if len(values) > 1:
                mean_val = sum(values) / len(values)
                variance = sum((x - mean_val) ** 2 for x in values) / len(values)
                total_variance += variance
                metric_count += 1
        
        if metric_count == 0:
            return 0.5
        
        avg_variance = total_variance / metric_count
        
        # Convert variance to confidence (lower variance = higher confidence)
        confidence = max(0.1, 1.0 - min(1.0, avg_variance / 1000000))
        
        return confidence
    
    def _default_predictions(self) -> Dict[str, float]:
        """Return default predictions when models fail."""
        return {
            'revenue': 1000000.0,
            'profit': 100000.0,
            'valuation': 10000000.0,
            'market_share': 0.05,
            'customer_acquisition_cost': 200.0,
            'funding_availability': 0.6,
            'operating_expenses': 800000.0,
            'employee_retention': 0.8,
            'prediction_date': datetime.now().isoformat(),
            'model_versions': ['default'],
            'confidence': 0.3
        }