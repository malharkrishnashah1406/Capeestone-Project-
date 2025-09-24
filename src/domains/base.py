"""
Base domain interface and shared functionality for startup analysis domains.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Protocol
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class Shock:
    """Represents an exogenous shock that can impact startup performance."""
    type: str
    jurisdiction: str
    intensity: float  # 0.0 to 1.0
    duration_days: int
    start_date: datetime
    confidence: float  # 0.0 to 1.0
    source_refs: List[str]


@dataclass
class Event:
    """Represents an event that can be mapped to shocks."""
    category: str
    title: str
    description: str
    date: datetime
    jurisdiction: str
    sentiment: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0


class BaseDomain(ABC):
    """
    Abstract base class for domain-specific analysis.
    
    Each domain implements specific feature extraction, risk assessment,
    and simulation capabilities for different types of startups.
    """
    
    @property
    @abstractmethod
    def key(self) -> str:
        """Unique identifier for this domain."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this domain."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of this domain and its characteristics."""
        pass
    
    @abstractmethod
    def feature_spec(self) -> Dict[str, str]:
        """
        Return feature specification for this domain.
        
        Returns:
            Dict mapping feature names to their data types and descriptions.
        """
        pass
    
    @abstractmethod
    def extract_features(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract domain-specific features from input data.
        
        Args:
            inputs: Raw input data (startup metrics, financial data, etc.)
            
        Returns:
            Dict of extracted features
        """
        pass
    
    @abstractmethod
    def risk_factors(self) -> List[str]:
        """
        Return list of key risk factors for this domain.
        
        Returns:
            List of risk factor names
        """
        pass
    
    @abstractmethod
    def map_events_to_shocks(self, events: List[Event]) -> List[Shock]:
        """
        Map events to domain-specific shocks.
        
        Args:
            events: List of events to analyze
            
        Returns:
            List of shocks that would impact this domain
        """
        pass
    
    @abstractmethod
    def simulate_response(self, features: Dict[str, Any], shocks: List[Shock]) -> Dict[str, float]:
        """
        Simulate domain response to shocks.
        
        Args:
            features: Current domain features
            shocks: List of shocks to simulate
            
        Returns:
            Dict of simulated outcomes and metrics
        """
        pass
    
    @abstractmethod
    def reporting_metrics(self) -> List[str]:
        """
        Return list of key metrics for reporting and monitoring.
        
        Returns:
            List of metric names
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert domain to dictionary representation."""
        return {
            'key': self.key,
            'name': self.name,
            'description': self.description,
            'feature_spec': self.feature_spec(),
            'risk_factors': self.risk_factors(),
            'reporting_metrics': self.reporting_metrics()
        }


class DomainRegistry:
    """Registry for managing domain implementations."""
    
    def __init__(self):
        self._domains: Dict[str, BaseDomain] = {}
    
    def register(self, domain: BaseDomain) -> None:
        """Register a domain implementation."""
        self._domains[domain.key] = domain
    
    def get(self, key: str) -> BaseDomain:
        """Get a domain by key."""
        if key not in self._domains:
            raise KeyError(f"Domain '{key}' not found. Available: {list(self._domains.keys())}")
        return self._domains[key]
    
    def list_all(self) -> List[BaseDomain]:
        """List all registered domains."""
        return list(self._domains.values())
    
    def list_keys(self) -> List[str]:
        """List all registered domain keys."""
        return list(self._domains.keys())


# Global registry instance
registry = DomainRegistry()

