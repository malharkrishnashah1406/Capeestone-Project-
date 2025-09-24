"""
HealthTech/Biotech Startups Domain.

This domain analyzes health technology and biotechnology startups,
focusing on regulatory compliance, clinical trials, and healthcare metrics.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from .base import BaseDomain, Event, Shock


class HealthTechBiotechDomain(BaseDomain):
    """Domain for analyzing health technology and biotechnology startups."""
    
    @property
    def key(self) -> str:
        return "healthtech_biotech"
    
    @property
    def name(self) -> str:
        return "HealthTech/Biotech"
    
    @property
    def description(self) -> str:
        return "Analysis of health technology and biotechnology startups, focusing on regulatory compliance, clinical trials, and healthcare metrics."
    
    def feature_spec(self) -> Dict[str, str]:
        return {
            "fda_approval_status": "str - FDA approval status",
            "clinical_trial_phase": "int - Current clinical trial phase (0-4)",
            "regulatory_burden_index": "float - Regulatory compliance burden (0-1)",
            "rd_investment": "float - R&D investment amount",
            "patent_count": "int - Number of patents held",
            "fda_audit_frequency": "int - Number of FDA audits per year",
            "patient_population_size": "int - Target patient population size",
            "reimbursement_status": "str - Insurance reimbursement status",
            "clinical_trial_success_rate": "float - Historical trial success rate (0-1)",
            "regulatory_timeline_days": "int - Average regulatory approval timeline",
            "market_access_barriers": "float - Market access difficulty (0-1)",
            "competitor_count": "int - Number of direct competitors"
        }
    
    def extract_features(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract HealthTech/Biotech-specific features from input data."""
        features = {}
        
        # Regulatory metrics
        features["fda_approval_status"] = inputs.get("fda_approval_status", "pending")
        features["clinical_trial_phase"] = inputs.get("clinical_trial_phase", 1)
        features["regulatory_burden_index"] = inputs.get("regulatory_burden_index", 0.7)
        features["fda_audit_frequency"] = inputs.get("fda_audit_frequency", 1)
        features["regulatory_timeline_days"] = inputs.get("regulatory_timeline_days", 365)
        
        # R&D metrics
        features["rd_investment"] = inputs.get("rd_investment", 0.0)
        features["patent_count"] = inputs.get("patent_count", 0)
        features["clinical_trial_success_rate"] = inputs.get("clinical_trial_success_rate", 0.3)
        
        # Market metrics
        features["patient_population_size"] = inputs.get("patient_population_size", 1000000)
        features["reimbursement_status"] = inputs.get("reimbursement_status", "pending")
        features["market_access_barriers"] = inputs.get("market_access_barriers", 0.6)
        features["competitor_count"] = inputs.get("competitor_count", 5)
        
        return features
    
    def risk_factors(self) -> List[str]:
        return [
            "fda_rejection",
            "clinical_trial_failure",
            "regulatory_delay",
            "reimbursement_denial",
            "competitor_breakthrough",
            "safety_concerns",
            "patent_expiry",
            "market_access_restrictions"
        ]
    
    def map_events_to_shocks(self, events: List[Event]) -> List[Shock]:
        """Map events to HealthTech/Biotech-specific shocks."""
        shocks = []
        
        for event in events:
            if event.category in ["regulation", "fda"]:
                shocks.append(Shock(
                    type="fda_rejection",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.9, abs(event.sentiment) * 0.9),
                    duration_days=180,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
            
            elif event.category in ["clinical_trial", "research"]:
                shocks.append(Shock(
                    type="clinical_trial_failure",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.8, abs(event.sentiment) * 0.8),
                    duration_days=365,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
            
            elif event.category in ["competition", "breakthrough"]:
                shocks.append(Shock(
                    type="competitor_breakthrough",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.7, abs(event.sentiment) * 0.7),
                    duration_days=90,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
        
        return shocks
    
    def simulate_response(self, features: Dict[str, Any], shocks: List[Shock]) -> Dict[str, float]:
        """Simulate HealthTech/Biotech response to shocks."""
        # Initialize base metrics
        approval_probability = 0.3
        trial_success_rate = features.get("clinical_trial_success_rate", 0.3)
        market_access_risk = 0.2
        revenue_impact = 0.0
        
        # Apply shock effects
        for shock in shocks:
            if shock.type == "fda_rejection":
                approval_probability -= shock.intensity * 0.5
                market_access_risk += shock.intensity * 0.3
                revenue_impact -= shock.intensity * 0.4
            
            elif shock.type == "clinical_trial_failure":
                trial_success_rate -= shock.intensity * 0.3
                approval_probability -= shock.intensity * 0.2
                revenue_impact -= shock.intensity * 0.3
            
            elif shock.type == "competitor_breakthrough":
                market_access_risk += shock.intensity * 0.2
                revenue_impact -= shock.intensity * 0.2
        
        # Calculate derived metrics
        regulatory_risk = (1 - approval_probability) * 0.8
        trial_risk = (1 - trial_success_rate) * 0.6
        market_penetration_risk = market_access_risk * 0.7
        
        return {
            "approval_probability": max(0.0, min(1.0, approval_probability)),
            "trial_success_rate": max(0.0, min(1.0, trial_success_rate)),
            "market_access_risk": min(1.0, market_access_risk),
            "revenue_impact": max(-0.8, revenue_impact),
            "regulatory_risk": min(1.0, regulatory_risk),
            "trial_risk": min(1.0, trial_risk),
            "market_penetration_risk": min(1.0, market_penetration_risk)
        }
    
    def reporting_metrics(self) -> List[str]:
        return [
            "approval_probability",
            "trial_success_rate",
            "market_access_risk",
            "revenue_impact",
            "regulatory_risk",
            "trial_risk",
            "market_penetration_risk"
        ]