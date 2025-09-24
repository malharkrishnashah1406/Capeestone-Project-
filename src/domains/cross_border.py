"""
Cross-Border Startups Domain.

This domain analyzes cross-border startups,
focusing on international expansion, trade dependencies, and geopolitical risks.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from .base import BaseDomain, Event, Shock


class CrossBorderDomain(BaseDomain):
    """Domain for analyzing cross-border startups."""
    
    @property
    def key(self) -> str:
        return "cross_border"
    
    @property
    def name(self) -> str:
        return "Cross-Border Startups"
    
    @property
    def description(self) -> str:
        return "Analysis of cross-border startups, focusing on international expansion, trade dependencies, and geopolitical risks."
    
    def feature_spec(self) -> Dict[str, str]:
        return {
            "fx_exposure": "float - Foreign exchange exposure percentage",
            "trade_dependence_ratio": "float - Dependence on international trade (0-1)",
            "cross_border_talent_ratio": "float - Ratio of international talent",
            "logistics_lead_time": "int - Average logistics lead time in days",
            "sanction_sensitivity": "float - Sensitivity to sanctions (0-1)",
            "market_count": "int - Number of international markets",
            "localization_cost_ratio": "float - Cost of localization as ratio of revenue",
            "regulatory_compliance_countries": "int - Number of countries with regulatory compliance",
            "currency_volatility_exposure": "float - Exposure to currency volatility",
            "supply_chain_complexity": "float - Supply chain complexity index (0-1)",
            "political_risk_score": "float - Political risk score (0-1)",
            "trade_agreement_coverage": "float - Coverage of trade agreements (0-1)",
            "international_partnership_count": "int - Number of international partnerships"
        }
    
    def extract_features(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Cross-Border-specific features from input data."""
        features = {}
        
        # Financial exposure metrics
        features["fx_exposure"] = inputs.get("fx_exposure", 0.3)
        features["currency_volatility_exposure"] = inputs.get("currency_volatility_exposure", 0.2)
        features["trade_dependence_ratio"] = inputs.get("trade_dependence_ratio", 0.4)
        
        # Operational metrics
        features["cross_border_talent_ratio"] = inputs.get("cross_border_talent_ratio", 0.3)
        features["logistics_lead_time"] = inputs.get("logistics_lead_time", 30)
        features["supply_chain_complexity"] = inputs.get("supply_chain_complexity", 0.5)
        
        # Market and compliance metrics
        features["market_count"] = inputs.get("market_count", 3)
        features["regulatory_compliance_countries"] = inputs.get("regulatory_compliance_countries", 2)
        features["international_partnership_count"] = inputs.get("international_partnership_count", 5)
        
        # Risk metrics
        features["sanction_sensitivity"] = inputs.get("sanction_sensitivity", 0.2)
        features["political_risk_score"] = inputs.get("political_risk_score", 0.3)
        features["trade_agreement_coverage"] = inputs.get("trade_agreement_coverage", 0.6)
        
        # Cost metrics
        features["localization_cost_ratio"] = inputs.get("localization_cost_ratio", 0.15)
        
        return features
    
    def risk_factors(self) -> List[str]:
        return [
            "tariff_changes",
            "sanctions",
            "immigration_rules",
            "currency_volatility",
            "trade_war",
            "political_instability",
            "supply_chain_disruption",
            "regulatory_divergence"
        ]
    
    def map_events_to_shocks(self, events: List[Event]) -> List[Shock]:
        """Map events to Cross-Border-specific shocks."""
        shocks = []
        
        for event in events:
            if event.category in ["tariff", "trade_policy"]:
                shocks.append(Shock(
                    type="tariff_changes",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.8, abs(event.sentiment) * 0.8),
                    duration_days=180,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
            
            elif event.category in ["sanctions", "embargo"]:
                shocks.append(Shock(
                    type="sanctions",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.9, abs(event.sentiment) * 0.9),
                    duration_days=365,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
            
            elif event.category in ["immigration", "visa_policy"]:
                shocks.append(Shock(
                    type="immigration_rules",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.7, abs(event.sentiment) * 0.7),
                    duration_days=120,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
        
        return shocks
    
    def simulate_response(self, features: Dict[str, Any], shocks: List[Shock]) -> Dict[str, float]:
        """Simulate Cross-Border response to shocks."""
        # Initialize base metrics
        gross_margin_delta = 0.0
        lead_time_delta = 0.0
        revenue_at_risk = 0.0
        
        # Apply shock effects
        for shock in shocks:
            if shock.type == "tariff_changes":
                # Tariff changes affect costs and margins
                gross_margin_delta -= shock.intensity * 0.15
                lead_time_delta += shock.intensity * 5.0  # Days
                revenue_at_risk += shock.intensity * 0.1
            
            elif shock.type == "sanctions":
                # Sanctions can severely impact operations
                gross_margin_delta -= shock.intensity * 0.3
                lead_time_delta += shock.intensity * 15.0
                revenue_at_risk += shock.intensity * 0.4
            
            elif shock.type == "immigration_rules":
                # Immigration rules affect talent availability
                gross_margin_delta -= shock.intensity * 0.05
                lead_time_delta += shock.intensity * 2.0
                revenue_at_risk += shock.intensity * 0.05
        
        # Calculate derived metrics
        supply_chain_risk = lead_time_delta / 30.0  # Normalize to monthly
        currency_risk = gross_margin_delta * 0.8
        geopolitical_risk = revenue_at_risk * 1.2
        
        return {
            "gross_margin_delta": max(-0.5, gross_margin_delta),  # Min -50%
            "lead_time_delta": min(30.0, lead_time_delta),  # Max 30 days
            "revenue_at_risk": min(0.6, revenue_at_risk),  # Max 60%
            "supply_chain_risk": min(1.0, supply_chain_risk),
            "currency_risk": min(0.4, currency_risk),
            "geopolitical_risk": min(0.8, geopolitical_risk),
            "operational_risk": (supply_chain_risk + currency_risk) * 0.5
        }
    
    def reporting_metrics(self) -> List[str]:
        return [
            "gross_margin_delta",
            "lead_time_delta",
            "revenue_at_risk",
            "supply_chain_risk",
            "currency_risk",
            "geopolitical_risk",
            "operational_risk"
        ]




