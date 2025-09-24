"""
Public Sector Funded Startups Domain.

This domain analyzes startups that receive public sector funding,
focusing on government contracts, grants, and public-private partnerships.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from .base import BaseDomain, Event, Shock


class PublicSectorFundedDomain(BaseDomain):
    """Domain for analyzing public sector funded startups."""
    
    @property
    def key(self) -> str:
        return "public_sector_funded"
    
    @property
    def name(self) -> str:
        return "Public Sector Funded Startups"
    
    @property
    def description(self) -> str:
        return "Analysis of startups that receive public sector funding, focusing on government contracts, grants, and public-private partnerships."
    
    def feature_spec(self) -> Dict[str, str]:
        return {
            "government_contracts": "int - Number of active government contracts",
            "grant_funding_ratio": "float - Ratio of grant funding to total funding",
            "compliance_score": "float - Regulatory compliance score (0-1)",
            "public_sector_revenue_share": "float - Share of revenue from public sector (0-1)",
            "contract_duration_months": "float - Average contract duration in months",
            "bidding_success_rate": "float - Success rate in government bidding (0-1)",
            "regulatory_risk_score": "float - Regulatory risk score (0-1)",
            "political_risk_score": "float - Political risk score (0-1)",
            "audit_frequency": "float - Frequency of government audits per year",
            "subsidy_dependency": "float - Dependency on government subsidies (0-1)",
            "procurement_cycle_length": "int - Average procurement cycle length in days",
            "public_sector_relationships": "dict - Key government relationships and contacts"
        }
    
    def extract_features(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract public sector funded startup features from input data."""
        features = {}
        
        # Contract and funding metrics
        features["government_contracts"] = inputs.get("government_contracts", 0)
        features["grant_funding_ratio"] = inputs.get("grant_funding_ratio", 0.3)
        features["public_sector_revenue_share"] = inputs.get("public_sector_revenue_share", 0.4)
        features["contract_duration_months"] = inputs.get("contract_duration_months", 24.0)
        
        # Performance metrics
        features["bidding_success_rate"] = inputs.get("bidding_success_rate", 0.6)
        features["compliance_score"] = inputs.get("compliance_score", 0.8)
        
        # Risk metrics
        features["regulatory_risk_score"] = inputs.get("regulatory_risk_score", 0.3)
        features["political_risk_score"] = inputs.get("political_risk_score", 0.4)
        features["audit_frequency"] = inputs.get("audit_frequency", 2.0)
        features["subsidy_dependency"] = inputs.get("subsidy_dependency", 0.2)
        
        # Process metrics
        features["procurement_cycle_length"] = inputs.get("procurement_cycle_length", 180)
        features["public_sector_relationships"] = inputs.get("public_sector_relationships", {})
        
        return features
    
    def risk_factors(self) -> List[str]:
        return [
            "budget_cuts",
            "policy_changes",
            "regulatory_increases",
            "political_instability",
            "audit_findings",
            "contract_termination",
            "compliance_violations",
            "public_scrutiny"
        ]
    
    def map_events_to_shocks(self, events: List[Event]) -> List[Shock]:
        """Map events to public sector funded startup shocks."""
        shocks = []
        
        for event in events:
            if event.category in ["budget_cuts", "fiscal_policy"]:
                shocks.append(Shock(
                    type="budget_cuts",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.8, abs(event.sentiment) * 0.8),
                    duration_days=365,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
            
            elif event.category in ["regulation", "policy_change"]:
                shocks.append(Shock(
                    type="regulatory_increases",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.7, abs(event.sentiment) * 0.7),
                    duration_days=180,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
            
            elif event.category in ["political_instability", "election"]:
                shocks.append(Shock(
                    type="political_instability",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.6, abs(event.sentiment) * 0.6),
                    duration_days=120,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
        
        return shocks
    
    def simulate_response(self, features: Dict[str, Any], shocks: List[Shock]) -> Dict[str, float]:
        """Simulate public sector funded startup response to shocks."""
        # Initialize base metrics
        contract_renewal_rate = 0.8
        revenue_stability = 0.7
        compliance_risk = 0.2
        
        # Apply shock effects
        for shock in shocks:
            if shock.type == "budget_cuts":
                # Budget cuts affect contract renewals and revenue
                contract_renewal_rate -= shock.intensity * 0.3
                revenue_stability -= shock.intensity * 0.4
                compliance_risk += shock.intensity * 0.1
            
            elif shock.type == "regulatory_increases":
                # Regulatory increases affect compliance and costs
                compliance_risk += shock.intensity * 0.2
                revenue_stability -= shock.intensity * 0.1
            
            elif shock.type == "political_instability":
                # Political instability affects all metrics
                contract_renewal_rate -= shock.intensity * 0.2
                revenue_stability -= shock.intensity * 0.3
                compliance_risk += shock.intensity * 0.15
        
        # Calculate derived metrics
        funding_risk = 1 - contract_renewal_rate
        operational_risk = (1 - revenue_stability) + compliance_risk
        political_risk = 1 - contract_renewal_rate
        
        return {
            "contract_renewal_rate": max(0.2, contract_renewal_rate),  # Min 20%
            "revenue_stability": max(0.1, revenue_stability),  # Min 10%
            "compliance_risk": min(0.8, compliance_risk),  # Max 80%
            "funding_risk": min(0.9, funding_risk),
            "operational_risk": min(0.9, operational_risk),
            "political_risk": min(0.8, political_risk),
            "audit_risk": compliance_risk * 1.2
        }
    
    def reporting_metrics(self) -> List[str]:
        return [
            "contract_renewal_rate",
            "revenue_stability",
            "compliance_risk",
            "funding_risk",
            "operational_risk",
            "political_risk",
            "audit_risk"
        ]