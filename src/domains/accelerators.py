"""
Startup Accelerators / Incubators Domain.

This domain analyzes startup accelerators and incubators,
focusing on cohort performance, mentor effectiveness, and program outcomes.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from .base import BaseDomain, Event, Shock


class AcceleratorsDomain(BaseDomain):
    """Domain for analyzing startup accelerators and incubators."""
    
    @property
    def key(self) -> str:
        return "accelerators"
    
    @property
    def name(self) -> str:
        return "Startup Accelerators / Incubators"
    
    @property
    def description(self) -> str:
        return "Analysis of startup accelerators and incubators, including cohort performance, mentor effectiveness, and program outcomes."
    
    def feature_spec(self) -> Dict[str, str]:
        return {
            "runway_months_cohort": "float - Average runway in months for cohort companies",
            "mentor_density": "float - Number of mentors per startup",
            "acceptance_quality_score": "float - Quality score of accepted startups (0-1)",
            "follow_on_funding_rate": "float - Rate of companies receiving follow-on funding",
            "visa_dependency_ratio": "float - Ratio of companies dependent on visas",
            "cohort_size": "int - Number of companies in current cohort",
            "program_duration_weeks": "int - Duration of accelerator program in weeks",
            "equity_taken": "float - Average equity taken by accelerator",
            "demo_day_attendance": "int - Number of investors at demo day",
            "alumni_network_size": "int - Size of alumni network",
            "industry_focus": "dict - Industry focus areas and distribution",
            "geographic_reach": "dict - Geographic distribution of companies"
        }
    
    def extract_features(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract accelerator-specific features from input data."""
        features = {}
        
        # Program metrics
        features["runway_months_cohort"] = inputs.get("runway_months_cohort", 6.0)
        features["mentor_density"] = inputs.get("mentor_density", 5.0)
        features["acceptance_quality_score"] = inputs.get("acceptance_quality_score", 0.7)
        features["follow_on_funding_rate"] = inputs.get("follow_on_funding_rate", 0.6)
        features["visa_dependency_ratio"] = inputs.get("visa_dependency_ratio", 0.3)
        
        # Program structure
        features["cohort_size"] = inputs.get("cohort_size", 20)
        features["program_duration_weeks"] = inputs.get("program_duration_weeks", 12)
        features["equity_taken"] = inputs.get("equity_taken", 0.06)
        
        # Network metrics
        features["demo_day_attendance"] = inputs.get("demo_day_attendance", 100)
        features["alumni_network_size"] = inputs.get("alumni_network_size", 500)
        
        # Focus areas
        features["industry_focus"] = inputs.get("industry_focus", {})
        features["geographic_reach"] = inputs.get("geographic_reach", {})
        
        return features
    
    def risk_factors(self) -> List[str]:
        return [
            "macro_tightening",
            "visa_delays",
            "grant_cuts",
            "mentor_attrition",
            "investor_pullback",
            "program_quality_decline",
            "geopolitical_risks",
            "market_saturation"
        ]
    
    def map_events_to_shocks(self, events: List[Event]) -> List[Shock]:
        """Map events to accelerator-specific shocks."""
        shocks = []
        
        for event in events:
            if event.category in ["rate_hike", "monetary_policy"]:
                shocks.append(Shock(
                    type="macro_tightening",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.7, abs(event.sentiment) * 0.7),
                    duration_days=180,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
            
            elif event.category in ["immigration", "visa_policy"]:
                shocks.append(Shock(
                    type="visa_delays",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.8, abs(event.sentiment) * 0.8),
                    duration_days=120,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
            
            elif event.category in ["funding_cuts", "budget_reduction"]:
                shocks.append(Shock(
                    type="grant_cuts",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.6, abs(event.sentiment) * 0.6),
                    duration_days=90,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
        
        return shocks
    
    def simulate_response(self, features: Dict[str, Any], shocks: List[Shock]) -> Dict[str, float]:
        """Simulate accelerator response to shocks."""
        # Initialize base metrics
        cohort_survival_12m = 0.7  # Base 12-month survival rate
        median_follow_on = 0.5  # Base median follow-on rate
        burn_extension_months = 0.0
        
        # Apply shock effects
        for shock in shocks:
            if shock.type == "macro_tightening":
                # Macro tightening affects funding and survival
                cohort_survival_12m -= shock.intensity * 0.2
                median_follow_on -= shock.intensity * 0.15
                burn_extension_months += shock.intensity * 2.0
            
            elif shock.type == "visa_delays":
                # Visa delays affect international companies
                cohort_survival_12m -= shock.intensity * 0.1
                median_follow_on -= shock.intensity * 0.1
                burn_extension_months += shock.intensity * 1.5
            
            elif shock.type == "grant_cuts":
                # Grant cuts affect accelerator funding
                cohort_survival_12m -= shock.intensity * 0.15
                median_follow_on -= shock.intensity * 0.1
                burn_extension_months += shock.intensity * 1.0
        
        # Calculate derived metrics
        mentor_effectiveness = max(0.3, 1 - burn_extension_months / 12)
        program_quality_risk = 1 - cohort_survival_12m
        funding_pipeline_risk = 1 - median_follow_on
        
        return {
            "cohort_survival_12m": max(0.2, cohort_survival_12m),  # Min 20%
            "median_follow_on": max(0.1, median_follow_on),  # Min 10%
            "burn_extension_months": min(12.0, burn_extension_months),  # Max 12 months
            "mentor_effectiveness": max(0.1, mentor_effectiveness),
            "program_quality_risk": min(0.8, program_quality_risk),
            "funding_pipeline_risk": min(0.9, funding_pipeline_risk),
            "cohort_attrition_risk": 1 - cohort_survival_12m
        }
    
    def reporting_metrics(self) -> List[str]:
        return [
            "cohort_survival_12m",
            "median_follow_on",
            "burn_extension_months",
            "mentor_effectiveness",
            "program_quality_risk",
            "funding_pipeline_risk",
            "cohort_attrition_risk"
        ]

