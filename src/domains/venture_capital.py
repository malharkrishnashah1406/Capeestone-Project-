"""
Venture Capital / Private Equity Portfolio Analysis Domain.

This domain analyzes venture capital and private equity portfolios,
focusing on fund performance, portfolio company health, and market dynamics.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import random
from .base import BaseDomain, Event, Shock


class VentureCapitalDomain(BaseDomain):
    """Domain for analyzing venture capital and private equity portfolios."""
    
    @property
    def key(self) -> str:
        return "venture_capital"
    
    @property
    def name(self) -> str:
        return "Venture Capital / Private Equity"
    
    @property
    def description(self) -> str:
        return "Analysis of venture capital and private equity portfolios, including fund performance, portfolio company health, and market dynamics."
    
    def feature_spec(self) -> Dict[str, str]:
        return {
            "dry_powder": "float - Available capital for new investments",
            "fund_age_years": "float - Age of the fund in years",
            "sector_exposure": "dict - Exposure to different sectors (tech, health, fintech, etc.)",
            "geo_exposure": "dict - Geographic exposure by region/country",
            "follow_on_rate": "float - Rate of follow-on investments (0-1)",
            "dpi": "float - Distributions to Paid-In capital ratio",
            "tvpi": "float - Total Value to Paid-In capital ratio",
            "bridge_need_ratio": "float - Ratio of companies needing bridge rounds",
            "portfolio_size": "int - Number of portfolio companies",
            "avg_round_size": "float - Average investment round size",
            "exit_pipeline": "dict - Companies in exit pipeline by stage",
            "liquidity_ratio": "float - Ratio of liquid to illiquid holdings"
        }
    
    def extract_features(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract VC-specific features from input data."""
        features = {}
        
        # Basic fund metrics
        features["dry_powder"] = inputs.get("dry_powder", 0.0)
        features["fund_age_years"] = inputs.get("fund_age_years", 0.0)
        features["portfolio_size"] = inputs.get("portfolio_size", 0)
        
        # Performance metrics
        features["follow_on_rate"] = inputs.get("follow_on_rate", 0.0)
        features["dpi"] = inputs.get("dpi", 0.0)
        features["tvpi"] = inputs.get("tvpi", 0.0)
        features["bridge_need_ratio"] = inputs.get("bridge_need_ratio", 0.0)
        
        # Exposure metrics
        features["sector_exposure"] = inputs.get("sector_exposure", {})
        features["geo_exposure"] = inputs.get("geo_exposure", {})
        
        # Additional metrics
        features["avg_round_size"] = inputs.get("avg_round_size", 0.0)
        features["exit_pipeline"] = inputs.get("exit_pipeline", {})
        features["liquidity_ratio"] = inputs.get("liquidity_ratio", 0.0)
        
        return features
    
    def risk_factors(self) -> List[str]:
        return [
            "liquidity_tightening",
            "rate_hikes",
            "exit_window_closure",
            "dry_powder_depletion",
            "portfolio_concentration",
            "market_correction",
            "regulatory_changes",
            "geopolitical_risks"
        ]
    
    def map_events_to_shocks(self, events: List[Event]) -> List[Shock]:
        """Map events to VC-specific shocks."""
        shocks = []
        
        for event in events:
            if event.category in ["rate_hike", "monetary_policy"]:
                shocks.append(Shock(
                    type="liquidity_tightening",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.8, abs(event.sentiment) * 0.8),
                    duration_days=180,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
            
            elif event.category in ["market_crash", "recession"]:
                shocks.append(Shock(
                    type="exit_window_closure",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.9, abs(event.sentiment) * 0.9),
                    duration_days=365,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
            
            elif event.category in ["regulation", "policy_change"]:
                shocks.append(Shock(
                    type="regulatory_changes",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.7, abs(event.sentiment) * 0.7),
                    duration_days=90,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
        
        return shocks
    
    def simulate_response(self, features: Dict[str, Any], shocks: List[Shock]) -> Dict[str, float]:
        """Simulate VC portfolio response to shocks."""
        # Initialize base metrics
        portfolio_var = 0.15  # Base portfolio VaR
        downround_prob = 0.1  # Base downround probability
        follow_on_shortfall = 0.0
        
        # Apply shock effects
        for shock in shocks:
            if shock.type == "liquidity_tightening":
                # Liquidity tightening affects follow-on funding
                follow_on_shortfall += shock.intensity * 0.3
                portfolio_var += shock.intensity * 0.1
                downround_prob += shock.intensity * 0.2
            
            elif shock.type == "exit_window_closure":
                # Exit window closure affects DPI and TVPI
                portfolio_var += shock.intensity * 0.2
                downround_prob += shock.intensity * 0.3
            
            elif shock.type == "regulatory_changes":
                # Regulatory changes affect specific sectors
                portfolio_var += shock.intensity * 0.05
                downround_prob += shock.intensity * 0.1
        
        # Calculate derived metrics
        bridge_need_increase = downround_prob * 0.5
        dry_powder_efficiency = max(0, 1 - follow_on_shortfall)
        
        return {
            "portfolio_var": min(0.5, portfolio_var),  # Cap at 50%
            "downround_prob": min(0.8, downround_prob),  # Cap at 80%
            "follow_on_shortfall": min(1.0, follow_on_shortfall),  # Cap at 100%
            "bridge_need_increase": min(0.5, bridge_need_increase),
            "dry_powder_efficiency": max(0.1, dry_powder_efficiency),
            "exit_pipeline_risk": portfolio_var * 0.8,
            "liquidity_risk": follow_on_shortfall * 0.6
        }
    
    def reporting_metrics(self) -> List[str]:
        return [
            "portfolio_var",
            "downround_prob",
            "follow_on_shortfall",
            "bridge_need_increase",
            "dry_powder_efficiency",
            "exit_pipeline_risk",
            "liquidity_risk"
        ]

