from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class EventType(Enum):
    """Types of events that can impact startups"""
    POLICY_CHANGE = "policy_change"
    MARKET_SHIFT = "market_shift"
    REGULATORY_UPDATE = "regulatory_update"
    COMPETITOR_ACTION = "competitor_action"
    TECHNOLOGY_TREND = "technology_trend"
    ECONOMIC_INDICATOR = "economic_indicator"
    INDUSTRY_NEWS = "industry_news"
    FUNDING_ANNOUNCEMENT = "funding_announcement"
    PARTNERSHIP = "partnership"
    PRODUCT_LAUNCH = "product_launch"

@dataclass
class FinancialMetric:
    """Represents a financial metric that can be impacted by events"""
    name: str
    description: str
    category: str

@dataclass
class Event:
    """Represents an event that can impact startups"""
    event_type: EventType
    title: str
    description: str
    source: str
    date: datetime
    location: str
    severity: float  # 0 to 1
    confidence: float  # 0 to 1
    raw_text: str

@dataclass
class ImpactPrediction:
    """Represents a prediction of how an event will impact a financial metric"""
    event: Event
    metric: FinancialMetric
    impact_score: float  # -1 to 1
    confidence: float  # 0 to 1
    timeframe: str  # short_term, medium_term, long_term
    explanation: str 