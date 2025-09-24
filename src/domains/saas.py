"""
SaaS Business Model Startups Domain.

This domain analyzes Software-as-a-Service startups,
focusing on recurring revenue, customer metrics, and unit economics.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from .base import BaseDomain, Event, Shock


class SaaSDomain(BaseDomain):
    """Domain for analyzing SaaS business model startups."""
    
    @property
    def key(self) -> str:
        return "saas"
    
    @property
    def name(self) -> str:
        return "SaaS Business Model"
    
    @property
    def description(self) -> str:
        return "Analysis of Software-as-a-Service startups, focusing on recurring revenue, customer metrics, and unit economics."
    
    def feature_spec(self) -> Dict[str, str]:
        return {
            "arr": "float - Annual Recurring Revenue",
            "ndr": "float - Net Dollar Retention rate (0-1)",
            "gross_churn": "float - Gross churn rate (0-1)",
            "net_churn": "float - Net churn rate (0-1)",
            "cac": "float - Customer Acquisition Cost",
            "ltv": "float - Lifetime Value per customer",
            "magic_number": "float - Sales efficiency metric",
            "sales_cycle_days": "int - Average sales cycle length",
            "gross_margin": "float - Gross margin percentage (0-1)",
            "payback_period_months": "int - CAC payback period",
            "expansion_rate": "float - Revenue expansion rate",
            "contract_value": "float - Average contract value",
            "customer_count": "int - Total number of customers",
            "enterprise_ratio": "float - Ratio of enterprise customers"
        }
    
    def extract_features(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract SaaS-specific features from input data."""
        features = {}
        
        # Revenue metrics
        features["arr"] = inputs.get("arr", 0.0)
        features["ndr"] = inputs.get("ndr", 0.9)
        features["gross_churn"] = inputs.get("gross_churn", 0.05)
        features["net_churn"] = inputs.get("net_churn", 0.02)
        
        # Unit economics
        features["cac"] = inputs.get("cac", 0.0)
        features["ltv"] = inputs.get("ltv", 0.0)
        features["magic_number"] = inputs.get("magic_number", 0.0)
        features["sales_cycle_days"] = inputs.get("sales_cycle_days", 90)
        features["gross_margin"] = inputs.get("gross_margin", 0.8)
        
        # Customer metrics
        features["payback_period_months"] = inputs.get("payback_period_months", 12)
        features["expansion_rate"] = inputs.get("expansion_rate", 0.15)
        features["contract_value"] = inputs.get("contract_value", 0.0)
        features["customer_count"] = inputs.get("customer_count", 0)
        features["enterprise_ratio"] = inputs.get("enterprise_ratio", 0.3)
        
        return features
    
    def risk_factors(self) -> List[str]:
        return [
            "competitor_mega_round",
            "cloud_price_changes",
            "market_saturation",
            "churn_spike",
            "sales_efficiency_decline",
            "enterprise_spending_cuts",
            "regulatory_changes",
            "economic_downturn"
        ]
    
    def map_events_to_shocks(self, events: List[Event]) -> List[Shock]:
        """Map events to SaaS-specific shocks."""
        shocks = []
        
        for event in events:
            if event.category in ["funding", "competition"]:
                shocks.append(Shock(
                    type="competitor_mega_round",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.6, abs(event.sentiment) * 0.6),
                    duration_days=90,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
            
            elif event.category in ["cloud_computing", "infrastructure"]:
                shocks.append(Shock(
                    type="cloud_price_changes",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.5, abs(event.sentiment) * 0.5),
                    duration_days=60,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
            
            elif event.category in ["market_saturation", "industry_consolidation"]:
                shocks.append(Shock(
                    type="market_saturation",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.7, abs(event.sentiment) * 0.7),
                    duration_days=180,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
        
        return shocks
    
    def simulate_response(self, features: Dict[str, Any], shocks: List[Shock]) -> Dict[str, float]:
        """Simulate SaaS response to shocks."""
        # Initialize base metrics
        arr_growth_delta = 0.0
        churn_delta = 0.0
        runway_change = 0.0
        
        # Apply shock effects
        for shock in shocks:
            if shock.type == "competitor_mega_round":
                # Competitor funding affects market dynamics
                arr_growth_delta -= shock.intensity * 0.15
                churn_delta += shock.intensity * 0.1
                runway_change -= shock.intensity * 2.0
            
            elif shock.type == "cloud_price_changes":
                # Cloud price changes affect margins
                arr_growth_delta -= shock.intensity * 0.05
                runway_change -= shock.intensity * 1.0
            
            elif shock.type == "market_saturation":
                # Market saturation affects growth
                arr_growth_delta -= shock.intensity * 0.2
                churn_delta += shock.intensity * 0.15
                runway_change -= shock.intensity * 3.0
        
        # Calculate derived metrics
        magic_number_delta = arr_growth_delta * 0.8
        cac_efficiency_risk = churn_delta * 1.2
        unit_econ_delta = arr_growth_delta - churn_delta
        
        return {
            "arr_growth_delta": max(-0.5, arr_growth_delta),  # Min -50%
            "churn_delta": min(0.3, churn_delta),  # Max +30%
            "runway_change": max(-12.0, runway_change),  # Min -12 months
            "magic_number_delta": max(-0.4, magic_number_delta),
            "cac_efficiency_risk": min(0.4, cac_efficiency_risk),
            "unit_econ_delta": max(-0.6, unit_econ_delta),
            "ndr_risk": churn_delta * 0.8
        }
    
    def reporting_metrics(self) -> List[str]:
        return [
            "arr_growth_delta",
            "churn_delta",
            "runway_change",
            "magic_number_delta",
            "cac_efficiency_risk",
            "unit_econ_delta",
            "ndr_risk"
        ]

