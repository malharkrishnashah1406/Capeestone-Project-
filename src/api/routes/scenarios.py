"""
Scenarios API Routes.

This module provides API endpoints for scenario management and analysis.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from ...simulation.scenario_engine import ScenarioParameters, ScenarioEngine, ScenarioResult
from ...simulation.shocks import Shock, ShockGenerator

logger = logging.getLogger(__name__)

router = APIRouter()


class ScenarioCreateRequest(BaseModel):
    """Request model for creating a scenario."""
    name: str
    description: str
    domain_key: str
    num_iterations: int = 1000
    time_horizon_days: int = 365
    seed: Optional[int] = None
    shock_types: Optional[List[str]] = None
    jurisdictions: Optional[List[str]] = None
    correlation_probability: float = 0.3


class ScenarioRunRequest(BaseModel):
    """Request model for running a scenario."""
    scenario_name: str
    parameters: Dict[str, Any]


class WhatIfRequest(BaseModel):
    """Request model for what-if analysis."""
    base_scenario_id: str
    modifications: Dict[str, Any]


class ScenarioResponse(BaseModel):
    """Response model for scenario results."""
    scenario_name: str
    domain_key: str
    num_iterations: int
    time_horizon_days: int
    seed: int
    summary_stats: Dict[str, Dict[str, float]]
    percentiles: Dict[str, List[float]]
    created_at: str


@router.post("/run")
async def run_scenario(request: ScenarioCreateRequest):
    """
    Run a scenario simulation.
    
    Args:
        request: Scenario creation request
        
    Returns:
        Scenario results
    """
    try:
        # Create scenario parameters
        params = ScenarioParameters(
            name=request.name,
            description=request.description,
            domain_key=request.domain_key,
            num_iterations=request.num_iterations,
            time_horizon_days=request.time_horizon_days,
            seed=request.seed,
            shock_types=request.shock_types,
            jurisdictions=request.jurisdictions,
            correlation_probability=request.correlation_probability
        )
        
        # Run scenario
        scenario_engine = ScenarioEngine()
        result = scenario_engine.run_scenario(params)
        
        return ScenarioResponse(
            scenario_name=result.scenario_name,
            domain_key=result.domain_key,
            num_iterations=result.num_iterations,
            time_horizon_days=result.time_horizon_days,
            seed=result.seed,
            summary_stats=result.summary_stats,
            percentiles=result.percentiles,
            created_at=result.created_at.isoformat()
        )
    except Exception as e:
        logger.error(f"Error running scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run/{scenario_name}")
async def run_named_scenario(scenario_name: str, request: ScenarioRunRequest):
    """
    Run a predefined scenario by name.
    
    Args:
        scenario_name: Name of the scenario
        request: Scenario run request
        
    Returns:
        Scenario results
    """
    try:
        # Generate shocks for the named scenario
        shock_generator = ShockGenerator()
        shocks = shock_generator.generate_scenario_shocks(scenario_name)
        
        # Create scenario parameters
        params = ScenarioParameters(
            name=scenario_name,
            description=f"Predefined scenario: {scenario_name}",
            domain_key=request.parameters.get('domain_key', 'venture_capital'),
            num_iterations=request.parameters.get('num_iterations', 1000),
            time_horizon_days=request.parameters.get('time_horizon_days', 365),
            seed=request.parameters.get('seed'),
            custom_shocks=shocks
        )
        
        # Run scenario
        scenario_engine = ScenarioEngine()
        result = scenario_engine.run_scenario(params)
        
        return ScenarioResponse(
            scenario_name=result.scenario_name,
            domain_key=result.domain_key,
            num_iterations=result.num_iterations,
            time_horizon_days=result.time_horizon_days,
            seed=result.seed,
            summary_stats=result.summary_stats,
            percentiles=result.percentiles,
            created_at=result.created_at.isoformat()
        )
    except Exception as e:
        logger.error(f"Error running named scenario {scenario_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/what-if")
async def run_what_if_analysis(request: WhatIfRequest):
    """
    Run what-if analysis by modifying base scenario parameters.
    
    Args:
        request: What-if analysis request
        
    Returns:
        What-if scenario results
    """
    try:
        # For now, we'll create a new scenario with modified parameters
        # In a real implementation, you'd load the base scenario from storage
        
        # Create modified scenario parameters
        params = ScenarioParameters(
            name=f"What-if: {request.base_scenario_id}",
            description=f"Modified version of {request.base_scenario_id}",
            domain_key=request.modifications.get('domain_key', 'venture_capital'),
            num_iterations=request.modifications.get('num_iterations', 1000),
            time_horizon_days=request.modifications.get('time_horizon_days', 365),
            seed=request.modifications.get('seed')
        )
        
        # Run scenario
        scenario_engine = ScenarioEngine()
        result = scenario_engine.run_scenario(params)
        
        return ScenarioResponse(
            scenario_name=result.scenario_name,
            domain_key=result.domain_key,
            num_iterations=result.num_iterations,
            time_horizon_days=result.time_horizon_days,
            seed=result.seed,
            summary_stats=result.summary_stats,
            percentiles=result.percentiles,
            created_at=result.created_at.isoformat()
        )
    except Exception as e:
        logger.error(f"Error running what-if analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available")
async def list_available_scenarios():
    """
    List available predefined scenarios.
    
    Returns:
        List of available scenarios
    """
    try:
        shock_generator = ShockGenerator()
        available_scenarios = list(shock_generator.shock_types.keys())
        
        return {
            "scenarios": available_scenarios,
            "count": len(available_scenarios)
        }
    except Exception as e:
        logger.error(f"Error listing available scenarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shock-types")
async def list_shock_types():
    """
    List available shock types.
    
    Returns:
        List of shock types with descriptions
    """
    try:
        shock_generator = ShockGenerator()
        shock_types = {}
        
        for shock_type, config in shock_generator.shock_types.items():
            shock_types[shock_type] = {
                "description": config['description'],
                "intensity_range": config['intensity_range'],
                "duration_range": config['duration_range'],
                "jurisdictions": config['jurisdictions']
            }
        
        return {
            "shock_types": shock_types,
            "count": len(shock_types)
        }
    except Exception as e:
        logger.error(f"Error listing shock types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_scenarios(scenarios: List[ScenarioResult]):
    """
    Compare multiple scenarios.
    
    Args:
        scenarios: List of scenario results to compare
        
    Returns:
        Comparison results
    """
    try:
        if len(scenarios) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 scenarios to compare")
        
        scenario_engine = ScenarioEngine()
        comparison = scenario_engine.compare_scenarios(scenarios)
        
        return comparison
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing scenarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_scenario_statistics():
    """
    Get statistics about scenario runs.
    
    Returns:
        Scenario statistics
    """
    try:
        # In a real implementation, this would query the database
        # For now, return placeholder statistics
        return {
            "total_scenarios_run": 0,
            "average_iterations": 1000,
            "most_common_domain": "venture_capital",
            "average_time_horizon_days": 365
        }
    except Exception as e:
        logger.error(f"Error getting scenario statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))








