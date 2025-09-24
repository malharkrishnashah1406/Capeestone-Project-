"""
Scenario Engine Module.

This module provides the core scenario simulation engine for running
Monte Carlo simulations and what-if analysis.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import logging
# import numpy as np  # Commented out for compatibility
from simulation.shocks import Shock, ShockGenerator
from domains.base import BaseDomain, registry

logger = logging.getLogger(__name__)


@dataclass
class ScenarioParameters:
    """Parameters for scenario simulation."""
    name: str
    description: str
    domain_key: str
    num_iterations: int = 1000
    time_horizon_days: int = 365
    seed: Optional[int] = None
    shock_types: Optional[List[str]] = None
    jurisdictions: Optional[List[str]] = None
    correlation_probability: float = 0.3
    custom_shocks: Optional[List[Shock]] = None


@dataclass
class IterationResult:
    """Result from a single simulation iteration."""
    outcomes: Dict[str, float]
    shocks: List[Shock]

@dataclass
class ScenarioResult:
    """Results from scenario simulation."""
    scenario_name: str
    domain_key: str
    num_iterations: int
    time_horizon_days: int
    seed: int
    summary_stats: Dict[str, Dict[str, float]]
    percentiles: Dict[str, List[float]]
    created_at: datetime
    results: List[IterationResult]
    raw_results: Optional[List[Dict[str, float]]] = None


class ScenarioEngine:
    """Engine for running scenario simulations."""
    
    def __init__(self):
        self.shock_generator = ShockGenerator()
    
    def run_scenario(self, params: ScenarioParameters) -> ScenarioResult:
        """
        Run a scenario simulation.
        
        Args:
            params: Scenario parameters
            
        Returns:
            Scenario results
        """
        # Set random seed if provided
        if params.seed is not None:
            random.seed(params.seed)
        
        # Get domain
        try:
            domain = registry.get(params.domain_key)
        except KeyError:
            raise ValueError(f"Domain {params.domain_key} not found")
        
        # Generate shocks
        if params.custom_shocks:
            shocks = params.custom_shocks
        else:
            shocks = self._generate_shocks(params)
        
        # Run simulation iterations
        results = []
        raw_results = []
        for i in range(params.num_iterations):
            iteration_result = self._run_single_iteration(domain, shocks, params)
            raw_results.append(iteration_result)
            results.append(IterationResult(
                outcomes=iteration_result,
                shocks=shocks
            ))
        
        # Calculate summary statistics
        summary_stats = self._calculate_summary_stats(raw_results)
        percentiles = self._calculate_percentiles(raw_results)
        
        return ScenarioResult(
            scenario_name=params.name,
            domain_key=params.domain_key,
            num_iterations=params.num_iterations,
            time_horizon_days=params.time_horizon_days,
            seed=params.seed or random.randint(0, 2**32-1),
            summary_stats=summary_stats,
            percentiles=percentiles,
            created_at=datetime.now(),
            results=results,
            raw_results=raw_results
        )
    
    def _generate_shocks(self, params: ScenarioParameters) -> List[Shock]:
        """Generate shocks for the scenario."""
        if params.shock_types and params.jurisdictions:
            return self.shock_generator.generate_shock_sequence(
                num_shocks=min(5, params.time_horizon_days // 30),
                shock_types=params.shock_types,
                jurisdictions=params.jurisdictions
            )
        else:
            return self.shock_generator.generate_shock_sequence(
                num_shocks=min(5, params.time_horizon_days // 30)
            )
    
    def _run_single_iteration(self, domain: BaseDomain, shocks: List[Shock], 
                            params: ScenarioParameters) -> Dict[str, float]:
        """Run a single simulation iteration."""
        # Generate random features for the domain
        features = self._generate_random_features(domain)
        
        # Simulate domain response to shocks
        response = domain.simulate_response(features, shocks)
        
        return response
    
    def _generate_random_features(self, domain: BaseDomain) -> Dict[str, Any]:
        """Generate random features for a domain."""
        features = {}
        feature_spec = domain.feature_spec()
        
        for feature_name, feature_desc in feature_spec.items():
            if 'float' in feature_desc.lower():
                if '0-1' in feature_desc:
                    features[feature_name] = random.uniform(0.0, 1.0)
                else:
                    features[feature_name] = random.uniform(0.0, 1000.0)
            elif 'int' in feature_desc.lower():
                features[feature_name] = random.randint(0, 1000)
            elif 'dict' in feature_desc.lower():
                features[feature_name] = {"key1": random.uniform(0.0, 1.0)}
            elif 'list' in feature_desc.lower():
                features[feature_name] = [random.uniform(0.0, 1.0) for _ in range(3)]
            else:
                features[feature_name] = f"random_{feature_name}"
        
        return features
    
    def _calculate_summary_stats(self, results: List[Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """Calculate summary statistics from results."""
        if not results:
            return {}
        
        summary_stats = {}
        
        # Get all metric names
        all_metrics = set()
        for result in results:
            all_metrics.update(result.keys())
        
        for metric in all_metrics:
            values = [result.get(metric, 0.0) for result in results]
            if values:
                mean_val = sum(values) / len(values)
                variance = sum((x - mean_val) ** 2 for x in values) / len(values)
                std_val = variance ** 0.5
                sorted_values = sorted(values)
                median_val = sorted_values[len(sorted_values) // 2] if len(sorted_values) % 2 == 1 else (sorted_values[len(sorted_values) // 2 - 1] + sorted_values[len(sorted_values) // 2]) / 2
                
                summary_stats[metric] = {
                    'mean': mean_val,
                    'std': std_val,
                    'min': min(values),
                    'max': max(values),
                    'median': median_val
                }
        
        return summary_stats
    
    def _calculate_percentiles(self, results: List[Dict[str, float]]) -> Dict[str, List[float]]:
        """Calculate percentiles from results."""
        if not results:
            return {}
        
        percentiles = {}
        
        # Get all metric names
        all_metrics = set()
        for result in results:
            all_metrics.update(result.keys())
        
        for metric in all_metrics:
            values = [result.get(metric, 0.0) for result in results]
            if values:
                sorted_values = sorted(values)
                percentiles[metric] = []
                for p in [5, 10, 25, 50, 75, 90, 95]:
                    index = (p / 100) * (len(sorted_values) - 1)
                    if index.is_integer():
                        percentiles[metric].append(sorted_values[int(index)])
                    else:
                        lower_index = int(index)
                        upper_index = lower_index + 1
                        weight = index - lower_index
                        if upper_index < len(sorted_values):
                            percentile_val = sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
                        else:
                            percentile_val = sorted_values[lower_index]
                        percentiles[metric].append(percentile_val)
            else:
                percentiles[metric] = [0.0] * 7
        
        return percentiles
    
    def compare_scenarios(self, scenarios: List[ScenarioResult]) -> Dict[str, Any]:
        """Compare multiple scenarios."""
        if len(scenarios) < 2:
            raise ValueError("Need at least 2 scenarios to compare")
        
        comparison = {
            "scenarios": [s.scenario_name for s in scenarios],
            "comparison_metrics": {},
            "rankings": {}
        }
        
        # Get common metrics across all scenarios
        all_metrics = set()
        for scenario in scenarios:
            all_metrics.update(scenario.summary_stats.keys())
        
        for metric in all_metrics:
            metric_comparison = {}
            for scenario in scenarios:
                if metric in scenario.summary_stats:
                    metric_comparison[scenario.scenario_name] = scenario.summary_stats[metric]['mean']
            
            comparison["comparison_metrics"][metric] = metric_comparison
            
            # Rank scenarios by this metric (higher is better for most metrics)
            ranked = sorted(metric_comparison.items(), key=lambda x: x[1], reverse=True)
            comparison["rankings"][metric] = [name for name, _ in ranked]
        
        return comparison
    
    def run_what_if_analysis(self, base_result: ScenarioResult, 
                           what_if_params: Dict[str, Any]) -> ScenarioResult:
        """
        Run what-if analysis based on a base scenario.
        
        Args:
            base_result: Base scenario result
            what_if_params: What-if parameters
            
        Returns:
            What-if scenario result
        """
        # Create modified parameters
        modified_params = ScenarioParameters(
            name=f"What-If: {base_result.scenario_name}",
            description=f"What-if analysis of {base_result.scenario_name}",
            domain_key=base_result.domain_key,
            num_iterations=base_result.num_iterations,
            time_horizon_days=base_result.time_horizon_days,
            seed=base_result.seed
        )
        
        # Generate modified shocks
        modified_shocks = []
        for result in base_result.results:
            for shock in result.shocks:
                modified_shock = Shock(
                    type=shock.type,
                    jurisdiction=shock.jurisdiction,
                    intensity=shock.intensity * what_if_params.get('intensity_multiplier', 1.0),
                    duration_days=int(shock.duration_days * what_if_params.get('duration_multiplier', 1.0)),
                    start_date=shock.start_date,
                    confidence=shock.confidence,
                    source_refs=shock.source_refs
                )
                modified_shocks.append(modified_shock)
        
        # Add additional shocks if specified
        additional_shocks = what_if_params.get('additional_shocks', 0)
        if additional_shocks > 0:
            extra_shocks = self.shock_generator.generate_shock_sequence(
                num_shocks=additional_shocks
            )
            modified_shocks.extend(extra_shocks)
        
        # Run modified scenario
        modified_params.custom_shocks = modified_shocks
        return self.run_scenario(modified_params)