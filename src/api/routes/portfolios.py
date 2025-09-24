"""
Portfolios API Routes.

This module provides API endpoints for portfolio management and analysis.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from ...simulation.domain_response import DomainResponseSimulator
from ...simulation.shocks import ShockGenerator

logger = logging.getLogger(__name__)

router = APIRouter()


class PortfolioCreateRequest(BaseModel):
    """Request model for creating a portfolio."""
    name: str
    description: str
    fund_id: Optional[str] = None
    base_currency: str = "USD"
    holdings: List[Dict[str, Any]]


class PortfolioSimulationRequest(BaseModel):
    """Request model for portfolio simulation."""
    portfolio_id: str
    shocks: Optional[List[Dict[str, Any]]] = None
    scenario_name: Optional[str] = None
    num_iterations: int = 1000


class Holding(BaseModel):
    """Model for portfolio holding."""
    startup_id: str
    domain_key: str
    weight: float
    features: Dict[str, Any]


class PortfolioResponse(BaseModel):
    """Response model for portfolio."""
    id: str
    name: str
    description: str
    fund_id: Optional[str]
    base_currency: str
    holdings: List[Holding]
    total_weight: float


class PortfolioSimulationResponse(BaseModel):
    """Response model for portfolio simulation."""
    portfolio_id: str
    scenario_name: str
    risk_metrics: Dict[str, float]
    domain_responses: Dict[str, Dict[str, Any]]
    portfolio_metrics: Dict[str, float]


@router.post("/")
async def create_portfolio(request: PortfolioCreateRequest):
    """
    Create a new portfolio.
    
    Args:
        request: Portfolio creation request
        
    Returns:
        Created portfolio
    """
    try:
        # Validate holdings
        total_weight = sum(holding.get('weight', 0) for holding in request.holdings)
        if abs(total_weight - 1.0) > 0.01:
            raise HTTPException(status_code=400, detail="Portfolio weights must sum to 1.0")
        
        # In a real implementation, this would save to database
        portfolio_id = f"portfolio_{len(request.holdings)}_{hash(request.name) % 10000}"
        
        holdings = []
        for holding in request.holdings:
            holdings.append(Holding(
                startup_id=holding.get('startup_id', ''),
                domain_key=holding.get('domain_key', ''),
                weight=holding.get('weight', 0.0),
                features=holding.get('features', {})
            ))
        
        return PortfolioResponse(
            id=portfolio_id,
            name=request.name,
            description=request.description,
            fund_id=request.fund_id,
            base_currency=request.base_currency,
            holdings=holdings,
            total_weight=total_weight
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: str):
    """
    Get portfolio by ID.
    
    Args:
        portfolio_id: Portfolio ID
        
    Returns:
        Portfolio information
    """
    try:
        # In a real implementation, this would query the database
        # For now, return a placeholder portfolio
        return PortfolioResponse(
            id=portfolio_id,
            name="Sample Portfolio",
            description="A sample portfolio for demonstration",
            fund_id="fund_001",
            base_currency="USD",
            holdings=[
                Holding(
                    startup_id="startup_001",
                    domain_key="venture_capital",
                    weight=0.4,
                    features={"dry_powder": 0.6, "fund_age_years": 3}
                ),
                Holding(
                    startup_id="startup_002",
                    domain_key="saas",
                    weight=0.3,
                    features={"arr": 1000000, "gross_churn": 0.05}
                ),
                Holding(
                    startup_id="startup_003",
                    domain_key="fintech",
                    weight=0.3,
                    features={"tpv": 10000000, "fraud_rate": 0.02}
                )
            ],
            total_weight=1.0
        )
    except Exception as e:
        logger.error(f"Error getting portfolio {portfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{portfolio_id}/simulate")
async def simulate_portfolio(portfolio_id: str, request: PortfolioSimulationRequest):
    """
    Run simulation for a portfolio.
    
    Args:
        portfolio_id: Portfolio ID
        request: Simulation request
        
    Returns:
        Simulation results
    """
    try:
        # Get portfolio (in real implementation, query database)
        portfolio = await get_portfolio(portfolio_id)
        
        # Generate shocks
        shock_generator = ShockGenerator()
        if request.scenario_name:
            shocks = shock_generator.generate_scenario_shocks(request.scenario_name)
        elif request.shocks:
            # Convert dict shocks to Shock objects
            shocks = []
            for shock_dict in request.shocks:
                # This is a simplified conversion - in real implementation,
                # you'd have proper Shock object creation
                shocks.append(shock_dict)
        else:
            # Generate random shocks
            shocks = shock_generator.generate_shock_sequence(num_shocks=3)
        
        # Simulate domain responses
        simulator = DomainResponseSimulator()
        domain_responses = {}
        
        # Group holdings by domain
        domain_holdings = {}
        for holding in portfolio.holdings:
            if holding.domain_key not in domain_holdings:
                domain_holdings[holding.domain_key] = []
            domain_holdings[holding.domain_key].append(holding)
        
        # Simulate each domain
        for domain_key, holdings in domain_holdings.items():
            # Aggregate features weighted by holding weights
            aggregated_features = {}
            total_weight = sum(h.weight for h in holdings)
            
            for holding in holdings:
                weight_ratio = holding.weight / total_weight
                for feature, value in holding.features.items():
                    if feature not in aggregated_features:
                        aggregated_features[feature] = 0.0
                    aggregated_features[feature] += value * weight_ratio
            
            # Simulate domain response
            response = simulator.simulate_domain_response(domain_key, aggregated_features, shocks)
            domain_responses[domain_key] = {
                "outcomes": response.outcomes,
                "confidence": response.confidence,
                "timestamp": response.timestamp.isoformat()
            }
        
        # Calculate portfolio risk metrics
        domain_weights = {}
        for holding in portfolio.holdings:
            if holding.domain_key not in domain_weights:
                domain_weights[holding.domain_key] = 0.0
            domain_weights[holding.domain_key] += holding.weight
        
        portfolio_metrics = simulator.calculate_portfolio_risk(domain_responses, domain_weights)
        
        # Calculate overall risk metrics
        risk_metrics = {
            "portfolio_var_95": portfolio_metrics.get("portfolio_var_95", 0.0),
            "total_exposure": sum(domain_weights.values()),
            "num_domains": len(domain_weights),
            "num_holdings": len(portfolio.holdings)
        }
        
        return PortfolioSimulationResponse(
            portfolio_id=portfolio_id,
            scenario_name=request.scenario_name or "custom",
            risk_metrics=risk_metrics,
            domain_responses=domain_responses,
            portfolio_metrics=portfolio_metrics
        )
    except Exception as e:
        logger.error(f"Error simulating portfolio {portfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{portfolio_id}/holdings")
async def get_portfolio_holdings(portfolio_id: str):
    """
    Get holdings for a portfolio.
    
    Args:
        portfolio_id: Portfolio ID
        
    Returns:
        Portfolio holdings
    """
    try:
        portfolio = await get_portfolio(portfolio_id)
        return {
            "portfolio_id": portfolio_id,
            "holdings": [holding.dict() for holding in portfolio.holdings],
            "total_weight": portfolio.total_weight
        }
    except Exception as e:
        logger.error(f"Error getting holdings for portfolio {portfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{portfolio_id}/exposure")
async def get_portfolio_exposure(portfolio_id: str):
    """
    Get domain exposure for a portfolio.
    
    Args:
        portfolio_id: Portfolio ID
        
    Returns:
        Domain exposure breakdown
    """
    try:
        portfolio = await get_portfolio(portfolio_id)
        
        # Calculate domain exposure
        domain_exposure = {}
        for holding in portfolio.holdings:
            if holding.domain_key not in domain_exposure:
                domain_exposure[holding.domain_key] = 0.0
            domain_exposure[holding.domain_key] += holding.weight
        
        return {
            "portfolio_id": portfolio_id,
            "domain_exposure": domain_exposure,
            "total_exposure": sum(domain_exposure.values())
        }
    except Exception as e:
        logger.error(f"Error getting exposure for portfolio {portfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{portfolio_id}/stress-test")
async def run_portfolio_stress_test(portfolio_id: str):
    """
    Run stress tests for a portfolio.
    
    Args:
        portfolio_id: Portfolio ID
        
    Returns:
        Stress test results
    """
    try:
        portfolio = await get_portfolio(portfolio_id)
        
        # Generate stress test scenarios
        simulator = DomainResponseSimulator()
        shock_generator = ShockGenerator()
        
        stress_scenarios = {
            'severe_recession': shock_generator.generate_shock_sequence(
                num_shocks=4,
                shock_types=['market_crash', 'policy_rate_change', 'political_instability', 'regulatory_change']
            ),
            'black_swan': shock_generator.generate_shock_sequence(
                num_shocks=5,
                shock_types=['pandemic', 'market_crash', 'cybersecurity_breach', 'climate_event', 'political_instability']
            ),
            'liquidity_crisis': shock_generator.generate_shock_sequence(
                num_shocks=2,
                shock_types=['policy_rate_change', 'market_crash']
            )
        }
        
        stress_results = {}
        for scenario_name, shocks in stress_scenarios.items():
            # Simulate portfolio under stress scenario
            simulation_request = PortfolioSimulationRequest(
                portfolio_id=portfolio_id,
                shocks=[shock.__dict__ for shock in shocks],
                scenario_name=scenario_name
            )
            
            result = await simulate_portfolio(portfolio_id, simulation_request)
            stress_results[scenario_name] = {
                "risk_metrics": result.risk_metrics,
                "portfolio_metrics": result.portfolio_metrics
            }
        
        return {
            "portfolio_id": portfolio_id,
            "stress_tests": stress_results
        }
    except Exception as e:
        logger.error(f"Error running stress test for portfolio {portfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_portfolios():
    """
    List all portfolios.
    
    Returns:
        List of portfolios
    """
    try:
        # In a real implementation, this would query the database
        # For now, return placeholder data
        return {
            "portfolios": [
                {
                    "id": "portfolio_001",
                    "name": "Sample Portfolio 1",
                    "description": "A sample portfolio",
                    "num_holdings": 3,
                    "total_weight": 1.0
                }
            ],
            "count": 1
        }
    except Exception as e:
        logger.error(f"Error listing portfolios: {e}")
        raise HTTPException(status_code=500, detail=str(e))








