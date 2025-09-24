"""
FinTech Startups Domain.

This domain analyzes financial technology startups,
focusing on regulatory compliance, fraud prevention, and financial metrics.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from .base import BaseDomain, Event, Shock


class FinTechDomain(BaseDomain):
    """Domain for analyzing financial technology startups."""
    
    @property
    def key(self) -> str:
        return "fintech"
    
    @property
    def name(self) -> str:
        return "Financial Technology (FinTech)"
    
    @property
    def description(self) -> str:
        return "Analysis of financial technology startups, focusing on regulatory compliance, fraud prevention, and financial metrics."
    
    def feature_spec(self) -> Dict[str, str]:
        return {
            "regulatory_burden_index": "float - Regulatory compliance burden (0-1)",
            "fraud_rate": "float - Fraud rate as percentage of transactions",
            "kyc_cost_per_user": "float - KYC compliance cost per user",
            "interchange_yield": "float - Interchange fee yield percentage",
            "interest_sensitivity": "float - Sensitivity to interest rate changes",
            "capital_ratio_proxy": "float - Proxy for capital adequacy ratio",
            "transaction_volume": "float - Monthly transaction volume",
            "user_acquisition_cost": "float - Cost to acquire new users",
            "regulatory_licenses": "list - List of regulatory licenses held",
            "compliance_automation_level": "float - Level of compliance automation (0-1)",
            "fraud_detection_accuracy": "float - Fraud detection accuracy (0-1)",
            "customer_trust_score": "float - Customer trust and satisfaction score",
            "regulatory_audit_frequency": "int - Number of regulatory audits per year"
        }
    
    def extract_features(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract FinTech-specific features from input data."""
        features = {}
        
        # Regulatory metrics
        features["regulatory_burden_index"] = inputs.get("regulatory_burden_index", 0.5)
        features["kyc_cost_per_user"] = inputs.get("kyc_cost_per_user", 5.0)
        features["regulatory_licenses"] = inputs.get("regulatory_licenses", [])
        features["compliance_automation_level"] = inputs.get("compliance_automation_level", 0.6)
        features["regulatory_audit_frequency"] = inputs.get("regulatory_audit_frequency", 2)
        
        # Financial metrics
        features["fraud_rate"] = inputs.get("fraud_rate", 0.01)
        features["interchange_yield"] = inputs.get("interchange_yield", 0.025)
        features["interest_sensitivity"] = inputs.get("interest_sensitivity", 0.3)
        features["capital_ratio_proxy"] = inputs.get("capital_ratio_proxy", 0.15)
        
        # Business metrics
        features["transaction_volume"] = inputs.get("transaction_volume", 0.0)
        features["user_acquisition_cost"] = inputs.get("user_acquisition_cost", 50.0)
        features["fraud_detection_accuracy"] = inputs.get("fraud_detection_accuracy", 0.95)
        features["customer_trust_score"] = inputs.get("customer_trust_score", 0.8)
        
        return features
    
    def risk_factors(self) -> List[str]:
        return [
            "policy_rate_change",
            "aml_crackdowns",
            "open_banking_updates",
            "regulatory_changes",
            "fraud_spike",
            "cybersecurity_breach",
            "customer_trust_loss",
            "capital_requirements_change"
        ]
    
    def map_events_to_shocks(self, events: List[Event]) -> List[Shock]:
        """Map events to FinTech-specific shocks."""
        shocks = []
        
        for event in events:
            if event.category in ["rate_hike", "monetary_policy"]:
                shocks.append(Shock(
                    type="policy_rate_change",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.8, abs(event.sentiment) * 0.8),
                    duration_days=180,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
            
            elif event.category in ["regulation", "compliance"]:
                shocks.append(Shock(
                    type="regulatory_changes",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.9, abs(event.sentiment) * 0.9),
                    duration_days=120,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
            
            elif event.category in ["fraud", "cybersecurity"]:
                shocks.append(Shock(
                    type="fraud_spike",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.7, abs(event.sentiment) * 0.7),
                    duration_days=90,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
        
        return shocks
    
    def simulate_response(self, features: Dict[str, Any], shocks: List[Shock]) -> Dict[str, float]:
        """Simulate FinTech response to shocks."""
        # Initialize base metrics
        tpv_growth_delta = 0.0
        loss_rate_delta = 0.0
        unit_econ_delta = 0.0
        
        # Apply shock effects
        for shock in shocks:
            if shock.type == "policy_rate_change":
                # Interest rate changes affect lending and deposits
                tpv_growth_delta -= shock.intensity * 0.1
                loss_rate_delta += shock.intensity * 0.05
                unit_econ_delta -= shock.intensity * 0.08
            
            elif shock.type == "regulatory_changes":
                # Regulatory changes affect compliance costs
                tpv_growth_delta -= shock.intensity * 0.05
                unit_econ_delta -= shock.intensity * 0.12
            
            elif shock.type == "fraud_spike":
                # Fraud affects trust and costs
                tpv_growth_delta -= shock.intensity * 0.15
                loss_rate_delta += shock.intensity * 0.1
                unit_econ_delta -= shock.intensity * 0.2
        
        # Calculate derived metrics
        compliance_cost_increase = unit_econ_delta * 0.8
        customer_trust_risk = loss_rate_delta * 1.5
        regulatory_risk = compliance_cost_increase * 0.6
        
        return {
            "tpv_growth_delta": max(-0.4, tpv_growth_delta),  # Min -40%
            "loss_rate_delta": min(0.2, loss_rate_delta),  # Max +20%
            "unit_econ_delta": max(-0.5, unit_econ_delta),  # Min -50%
            "compliance_cost_increase": min(0.4, compliance_cost_increase),
            "customer_trust_risk": min(0.3, customer_trust_risk),
            "regulatory_risk": min(0.3, regulatory_risk),
            "fraud_risk": loss_rate_delta * 0.8
        }
    
    def reporting_metrics(self) -> List[str]:
        return [
            "tpv_growth_delta",
            "loss_rate_delta",
            "unit_econ_delta",
            "compliance_cost_increase",
            "customer_trust_risk",
            "regulatory_risk",
            "fraud_risk"
        ]

