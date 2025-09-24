import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import requests
from io import BytesIO
import base64

class MarketAnalyzer:
    def __init__(self):
        self.stock_data = {}
        self.sector_data = {}
        self.risk_metrics = {}
        self.model_path = Path("models/market_predictor.joblib")
        self._load_or_create_model()

    def _load_or_create_model(self):
        """Load existing model or create a new one if it doesn't exist."""
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
        else:
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model_path.parent.mkdir(exist_ok=True)

    def get_stock_data(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """Fetch stock data for a given ticker."""
        if ticker not in self.stock_data:
            try:
                stock = yf.Ticker(ticker)
                self.stock_data[ticker] = stock.history(period=period)
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
                return pd.DataFrame()
        return self.stock_data[ticker]

    def analyze_market_correlation(self, company: str, ticker: str) -> Dict:
        """Analyze correlation between news sentiment and stock performance."""
        try:
            # Get stock data
            stock_data = self.get_stock_data(ticker)
            if stock_data.empty:
                return {"error": "No stock data available"}

            # Calculate daily returns
            stock_data['Returns'] = stock_data['Close'].pct_change()
            
            # Get sentiment data (assuming it's stored in a database)
            # This would need to be integrated with your database
            sentiment_data = self._get_sentiment_data(company)
            
            # Calculate correlation
            correlation = np.corrcoef(stock_data['Returns'].dropna(), 
                                    sentiment_data['sentiment'].dropna())[0,1]
            
            return {
                "correlation": correlation,
                "stock_volatility": stock_data['Returns'].std(),
                "sentiment_volatility": sentiment_data['sentiment'].std(),
                "analysis_period": len(stock_data)
            }
        except Exception as e:
            return {"error": str(e)}

    def generate_market_visualization(self, ticker: str) -> str:
        """Generate interactive market visualization using Plotly."""
        try:
            stock_data = self.get_stock_data(ticker)
            if stock_data.empty:
                return ""

            # Create subplot figure
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                              vertical_spacing=0.03, subplot_titles=('Price', 'Volume'),
                              row_heights=[0.7, 0.3])

            # Add candlestick chart
            fig.add_trace(go.Candlestick(x=stock_data.index,
                                        open=stock_data['Open'],
                                        high=stock_data['High'],
                                        low=stock_data['Low'],
                                        close=stock_data['Close'],
                                        name='Price'),
                         row=1, col=1)

            # Add volume bar chart
            fig.add_trace(go.Bar(x=stock_data.index,
                                y=stock_data['Volume'],
                                name='Volume'),
                         row=2, col=1)

            # Update layout
            fig.update_layout(
                title=f'{ticker} Stock Price and Volume',
                yaxis_title='Price',
                yaxis2_title='Volume',
                xaxis_rangeslider_visible=False
            )

            # Convert to HTML
            return fig.to_html(full_html=False)
        except Exception as e:
            print(f"Error generating visualization: {e}")
            return ""

    def calculate_risk_metrics(self, ticker: str) -> Dict:
        """Calculate various risk metrics for a stock."""
        try:
            stock_data = self.get_stock_data(ticker)
            if stock_data.empty:
                return {"error": "No stock data available"}

            returns = stock_data['Close'].pct_change().dropna()
            
            metrics = {
                "volatility": returns.std() * np.sqrt(252),  # Annualized volatility
                "sharpe_ratio": (returns.mean() * 252) / (returns.std() * np.sqrt(252)),
                "max_drawdown": (stock_data['Close'] / stock_data['Close'].cummax() - 1).min(),
                "var_95": np.percentile(returns, 5),  # 95% Value at Risk
                "beta": self._calculate_beta(ticker)  # Market beta
            }
            
            self.risk_metrics[ticker] = metrics
            return metrics
        except Exception as e:
            return {"error": str(e)}

    def _calculate_beta(self, ticker: str) -> float:
        """Calculate beta coefficient against market (S&P 500)."""
        try:
            stock_data = self.get_stock_data(ticker)
            market_data = self.get_stock_data("^GSPC")  # S&P 500
            
            # Calculate returns
            stock_returns = stock_data['Close'].pct_change().dropna()
            market_returns = market_data['Close'].pct_change().dropna()
            
            # Calculate beta
            covariance = np.cov(stock_returns, market_returns)[0][1]
            market_variance = np.var(market_returns)
            
            return covariance / market_variance
        except Exception as e:
            print(f"Error calculating beta: {e}")
            return 0.0

    def generate_risk_report(self, ticker: str) -> str:
        """Generate a comprehensive risk report."""
        try:
            metrics = self.calculate_risk_metrics(ticker)
            if "error" in metrics:
                return metrics["error"]

            # Create visualization
            fig = make_subplots(rows=2, cols=2,
                              subplot_titles=('Volatility', 'Sharpe Ratio',
                                            'Maximum Drawdown', 'Value at Risk'))

            # Add metrics to subplots
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=metrics["volatility"] * 100,
                title={'text': "Volatility (%)"},
                gauge={'axis': {'range': [0, 100]}},
            ), row=1, col=1)

            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=metrics["sharpe_ratio"],
                title={'text': "Sharpe Ratio"},
                gauge={'axis': {'range': [-2, 2]}},
            ), row=1, col=2)

            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=metrics["max_drawdown"] * 100,
                title={'text': "Max Drawdown (%)"},
                gauge={'axis': {'range': [-100, 0]}},
            ), row=2, col=1)

            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=metrics["var_95"] * 100,
                title={'text': "VaR 95% (%)"},
                gauge={'axis': {'range': [-20, 0]}},
            ), row=2, col=2)

            fig.update_layout(height=600, showlegend=False)
            return fig.to_html(full_html=False)
        except Exception as e:
            return f"Error generating risk report: {str(e)}"

    def export_analysis(self, ticker: str, format: str = "pdf") -> bytes:
        """Export analysis results in various formats."""
        try:
            # Generate all necessary data
            stock_data = self.get_stock_data(ticker)
            risk_metrics = self.calculate_risk_metrics(ticker)
            market_correlation = self.analyze_market_correlation(ticker, ticker)
            
            if format.lower() == "pdf":
                # Create PDF report
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
                from reportlab.lib.styles import getSampleStyleSheet
                
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                styles = getSampleStyleSheet()
                elements = []
                
                # Add title
                elements.append(Paragraph(f"Analysis Report for {ticker}", styles['Title']))
                
                # Add risk metrics table
                data = [[k, str(v)] for k, v in risk_metrics.items()]
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(table)
                
                # Build PDF
                doc.build(elements)
                return buffer.getvalue()
                
            elif format.lower() == "json":
                # Export as JSON
                data = {
                    "ticker": ticker,
                    "risk_metrics": risk_metrics,
                    "market_correlation": market_correlation,
                    "last_updated": datetime.now().isoformat()
                }
                return json.dumps(data, indent=2).encode()
                
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            print(f"Error exporting analysis: {e}")
            return b""

    def predict_market_trend(self, ticker: str) -> Dict:
        """Predict market trend using machine learning model."""
        try:
            stock_data = self.get_stock_data(ticker)
            if stock_data.empty:
                return {"error": "No stock data available"}

            # Prepare features
            features = self._prepare_features(stock_data)
            
            # Make prediction
            prediction = self.model.predict(features)
            
            return {
                "predicted_trend": "up" if prediction[-1] > 0 else "down",
                "confidence": abs(prediction[-1]),
                "features_importance": dict(zip(features.columns, 
                                             self.model.feature_importances_))
            }
        except Exception as e:
            return {"error": str(e)}

    def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for machine learning model."""
        # Calculate technical indicators
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['RSI'] = self._calculate_rsi(data['Close'])
        data['MACD'] = self._calculate_macd(data['Close'])
        
        # Drop NaN values
        data = data.dropna()
        
        # Select features
        features = data[['SMA_20', 'SMA_50', 'RSI', 'MACD', 'Volume']]
        
        return features

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

    def _get_sentiment_data(self, company: str) -> pd.DataFrame:
        """Get sentiment data for a company (to be implemented with your database)."""
        # This is a placeholder - implement with your actual database
        return pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=100),
            'sentiment': np.random.normal(0, 1, 100)
        }) 