"""
Shock Generator Module.

This module generates exogenous shocks for scenario analysis,
including policy changes, rate changes, market events, etc.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)


@dataclass
class Shock:
    """Represents an exogenous shock."""
    type: str
    jurisdiction: str
    intensity: float  # 0.0 to 1.0
    duration_days: int
    start_date: datetime
    confidence: float  # 0.0 to 1.0
    source_refs: List[str]
    description: str = ""


class ShockGenerator:
    """Generates exogenous shocks for scenario analysis."""
    
    def __init__(self):
        self.shock_types = {
            'policy_rate_change': {
                'description': 'Central bank policy rate change',
                'intensity_range': (0.3, 0.8),
                'duration_range': (30, 180),
                'jurisdictions': ['US', 'EU', 'UK', 'JP', 'CA']
            },
            'regulatory_change': {
                'description': 'New regulatory requirements or changes',
                'intensity_range': (0.4, 0.9),
                'duration_range': (60, 365),
                'jurisdictions': ['US', 'EU', 'UK', 'CA']
            },
            'market_crash': {
                'description': 'Significant market downturn',
                'intensity_range': (0.6, 1.0),
                'duration_range': (30, 90),
                'jurisdictions': ['US', 'EU', 'UK', 'JP', 'CA']
            },
            'trade_war': {
                'description': 'Trade tensions and tariffs',
                'intensity_range': (0.5, 0.9),
                'duration_range': (90, 365),
                'jurisdictions': ['US', 'CN', 'EU', 'JP']
            },
            'pandemic': {
                'description': 'Public health emergency',
                'intensity_range': (0.7, 1.0),
                'duration_range': (180, 730),
                'jurisdictions': ['US', 'EU', 'UK', 'JP', 'CA', 'CN']
            },
            'cybersecurity_breach': {
                'description': 'Major cybersecurity incident',
                'intensity_range': (0.4, 0.8),
                'duration_range': (30, 120),
                'jurisdictions': ['US', 'EU', 'UK', 'JP', 'CA']
            },
            'climate_event': {
                'description': 'Extreme weather or climate event',
                'intensity_range': (0.3, 0.7),
                'duration_range': (7, 60),
                'jurisdictions': ['US', 'EU', 'UK', 'JP', 'CA', 'CN']
            },
            'political_instability': {
                'description': 'Political uncertainty or instability',
                'intensity_range': (0.4, 0.8),
                'duration_range': (30, 180),
                'jurisdictions': ['US', 'EU', 'UK', 'JP', 'CA']
            }
        }
    
    def generate_random_shock(self, shock_type: Optional[str] = None, 
                            jurisdiction: Optional[str] = None) -> Shock:
        """
        Generate a random shock.
        
        Args:
            shock_type: Specific shock type to generate
            jurisdiction: Specific jurisdiction for the shock
            
        Returns:
            Generated shock
        """
        # Select shock type
        if shock_type is None:
            shock_type = random.choice(list(self.shock_types.keys()))
        
        if shock_type not in self.shock_types:
            raise ValueError(f"Unknown shock type: {shock_type}")
        
        shock_config = self.shock_types[shock_type]
        
        # Select jurisdiction
        if jurisdiction is None:
            jurisdiction = random.choice(shock_config['jurisdictions'])
        
        # Generate random parameters
        intensity = random.uniform(*shock_config['intensity_range'])
        duration_days = random.randint(*shock_config['duration_range'])
        confidence = random.uniform(0.6, 0.9)
        
        # Generate start date (within next 30 days)
        start_date = datetime.now() + timedelta(days=random.randint(0, 30))
        
        # Generate source references
        source_refs = [f"Generated shock: {shock_type}"]
        
        return Shock(
            type=shock_type,
            jurisdiction=jurisdiction,
            intensity=intensity,
            duration_days=duration_days,
            start_date=start_date,
            confidence=confidence,
            source_refs=source_refs,
            description=shock_config['description']
        )
    
    def generate_shock_sequence(self, num_shocks: int, 
                              shock_types: Optional[List[str]] = None,
                              jurisdictions: Optional[List[str]] = None) -> List[Shock]:
        """
        Generate a sequence of shocks.
        
        Args:
            num_shocks: Number of shocks to generate
            shock_types: List of allowed shock types
            jurisdictions: List of allowed jurisdictions
            
        Returns:
            List of generated shocks
        """
        shocks = []
        
        for _ in range(num_shocks):
            # Select shock type from allowed types
            shock_type = None
            if shock_types:
                shock_type = random.choice(shock_types)
            
            # Select jurisdiction from allowed jurisdictions
            jurisdiction = None
            if jurisdictions:
                jurisdiction = random.choice(jurisdictions)
            
            shock = self.generate_random_shock(shock_type, jurisdiction)
            shocks.append(shock)
        
        return shocks
    
    def generate_scenario_shocks(self, scenario_name: str) -> List[Shock]:
        """
        Generate shocks for predefined scenarios.
        
        Args:
            scenario_name: Name of the scenario
            
        Returns:
            List of shocks for the scenario
        """
        scenarios = {
            'recession': [
                ('policy_rate_change', 'US', 0.8, 180),
                ('market_crash', 'US', 0.9, 90),
                ('political_instability', 'US', 0.6, 120)
            ],
            'tech_regulation': [
                ('regulatory_change', 'US', 0.7, 365),
                ('regulatory_change', 'EU', 0.6, 365),
                ('cybersecurity_breach', 'US', 0.5, 60)
            ],
            'trade_conflict': [
                ('trade_war', 'US', 0.8, 365),
                ('trade_war', 'CN', 0.7, 365),
                ('political_instability', 'US', 0.5, 180)
            ],
            'climate_crisis': [
                ('climate_event', 'US', 0.6, 90),
                ('climate_event', 'EU', 0.5, 90),
                ('regulatory_change', 'US', 0.6, 180)
            ],
            'pandemic_response': [
                ('pandemic', 'US', 0.8, 365),
                ('pandemic', 'EU', 0.7, 365),
                ('policy_rate_change', 'US', 0.5, 90)
            ]
        }
        
        if scenario_name not in scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        shocks = []
        scenario_config = scenarios[scenario_name]
        
        for shock_type, jurisdiction, intensity, duration in scenario_config:
            start_date = datetime.now() + timedelta(days=random.randint(0, 30))
            
            shock = Shock(
                type=shock_type,
                jurisdiction=jurisdiction,
                intensity=intensity,
                duration_days=duration,
                start_date=start_date,
                confidence=random.uniform(0.7, 0.9),
                source_refs=[f"Scenario: {scenario_name}"],
                description=self.shock_types[shock_type]['description']
            )
            shocks.append(shock)
        
        return shocks
    
    def generate_correlated_shocks(self, primary_shock: Shock, 
                                 correlation_probability: float = 0.3) -> List[Shock]:
        """
        Generate correlated shocks based on a primary shock.
        
        Args:
            primary_shock: Primary shock to base correlations on
            correlation_probability: Probability of generating correlated shocks
            
        Returns:
            List of correlated shocks
        """
        correlated_shocks = []
        
        # Define correlation patterns
        correlations = {
            'policy_rate_change': ['market_crash', 'political_instability'],
            'regulatory_change': ['cybersecurity_breach', 'political_instability'],
            'market_crash': ['policy_rate_change', 'political_instability'],
            'trade_war': ['political_instability', 'market_crash'],
            'pandemic': ['policy_rate_change', 'market_crash'],
            'cybersecurity_breach': ['regulatory_change', 'political_instability'],
            'climate_event': ['regulatory_change', 'political_instability'],
            'political_instability': ['market_crash', 'policy_rate_change']
        }
        
        if primary_shock.type in correlations:
            correlated_types = correlations[primary_shock.type]
            
            for correlated_type in correlated_types:
                if random.random() < correlation_probability:
                    # Generate correlated shock with similar timing
                    correlated_shock = Shock(
                        type=correlated_type,
                        jurisdiction=primary_shock.jurisdiction,
                        intensity=primary_shock.intensity * random.uniform(0.5, 1.0),
                        duration_days=primary_shock.duration_days * random.uniform(0.5, 1.5),
                        start_date=primary_shock.start_date + timedelta(days=random.randint(-7, 14)),
                        confidence=primary_shock.confidence * random.uniform(0.8, 1.0),
                        source_refs=[f"Correlated to: {primary_shock.type}"],
                        description=self.shock_types[correlated_type]['description']
                    )
                    correlated_shocks.append(correlated_shock)
        
        return correlated_shocks
    
    def validate_shock(self, shock: Shock) -> bool:
        """
        Validate a shock.
        
        Args:
            shock: Shock to validate
            
        Returns:
            True if valid, False otherwise
        """
        if shock.type not in self.shock_types:
            return False
        
        if shock.intensity < 0.0 or shock.intensity > 1.0:
            return False
        
        if shock.duration_days < 1:
            return False
        
        if shock.confidence < 0.0 or shock.confidence > 1.0:
            return False
        
        shock_config = self.shock_types[shock.type]
        if shock.jurisdiction not in shock_config['jurisdictions']:
            return False
        
        return True
    
    def get_shock_statistics(self, shocks: List[Shock]) -> Dict[str, Any]:
        """
        Get statistics about a list of shocks.
        
        Args:
            shocks: List of shocks
            
        Returns:
            Dictionary with shock statistics
        """
        if not shocks:
            return {
                'total_shocks': 0,
                'by_type': {},
                'by_jurisdiction': {},
                'avg_intensity': 0.0,
                'avg_duration': 0.0,
                'avg_confidence': 0.0
            }
        
        stats = {
            'total_shocks': len(shocks),
            'by_type': {},
            'by_jurisdiction': {},
            'avg_intensity': sum(s.intensity for s in shocks) / len(shocks),
            'avg_duration': sum(s.duration_days for s in shocks) / len(shocks),
            'avg_confidence': sum(s.confidence for s in shocks) / len(shocks)
        }
        
        # Count by type
        for shock in shocks:
            if shock.type not in stats['by_type']:
                stats['by_type'][shock.type] = 0
            stats['by_type'][shock.type] += 1
        
        # Count by jurisdiction
        for shock in shocks:
            if shock.jurisdiction not in stats['by_jurisdiction']:
                stats['by_jurisdiction'][shock.jurisdiction] = 0
            stats['by_jurisdiction'][shock.jurisdiction] += 1
        
        return stats























