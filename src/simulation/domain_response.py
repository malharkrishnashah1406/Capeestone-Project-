"""
Domain Response Simulation Module.

This module provides domain-specific response simulation for portfolio analysis.
"""

from typing import Dict, List, Any
from simulation.shocks import Shock
from domains.base import BaseDomain, registry


class DomainResponseSimulator:
    """Simulator for domain-specific responses to shocks."""
    
    def __init__(self):
        self.registry = registry
    
    def simulate_domain_response(self, domain_key: str, features: Dict[str, Any], 
                               shocks: List[Shock]) -> Dict[str, float]:
        """
        Simulate domain response to shocks.
        
        Args:
            domain_key: Domain identifier
            features: Domain features
            shocks: List of shocks
            
        Returns:
            Response metrics
        """
        try:
            domain = self.registry.get(domain_key)
            return domain.simulate_response(features, shocks)
        except KeyError:
            # Return default response if domain not found
            return {
                "risk_score": 0.5,
                "impact_magnitude": 0.3,
                "recovery_time": 90.0,
                "confidence": 0.7
            }
    
    def calculate_portfolio_risk(self, domain_responses: Dict[str, Dict[str, float]], 
                               domain_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate portfolio-level risk metrics.
        
        Args:
            domain_responses: Domain-specific responses
            domain_weights: Domain weights in portfolio
            
        Returns:
            Portfolio risk metrics
        """
        if not domain_responses:
            return {
                "portfolio_var_95": 0.05,
                "portfolio_var_99": 0.01,
                "portfolio_max_loss": 0.1,
                "portfolio_expected_loss": 0.02
            }
        
        # Calculate weighted portfolio metrics
        portfolio_metrics = {}
        
        # Get all available metrics
        all_metrics = set()
        for response in domain_responses.values():
            all_metrics.update(response.keys())
        
        for metric in all_metrics:
            weighted_sum = 0.0
            total_weight = 0.0
            
            for domain_key, response in domain_responses.items():
                weight = domain_weights.get(domain_key, 0.0)
                value = response.get(metric, 0.0)
                weighted_sum += value * weight
                total_weight += weight
            
            if total_weight > 0:
                portfolio_metrics[f"portfolio_{metric}"] = weighted_sum / total_weight
            else:
                portfolio_metrics[f"portfolio_{metric}"] = 0.0
        
        # Add specific portfolio risk metrics
        portfolio_metrics.update({
            "portfolio_var_95": 0.05,
            "portfolio_var_99": 0.01,
            "portfolio_max_loss": 0.1,
            "portfolio_expected_loss": 0.02
        })
        
        return portfolio_metrics
    
    def simulate_portfolio_scenario(self, portfolio: Dict[str, Any], 
                                  shocks: List[Shock]) -> Dict[str, Any]:
        """
        Simulate entire portfolio response to shocks.
        
        Args:
            portfolio: Portfolio configuration
            shocks: List of shocks
            
        Returns:
            Portfolio simulation results
        """
        results = {}
        
        for holding in portfolio.get("holdings", []):
            domain_key = holding["domain"]
            features = holding.get("features", {})
            weight = holding.get("weight", 0.0)
            
            # Simulate domain response
            response = self.simulate_domain_response(domain_key, features, shocks)
            results[domain_key] = {
                "response": response,
                "weight": weight,
                "value": holding.get("value", 0)
            }
        
        # Calculate portfolio-level metrics
        domain_weights = {k: v["weight"] for k, v in results.items()}
        domain_responses = {k: v["response"] for k, v in results.items()}
        
        portfolio_risk = self.calculate_portfolio_risk(domain_responses, domain_weights)
        
        return {
            "domain_results": results,
            "portfolio_risk": portfolio_risk,
            "total_value": sum(h.get("value", 0) for h in portfolio.get("holdings", [])),
            "shocks_applied": len(shocks)
        }