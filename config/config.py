import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Data Collection Settings
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "3a028cb39f384ca48b335ad35aad974d")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "49f8f6053f9edaf0cbbb8f5b0e341646")

# Database Configuration
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),  # PostgreSQL default port
    "database": os.getenv("DB_NAME", "news_analyzer"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "malhar1234")
}

# Web Scraping Settings
SCRAPING_CONFIG = {
    "rate_limit": 2,  # seconds between requests
    "max_retries": 3,
    "timeout": 30,  # seconds
    "user_agent_rotation": True
}

# News Sources
NEWS_SOURCES = {
    "government": [
        "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx",
        # Add more government news sources here
    ],
    "startup": [
        "https://inc42.com/",
        # Add more startup news sources here
    ],
    "financial": [
        "https://www.moneycontrol.com/news/",
        # Add more financial news sources here
    ]
}

# Event Categories
EVENT_CATEGORIES = [
    "Wars",
    "Market Crash",
    "Pandemic",
    "Global Events",
    "Government Policies",
    "Technological Disruptions",
    "Global Trade Relations",
    "Monetary Policy Shifts",
    "Global Supply Chain disruptions",
    "Inflation/Deflation",
    "Consumer Behaviour",
    "Social Moments",
    "Cold wars / Social Conflicts",
    "Venture Capital Boom",
    "Merger or Acquisitions",
    "Talent Migration",
    "Infrastructure Development",
    "Innovation, Grant and R & D Support",
    "Funding of Any rival company",
    "Increase / Decrease in Consumer Spending",
    "Access to Global Talent",
    "IPO and Public Marker access"
]

# Financial Parameters
FINANCIAL_PARAMETERS = [
    "Total Revenue",
    "Revenue Growth Rate (%)",
    "Net Profit / Loss",
    "EBITDA",
    "Gross Profit Margin (%)",
    "Operating Profit Margin (%)",
    "Net Profit Margin (%)",
    "Free Cash Flow (FCF)",
    "Burn Rate",
    "Break-even Point",
    "Total Funding Raised",
    "Number of Funding Rounds",
    "Valuation",
    "Investor Concentration Risk",
    "Venture Capital Dependency (%)",
    "Equity Dilution (%)",
    "Convertible Debt",
    "IPO Status",
    "Stock Price Growth",
    "Mergers & Acquisitions (M&A) Activity",
    "Market Share (%)",
    "Customer Acquisition Cost (CAC)",
    "Lifetime Value (LTV) per Customer",
    "LTV/CAC Ratio",
    "Churn Rate (%)",
    "Revenue Per User (ARPU)",
    "Active User Growth (%)",
    "Brand Sentiment Score",
    "Competitor Funding & Valuation Trends",
    "Subscription Renewal Rate (%)",
    "R&D Expenditure (% of revenue)",
    "Technology Adoption Rate (%)",
    "Talent Migration",
    "Geographical Expansion Rate (%)",
    "ESG Compliance Score",
    "Infrastructure Development Investment",
    "Patents & Intellectual Property Owned",
    "Supply Chain Efficiency Score",
    "Customer Satisfaction Index",
    "Regulatory & Compliance Risks",
    "Inflation Impact on Business Costs",
    "Interest Rate Impact on Loans & Investments",
    "Global Trade Relations Impact",
    "Effect of Pandemics/Epidemics on Demand",
    "Venture Capital Boom or Funding Slowdown",
    "Stock Market Crash Impact on Investments",
    "Government Policy Shifts Affecting Industry",
    "Major Technological Disruptions in Industry",
    "Rival Company's Big Funding / IPO Impact",
    "Global Conflict / War Impact on Operations"
]

# Model Settings
MODEL_CONFIG = {
    "event_classification": {
        "model_name": "bert-base-uncased",
        "max_length": 512,
        "batch_size": 16,
        "learning_rate": 2e-5
    },
    "financial_prediction": {
        "model_name": "xgboost",
        "n_estimators": 100,
        "max_depth": 6,
        "learning_rate": 0.1
    },
    "sentiment_analysis": {
        "model_name": "ProsusAI/finbert",
        "max_length": 512,
        "batch_size": 16
    }
}

# API Settings
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": True
}

# Data Collection Settings
DATA_COLLECTION_CONFIG = {
    "news_sources": NEWS_SOURCES,
    "update_frequency": "1h",  # How often to collect new data
    "historical_data_days": 365  # How many days of historical data to collect
}

# Visualization Settings
VISUALIZATION_CONFIG = {
    "theme": "streamlit",
    "update_frequency": "5m",
    "max_data_points": 1000
}

# Event extraction configuration
EVENT_EXTRACTION = {
    "min_confidence": 0.7,
    "max_events_per_article": 5,
    "event_types": [
        "funding",
        "acquisition",
        "partnership",
        "product_launch",
        "regulatory_change",
        "market_trend"
    ]
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/app.log"
} 