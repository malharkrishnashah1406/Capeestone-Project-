"""
GreenTech Startups Domain.

This domain analyzes green technology startups,
focusing on environmental policies, sustainability metrics, and carbon credits.
"""

from typing import Dict, List, Any
from .base import BaseDomain, Event, Shock


class GreenTechDomain(BaseDomain):
    """Domain for analyzing green technology startups."""
    
    @property
    def key(self) -> str:
        return "greentech"
    
    @property
    def name(self) -> str:
        return "GreenTech"
    
    @property
    def description(self) -> str:
        return "Analysis of green technology startups, focusing on environmental policies, sustainability metrics, and carbon credits."
    
    def feature_spec(self) -> Dict[str, str]:
        return {
            "carbon_footprint_reduction": "float - Carbon footprint reduction percentage",
            "sustainability_score": "float - Overall sustainability score (0-1)",
            "renewable_energy_usage": "float - Percentage of renewable energy used",
            "carbon_credits_earned": "int - Number of carbon credits earned",
            "environmental_certifications": "list - List of environmental certifications",
            "regulatory_compliance_score": "float - Environmental regulatory compliance (0-1)",
            "green_investment_ratio": "float - Ratio of green investments to total",
            "waste_reduction_percentage": "float - Waste reduction percentage",
            "energy_efficiency_rating": "float - Energy efficiency rating (0-1)",
            "climate_risk_exposure": "float - Exposure to climate risks (0-1)"
        }
    
    def extract_features(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract GreenTech-specific features from input data."""
        features = {}
        
        # Environmental metrics
        features["carbon_footprint_reduction"] = inputs.get("carbon_footprint_reduction", 0.0)
        features["sustainability_score"] = inputs.get("sustainability_score", 0.5)
        features["renewable_energy_usage"] = inputs.get("renewable_energy_usage", 0.0)
        features["carbon_credits_earned"] = inputs.get("carbon_credits_earned", 0)
        features["environmental_certifications"] = inputs.get("environmental_certifications", [])
        
        # Compliance metrics
        features["regulatory_compliance_score"] = inputs.get("regulatory_compliance_score", 0.7)
        features["green_investment_ratio"] = inputs.get("green_investment_ratio", 0.3)
        features["waste_reduction_percentage"] = inputs.get("waste_reduction_percentage", 0.0)
        features["energy_efficiency_rating"] = inputs.get("energy_efficiency_rating", 0.5)
        features["climate_risk_exposure"] = inputs.get("climate_risk_exposure", 0.4)
        
        return features
    
    def risk_factors(self) -> List[str]:
        return [
            "climate_policy_change",
            "carbon_pricing_changes",
            "renewable_energy_subsidy_cuts",
            "environmental_regulation_tightening",
            "climate_event_impact",
            "green_investment_downturn",
            "sustainability_standards_change",
            "carbon_market_volatility"
        ]
    
    def map_events_to_shocks(self, events: List[Event]) -> List[Shock]:
        """Map events to GreenTech-specific shocks."""
        shocks = []
        
        for event in events:
            if event.category in ["climate_policy", "environmental_regulation"]:
                shocks.append(Shock(
                    type="climate_policy_change",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.8, abs(event.sentiment) * 0.8),
                    duration_days=365,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
            
            elif event.category in ["carbon_pricing", "carbon_tax"]:
                shocks.append(Shock(
                    type="carbon_pricing_changes",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.7, abs(event.sentiment) * 0.7),
                    duration_days=180,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
        
        return shocks
    
    def simulate_response(self, features: Dict[str, Any], shocks: List[Shock]) -> Dict[str, float]:
        """Simulate GreenTech response to shocks."""
        # Initialize base metrics
        sustainability_impact = 0.0
        carbon_credit_value = 0.0
        regulatory_risk = 0.2
        market_demand = 0.5
        
        # Apply shock effects
        for shock in shocks:
            if shock.type == "climate_policy_change":
                sustainability_impact += shock.intensity * 0.3
                carbon_credit_value += shock.intensity * 0.2
                regulatory_risk += shock.intensity * 0.3
                market_demand += shock.intensity * 0.4
            
            elif shock.type == "carbon_pricing_changes":
                carbon_credit_value += shock.intensity * 0.4
                market_demand += shock.intensity * 0.2
                regulatory_risk += shock.intensity * 0.1
        
        # Calculate derived metrics
        green_premium = sustainability_impact * 0.6
        compliance_cost = regulatory_risk * 0.8
        market_opportunity = market_demand * 0.7
        
        return {
            "sustainability_impact": min(1.0, sustainability_impact),
            "carbon_credit_value": min(1.0, carbon_credit_value),
            "regulatory_risk": min(1.0, regulatory_risk),
            "market_demand": min(1.0, market_demand),
            "green_premium": min(1.0, green_premium),
            "compliance_cost": min(1.0, compliance_cost),
            "market_opportunity": min(1.0, market_opportunity)
        }
    
    def reporting_metrics(self) -> List[str]:
        return [
            "sustainability_impact",
            "carbon_credit_value",
            "regulatory_risk",
            "market_demand",
            "green_premium",
            "compliance_cost",
            "market_opportunity"
        ]