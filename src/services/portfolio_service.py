"""
Portfolio Service.

This module provides business logic for portfolio management and analysis.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from ..simulation.domain_response import DomainResponseSimulator
from ..simulation.shocks import ShockGenerator
from ..utils.registry import get_domain

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service for portfolio management and analysis."""
    
    def __init__(self):
        self.simulator = DomainResponseSimulator()
        self.shock_generator = ShockGenerator()
    
    def create_portfolio(self, name: str, description: str, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a new portfolio.
        
        Args:
            name: Portfolio name
            description: Portfolio description
            holdings: List of holdings with domain and feature information
            
        Returns:
            Created portfolio
        """
        try:
            # Validate holdings
            self._validate_holdings(holdings)
            
            # Calculate total weight
            total_weight = sum(holding.get('weight', 0) for holding in holdings)
            
            # Generate portfolio ID
            portfolio_id = f"portfolio_{hash(name) % 10000}"
            
            portfolio = {
                "id": portfolio_id,
                "name": name,
                "description": description,
                "holdings": holdings,
                "total_weight": total_weight,
                "num_holdings": len(holdings),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Calculate domain exposure
            portfolio["domain_exposure"] = self._calculate_domain_exposure(holdings)
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Error creating portfolio: {e}")
            raise
    
    def _validate_holdings(self, holdings: List[Dict[str, Any]]) -> None:
        """Validate portfolio holdings."""
        if not holdings:
            raise ValueError("Portfolio must have at least one holding")
        
        total_weight = 0
        for holding in holdings:
            # Validate required fields
            if 'domain_key' not in holding:
                raise ValueError("Each holding must have a domain_key")
            
            if 'weight' not in holding:
                raise ValueError("Each holding must have a weight")
            
            # Validate domain exists
            try:
                get_domain(holding['domain_key'])
            except KeyError:
                raise ValueError(f"Unknown domain: {holding['domain_key']}")
            
            # Validate weight
            weight = holding['weight']
            if not isinstance(weight, (int, float)) or weight < 0:
                raise ValueError("Weight must be a non-negative number")
            
            total_weight += weight
        
        # Validate total weight
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError("Portfolio weights must sum to 1.0")
    
    def _calculate_domain_exposure(self, holdings: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate domain exposure for portfolio."""
        domain_exposure = {}
        
        for holding in holdings:
            domain_key = holding['domain_key']
            weight = holding['weight']
            
            if domain_key not in domain_exposure:
                domain_exposure[domain_key] = 0.0
            
            domain_exposure[domain_key] += weight
        
        return domain_exposure
    
    def analyze_portfolio_risk(self, portfolio: Dict[str, Any], 
                             scenario_name: Optional[str] = None,
                             custom_shocks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Analyze portfolio risk under different scenarios.
        
        Args:
            portfolio: Portfolio data
            scenario_name: Name of predefined scenario
            custom_shocks: Custom shock definitions
            
        Returns:
            Risk analysis results
        """
        try:
            holdings = portfolio['holdings']
            
            # Generate shocks
            if scenario_name:
                shocks = self.shock_generator.generate_scenario_shocks(scenario_name)
            elif custom_shocks:
                # Convert dict shocks to Shock objects (simplified)
                shocks = custom_shocks
            else:
                # Generate random shocks
                shocks = self.shock_generator.generate_shock_sequence(num_shocks=3)
            
            # Group holdings by domain
            domain_holdings = {}
            for holding in holdings:
                domain_key = holding['domain_key']
                if domain_key not in domain_holdings:
                    domain_holdings[domain_key] = []
                domain_holdings[domain_key].append(holding)
            
            # Simulate each domain
            domain_responses = {}
            for domain_key, domain_holdings_list in domain_holdings.items():
                # Aggregate features weighted by holding weights
                aggregated_features = self._aggregate_domain_features(domain_holdings_list)
                
                # Simulate domain response
                response = self.simulator.simulate_domain_response(domain_key, aggregated_features, shocks)
                domain_responses[domain_key] = response
            
            # Calculate portfolio-level metrics
            portfolio_metrics = self._calculate_portfolio_metrics(domain_responses, holdings)
            
            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(domain_responses, holdings)
            
            return {
                "portfolio_id": portfolio['id'],
                "scenario_name": scenario_name or "custom",
                "shocks": [shock.__dict__ if hasattr(shock, '__dict__') else shock for shock in shocks],
                "domain_responses": {
                    domain: {
                        "outcomes": response.outcomes,
                        "confidence": response.confidence,
                        "timestamp": response.timestamp.isoformat()
                    }
                    for domain, response in domain_responses.items()
                },
                "portfolio_metrics": portfolio_metrics,
                "risk_metrics": risk_metrics,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio risk: {e}")
            raise
    
    def _aggregate_domain_features(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate features for a domain weighted by holding weights."""
        aggregated_features = {}
        total_weight = sum(holding['weight'] for holding in holdings)
        
        for holding in holdings:
            weight_ratio = holding['weight'] / total_weight
            features = holding.get('features', {})
            
            for feature, value in features.items():
                if feature not in aggregated_features:
                    aggregated_features[feature] = 0.0
                
                if isinstance(value, (int, float)):
                    aggregated_features[feature] += value * weight_ratio
                elif isinstance(value, dict):
                    # For dictionary features, aggregate recursively
                    if feature not in aggregated_features:
                        aggregated_features[feature] = {}
                    
                    for sub_feature, sub_value in value.items():
                        if sub_feature not in aggregated_features[feature]:
                            aggregated_features[feature][sub_feature] = 0.0
                        
                        if isinstance(sub_value, (int, float)):
                            aggregated_features[feature][sub_feature] += sub_value * weight_ratio
        
        return aggregated_features
    
    def _calculate_portfolio_metrics(self, domain_responses: Dict[str, Any], 
                                   holdings: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate portfolio-level metrics."""
        portfolio_metrics = {}
        
        # Calculate weighted outcomes
        for domain_key, response in domain_responses.items():
            domain_weight = sum(h['weight'] for h in holdings if h['domain_key'] == domain_key)
            
            for metric, value in response.outcomes.items():
                portfolio_metric = f"portfolio_{metric}"
                if portfolio_metric not in portfolio_metrics:
                    portfolio_metrics[portfolio_metric] = 0.0
                
                portfolio_metrics[portfolio_metric] += value * domain_weight
        
        return portfolio_metrics
    
    def _calculate_risk_metrics(self, domain_responses: Dict[str, Any], 
                              holdings: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate risk metrics for the portfolio."""
        risk_metrics = {
            "total_exposure": 1.0,
            "num_domains": len(domain_responses),
            "num_holdings": len(holdings),
            "diversification_score": self._calculate_diversification_score(holdings),
            "concentration_risk": self._calculate_concentration_risk(holdings)
        }
        
        # Calculate portfolio VaR (simplified)
        if domain_responses:
            # Aggregate outcomes for VaR calculation
            all_outcomes = []
            for response in domain_responses.values():
                all_outcomes.extend(response.outcomes.values())
            
            if all_outcomes:
                # Simple VaR calculation (5th percentile)
                sorted_outcomes = sorted(all_outcomes)
                var_index = int(len(sorted_outcomes) * 0.05)
                risk_metrics["portfolio_var_95"] = sorted_outcomes[var_index] if var_index < len(sorted_outcomes) else sorted_outcomes[0]
        
        return risk_metrics
    
    def _calculate_diversification_score(self, holdings: List[Dict[str, Any]]) -> float:
        """Calculate diversification score (0-1, higher is better)."""
        if len(holdings) <= 1:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index
        hhi = sum(holding['weight'] ** 2 for holding in holdings)
        
        # Convert to diversification score (1 - normalized HHI)
        max_hhi = 1.0  # Maximum HHI for single holding
        min_hhi = 1.0 / len(holdings)  # Minimum HHI for equal weights
        
        if max_hhi == min_hhi:
            return 1.0
        
        normalized_hhi = (hhi - min_hhi) / (max_hhi - min_hhi)
        return 1.0 - normalized_hhi
    
    def _calculate_concentration_risk(self, holdings: List[Dict[str, Any]]) -> float:
        """Calculate concentration risk (0-1, higher is worse)."""
        if not holdings:
            return 0.0
        
        # Calculate the weight of the largest holding
        max_weight = max(holding['weight'] for holding in holdings)
        return max_weight
    
    def run_stress_tests(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run stress tests for a portfolio.
        
        Args:
            portfolio: Portfolio data
            
        Returns:
            Stress test results
        """
        try:
            stress_scenarios = [
                'severe_recession',
                'black_swan',
                'liquidity_crisis',
                'regulatory_crackdown'
            ]
            
            stress_results = {}
            
            for scenario in stress_scenarios:
                try:
                    result = self.analyze_portfolio_risk(portfolio, scenario_name=scenario)
                    stress_results[scenario] = {
                        "risk_metrics": result["risk_metrics"],
                        "portfolio_metrics": result["portfolio_metrics"]
                    }
                except Exception as e:
                    logger.warning(f"Failed to run stress test {scenario}: {e}")
                    stress_results[scenario] = {"error": str(e)}
            
            return {
                "portfolio_id": portfolio['id'],
                "stress_tests": stress_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error running stress tests: {e}")
            raise
    
    def get_portfolio_recommendations(self, portfolio: Dict[str, Any], 
                                    risk_tolerance: str = "medium") -> Dict[str, Any]:
        """
        Get portfolio recommendations based on risk tolerance.
        
        Args:
            portfolio: Portfolio data
            risk_tolerance: Risk tolerance level (low/medium/high)
            
        Returns:
            Portfolio recommendations
        """
        try:
            recommendations = {
                "risk_tolerance": risk_tolerance,
                "recommendations": [],
                "warnings": [],
                "suggestions": []
            }
            
            holdings = portfolio['holdings']
            domain_exposure = portfolio['domain_exposure']
            
            # Check diversification
            diversification_score = self._calculate_diversification_score(holdings)
            if diversification_score < 0.3:
                recommendations["warnings"].append("Low diversification - consider adding more holdings")
            elif diversification_score < 0.6:
                recommendations["suggestions"].append("Moderate diversification - could be improved")
            
            # Check concentration risk
            concentration_risk = self._calculate_concentration_risk(holdings)
            if concentration_risk > 0.4:
                recommendations["warnings"].append(f"High concentration risk ({concentration_risk:.1%}) - consider reducing largest holding")
            
            # Check domain exposure
            if len(domain_exposure) < 3:
                recommendations["suggestions"].append("Limited domain exposure - consider diversifying across more domains")
            
            # Risk tolerance specific recommendations
            if risk_tolerance == "low":
                if concentration_risk > 0.2:
                    recommendations["recommendations"].append("Reduce concentration for lower risk tolerance")
                if diversification_score < 0.7:
                    recommendations["recommendations"].append("Increase diversification for lower risk tolerance")
            
            elif risk_tolerance == "high":
                if concentration_risk < 0.3:
                    recommendations["suggestions"].append("Consider higher concentration for higher risk tolerance")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting portfolio recommendations: {e}")
            raise








