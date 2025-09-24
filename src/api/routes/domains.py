"""
Domains API Routes.

This module provides API endpoints for domain management and analysis.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from ...utils.registry import get_domain, list_domains, list_domain_keys, get_all_domain_info
from ...domains.base import BaseDomain
from ...simulation.scenario_engine import ScenarioParameters, ScenarioEngine
from ...simulation.domain_response import DomainResponseSimulator

logger = logging.getLogger(__name__)

router = APIRouter()


class DomainFeatureRequest(BaseModel):
    """Request model for domain feature extraction."""
    features: Dict[str, Any]
    domain_key: str


class DomainSimulationRequest(BaseModel):
    """Request model for domain simulation."""
    domain_key: str
    features: Dict[str, Any]
    shocks: Optional[List[Dict[str, Any]]] = None
    num_iterations: int = 100
    time_horizon_days: int = 365


class DomainSimulationResponse(BaseModel):
    """Response model for domain simulation."""
    domain_key: str
    outcomes: Dict[str, float]
    confidence: float
    summary_stats: Dict[str, Dict[str, float]]
    percentiles: Dict[str, List[float]]


@router.get("/")
async def list_domains_endpoint():
    """
    List all available domains.
    
    Returns:
        List of domain information
    """
    try:
        domain_info = get_all_domain_info()
        return {
            "domains": domain_info,
            "count": len(domain_info)
        }
    except Exception as e:
        logger.error(f"Error listing domains: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{domain_key}")
async def get_domain_endpoint(domain_key: str):
    """
    Get information about a specific domain.
    
    Args:
        domain_key: Domain key identifier
        
    Returns:
        Domain information
    """
    try:
        domain_info = get_domain_info(domain_key)
        if not domain_info:
            raise HTTPException(status_code=404, detail=f"Domain {domain_key} not found")
        return domain_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting domain {domain_key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{domain_key}/features")
async def get_domain_features(domain_key: str):
    """
    Get feature specification for a domain.
    
    Args:
        domain_key: Domain key identifier
        
    Returns:
        Domain feature specification
    """
    try:
        domain = get_domain(domain_key)
        feature_spec = domain.feature_spec()
        return {
            "domain_key": domain_key,
            "features": feature_spec
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Domain {domain_key} not found")
    except Exception as e:
        logger.error(f"Error getting features for domain {domain_key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{domain_key}/features/extract")
async def extract_domain_features(domain_key: str, request: DomainFeatureRequest):
    """
    Extract features for a domain from input data.
    
    Args:
        domain_key: Domain key identifier
        request: Feature extraction request
        
    Returns:
        Extracted features
    """
    try:
        domain = get_domain(domain_key)
        features = domain.extract_features(request.features)
        return {
            "domain_key": domain_key,
            "extracted_features": features
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Domain {domain_key} not found")
    except Exception as e:
        logger.error(f"Error extracting features for domain {domain_key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{domain_key}/risk-factors")
async def get_domain_risk_factors(domain_key: str):
    """
    Get risk factors for a domain.
    
    Args:
        domain_key: Domain key identifier
        
    Returns:
        List of risk factors
    """
    try:
        domain = get_domain(domain_key)
        risk_factors = domain.risk_factors()
        return {
            "domain_key": domain_key,
            "risk_factors": risk_factors
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Domain {domain_key} not found")
    except Exception as e:
        logger.error(f"Error getting risk factors for domain {domain_key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{domain_key}/simulate")
async def simulate_domain(domain_key: str, request: DomainSimulationRequest):
    """
    Run a simulation for a domain.
    
    Args:
        domain_key: Domain key identifier
        request: Simulation request
        
    Returns:
        Simulation results
    """
    try:
        # Validate domain
        domain = get_domain(domain_key)
        
        # Create scenario parameters
        params = ScenarioParameters(
            name=f"Domain simulation for {domain_key}",
            description=f"Simulation for domain {domain_key}",
            domain_key=domain_key,
            num_iterations=request.num_iterations,
            time_horizon_days=request.time_horizon_days
        )
        
        # Run simulation
        scenario_engine = ScenarioEngine()
        result = scenario_engine.run_scenario(params)
        
        return DomainSimulationResponse(
            domain_key=domain_key,
            outcomes=result.summary_stats,
            confidence=0.8,  # Placeholder
            summary_stats=result.summary_stats,
            percentiles=result.percentiles
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Domain {domain_key} not found")
    except Exception as e:
        logger.error(f"Error simulating domain {domain_key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{domain_key}/reporting-metrics")
async def get_domain_reporting_metrics(domain_key: str):
    """
    Get reporting metrics for a domain.
    
    Args:
        domain_key: Domain key identifier
        
    Returns:
        List of reporting metrics
    """
    try:
        domain = get_domain(domain_key)
        metrics = domain.reporting_metrics()
        return {
            "domain_key": domain_key,
            "reporting_metrics": metrics
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Domain {domain_key} not found")
    except Exception as e:
        logger.error(f"Error getting reporting metrics for domain {domain_key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{domain_key}/stress-test")
async def run_domain_stress_test(domain_key: str, features: Dict[str, Any]):
    """
    Run stress tests for a domain.
    
    Args:
        domain_key: Domain key identifier
        features: Domain features
        
    Returns:
        Stress test results
    """
    try:
        domain = get_domain(domain_key)
        simulator = DomainResponseSimulator()
        results = simulator.run_stress_tests(domain_key, features)
        
        # Convert results to serializable format
        serializable_results = {}
        for scenario_name, response in results.items():
            serializable_results[scenario_name] = {
                "outcomes": response.outcomes,
                "confidence": response.confidence,
                "timestamp": response.timestamp.isoformat()
            }
        
        return {
            "domain_key": domain_key,
            "stress_tests": serializable_results
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Domain {domain_key} not found")
    except Exception as e:
        logger.error(f"Error running stress test for domain {domain_key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))








