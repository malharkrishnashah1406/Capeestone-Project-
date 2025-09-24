"""
Tests for simulation module.
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from simulation.shocks import Shock, ShockGenerator
from simulation.scenario_engine import ScenarioParameters, ScenarioEngine, SimulationResult, ScenarioResult
from simulation.domain_response import DomainResponse, DomainResponseSimulator
from domains.venture_capital import VentureCapitalDomain


class TestShock(unittest.TestCase):
    """Test Shock dataclass."""
    
    def test_shock_creation(self):
        """Test creating a shock."""
        shock = Shock(
            type="policy_rate_change",
            jurisdiction="US",
            intensity=0.5,
            duration_days=30,
            start_date=datetime.now(),
            confidence=0.8,
            source_refs=["test"],
            description="Test shock"
        )
        
        self.assertEqual(shock.type, "policy_rate_change")
        self.assertEqual(shock.jurisdiction, "US")
        self.assertEqual(shock.intensity, 0.5)
        self.assertEqual(shock.duration_days, 30)
        self.assertEqual(shock.confidence, 0.8)
        self.assertEqual(shock.description, "Test shock")
    
    def test_shock_default_description(self):
        """Test shock with default description."""
        shock = Shock(
            type="policy_rate_change",
            jurisdiction="US",
            intensity=0.5,
            duration_days=30,
            start_date=datetime.now(),
            confidence=0.8,
            source_refs=["test"]
        )
        
        self.assertEqual(shock.description, "")


class TestShockGenerator(unittest.TestCase):
    """Test ShockGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ShockGenerator()
    
    def test_shock_types(self):
        """Test available shock types."""
        expected_types = [
            'policy_rate_change', 'regulatory_change', 'market_crash',
            'trade_war', 'pandemic', 'cybersecurity_breach',
            'climate_event', 'political_instability'
        ]
        
        for shock_type in expected_types:
            self.assertIn(shock_type, self.generator.shock_types)
    
    def test_generate_random_shock(self):
        """Test generating a random shock."""
        shock = self.generator.generate_random_shock()
        
        self.assertIsInstance(shock, Shock)
        self.assertIn(shock.type, self.generator.shock_types)
        self.assertGreaterEqual(shock.intensity, 0.0)
        self.assertLessEqual(shock.intensity, 1.0)
        self.assertGreater(shock.duration_days, 0)
        self.assertGreaterEqual(shock.confidence, 0.0)
        self.assertLessEqual(shock.confidence, 1.0)
    
    def test_generate_random_shock_specific_type(self):
        """Test generating a random shock with specific type."""
        shock = self.generator.generate_random_shock("policy_rate_change")
        
        self.assertEqual(shock.type, "policy_rate_change")
        self.assertIn(shock.jurisdiction, self.generator.shock_types["policy_rate_change"]["jurisdictions"])
    
    def test_generate_random_shock_specific_jurisdiction(self):
        """Test generating a random shock with specific jurisdiction."""
        shock = self.generator.generate_random_shock(jurisdiction="US")
        
        self.assertEqual(shock.jurisdiction, "US")
    
    def test_generate_random_shock_invalid_type(self):
        """Test generating a random shock with invalid type."""
        with self.assertRaises(ValueError):
            self.generator.generate_random_shock("invalid_type")
    
    def test_generate_shock_sequence(self):
        """Test generating a sequence of shocks."""
        shocks = self.generator.generate_shock_sequence(num_shocks=5)
        
        self.assertEqual(len(shocks), 5)
        for shock in shocks:
            self.assertIsInstance(shock, Shock)
    
    def test_generate_shock_sequence_with_types(self):
        """Test generating a sequence with specific shock types."""
        shock_types = ["policy_rate_change", "market_crash"]
        shocks = self.generator.generate_shock_sequence(
            num_shocks=3,
            shock_types=shock_types
        )
        
        self.assertEqual(len(shocks), 3)
        for shock in shocks:
            self.assertIn(shock.type, shock_types)
    
    def test_generate_shock_sequence_with_jurisdictions(self):
        """Test generating a sequence with specific jurisdictions."""
        jurisdictions = ["US", "EU"]
        shocks = self.generator.generate_shock_sequence(
            num_shocks=3,
            jurisdictions=jurisdictions
        )
        
        self.assertEqual(len(shocks), 3)
        for shock in shocks:
            self.assertIn(shock.jurisdiction, jurisdictions)
    
    def test_generate_scenario_shocks(self):
        """Test generating scenario shocks."""
        scenarios = ["recession", "tech_regulation", "trade_conflict", "climate_crisis", "pandemic_response"]
        
        for scenario in scenarios:
            shocks = self.generator.generate_scenario_shocks(scenario)
            self.assertIsInstance(shocks, list)
            self.assertGreater(len(shocks), 0)
            for shock in shocks:
                self.assertIsInstance(shock, Shock)
    
    def test_generate_scenario_shocks_invalid(self):
        """Test generating scenario shocks with invalid scenario."""
        with self.assertRaises(ValueError):
            self.generator.generate_scenario_shocks("invalid_scenario")
    
    def test_generate_correlated_shocks(self):
        """Test generating correlated shocks."""
        primary_shock = Shock(
            type="policy_rate_change",
            jurisdiction="US",
            intensity=0.5,
            duration_days=30,
            start_date=datetime.now(),
            confidence=0.8,
            source_refs=["test"]
        )
        
        correlated_shocks = self.generator.generate_correlated_shocks(primary_shock)
        
        self.assertIsInstance(correlated_shocks, list)
        # With low correlation probability, might be empty
        if correlated_shocks:
            for shock in correlated_shocks:
                self.assertIsInstance(shock, Shock)
                self.assertIn(shock.type, ["market_crash", "political_instability"])
    
    def test_validate_shock(self):
        """Test shock validation."""
        # Valid shock
        valid_shock = Shock(
            type="policy_rate_change",
            jurisdiction="US",
            intensity=0.5,
            duration_days=30,
            start_date=datetime.now(),
            confidence=0.8,
            source_refs=["test"]
        )
        self.assertTrue(self.generator.validate_shock(valid_shock))
        
        # Invalid shock - wrong type
        invalid_shock = Shock(
            type="invalid_type",
            jurisdiction="US",
            intensity=0.5,
            duration_days=30,
            start_date=datetime.now(),
            confidence=0.8,
            source_refs=["test"]
        )
        self.assertFalse(self.generator.validate_shock(invalid_shock))
        
        # Invalid shock - intensity out of range
        invalid_shock = Shock(
            type="policy_rate_change",
            jurisdiction="US",
            intensity=1.5,  # > 1.0
            duration_days=30,
            start_date=datetime.now(),
            confidence=0.8,
            source_refs=["test"]
        )
        self.assertFalse(self.generator.validate_shock(invalid_shock))
        
        # Invalid shock - duration < 1
        invalid_shock = Shock(
            type="policy_rate_change",
            jurisdiction="US",
            intensity=0.5,
            duration_days=0,  # < 1
            start_date=datetime.now(),
            confidence=0.8,
            source_refs=["test"]
        )
        self.assertFalse(self.generator.validate_shock(invalid_shock))
        
        # Invalid shock - confidence out of range
        invalid_shock = Shock(
            type="policy_rate_change",
            jurisdiction="US",
            intensity=0.5,
            duration_days=30,
            start_date=datetime.now(),
            confidence=1.5,  # > 1.0
            source_refs=["test"]
        )
        self.assertFalse(self.generator.validate_shock(invalid_shock))
        
        # Invalid shock - jurisdiction not in allowed list
        invalid_shock = Shock(
            type="policy_rate_change",
            jurisdiction="INVALID",  # Not in allowed jurisdictions
            intensity=0.5,
            duration_days=30,
            start_date=datetime.now(),
            confidence=0.8,
            source_refs=["test"]
        )
        self.assertFalse(self.generator.validate_shock(invalid_shock))
    
    def test_get_shock_statistics(self):
        """Test getting shock statistics."""
        shocks = [
            Shock(
                type="policy_rate_change",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date=datetime.now(),
                confidence=0.8,
                source_refs=["test"]
            ),
            Shock(
                type="market_crash",
                jurisdiction="EU",
                intensity=0.7,
                duration_days=60,
                start_date=datetime.now(),
                confidence=0.9,
                source_refs=["test"]
            )
        ]
        
        stats = self.generator.get_shock_statistics(shocks)
        
        self.assertEqual(stats["total_shocks"], 2)
        self.assertEqual(stats["by_type"]["policy_rate_change"], 1)
        self.assertEqual(stats["by_type"]["market_crash"], 1)
        self.assertEqual(stats["by_jurisdiction"]["US"], 1)
        self.assertEqual(stats["by_jurisdiction"]["EU"], 1)
        self.assertAlmostEqual(stats["avg_intensity"], 0.6)
        self.assertAlmostEqual(stats["avg_duration"], 45.0)
        self.assertAlmostEqual(stats["avg_confidence"], 0.85)
    
    def test_get_shock_statistics_empty(self):
        """Test getting shock statistics for empty list."""
        stats = self.generator.get_shock_statistics([])
        
        self.assertEqual(stats["total_shocks"], 0)
        self.assertEqual(stats["avg_intensity"], 0.0)
        self.assertEqual(stats["avg_duration"], 0.0)
        self.assertEqual(stats["avg_confidence"], 0.0)


class TestScenarioParameters(unittest.TestCase):
    """Test ScenarioParameters dataclass."""
    
    def test_scenario_parameters_creation(self):
        """Test creating scenario parameters."""
        params = ScenarioParameters(
            name="Test Scenario",
            description="A test scenario",
            domain_key="venture_capital",
            num_iterations=1000,
            time_horizon_days=365,
            seed=42,
            shock_types=["policy_rate_change"],
            jurisdictions=["US"],
            correlation_probability=0.3
        )
        
        self.assertEqual(params.name, "Test Scenario")
        self.assertEqual(params.description, "A test scenario")
        self.assertEqual(params.domain_key, "venture_capital")
        self.assertEqual(params.num_iterations, 1000)
        self.assertEqual(params.time_horizon_days, 365)
        self.assertEqual(params.seed, 42)
        self.assertEqual(params.shock_types, ["policy_rate_change"])
        self.assertEqual(params.jurisdictions, ["US"])
        self.assertEqual(params.correlation_probability, 0.3)
    
    def test_scenario_parameters_defaults(self):
        """Test scenario parameters with defaults."""
        params = ScenarioParameters(
            name="Test Scenario",
            description="A test scenario",
            domain_key="venture_capital"
        )
        
        self.assertEqual(params.num_iterations, 1000)
        self.assertEqual(params.time_horizon_days, 365)
        self.assertIsNone(params.seed)
        self.assertIsNone(params.shock_types)
        self.assertIsNone(params.jurisdictions)
        self.assertEqual(params.correlation_probability, 0.3)


class TestSimulationResult(unittest.TestCase):
    """Test SimulationResult dataclass."""
    
    def test_simulation_result_creation(self):
        """Test creating simulation result."""
        shocks = [
            Shock(
                type="policy_rate_change",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date=datetime.now(),
                confidence=0.8,
                source_refs=["test"]
            )
        ]
        
        features = {"dry_powder": 0.6, "fund_age_years": 3}
        outcomes = {"portfolio_VaR": 0.1, "downround_prob": 0.2}
        
        result = SimulationResult(
            iteration=1,
            shocks=shocks,
            features=features,
            outcomes=outcomes,
            timestamp=datetime.now()
        )
        
        self.assertEqual(result.iteration, 1)
        self.assertEqual(result.shocks, shocks)
        self.assertEqual(result.features, features)
        self.assertEqual(result.outcomes, outcomes)
        self.assertIsInstance(result.timestamp, datetime)


class TestScenarioResult(unittest.TestCase):
    """Test ScenarioResult dataclass."""
    
    def test_scenario_result_creation(self):
        """Test creating scenario result."""
        results = [
            SimulationResult(
                iteration=1,
                shocks=[],
                features={},
                outcomes={},
                timestamp=datetime.now()
            )
        ]
        
        summary_stats = {"metric": {"mean": 0.5, "std": 0.1}}
        percentiles = {"metric": [0.1, 0.25, 0.5, 0.75, 0.9]}
        
        scenario_result = ScenarioResult(
            scenario_name="Test Scenario",
            domain_key="venture_capital",
            num_iterations=1,
            time_horizon_days=365,
            seed=42,
            results=results,
            summary_stats=summary_stats,
            percentiles=percentiles,
            created_at=datetime.now()
        )
        
        self.assertEqual(scenario_result.scenario_name, "Test Scenario")
        self.assertEqual(scenario_result.domain_key, "venture_capital")
        self.assertEqual(scenario_result.num_iterations, 1)
        self.assertEqual(scenario_result.time_horizon_days, 365)
        self.assertEqual(scenario_result.seed, 42)
        self.assertEqual(scenario_result.results, results)
        self.assertEqual(scenario_result.summary_stats, summary_stats)
        self.assertEqual(scenario_result.percentiles, percentiles)
        self.assertIsInstance(scenario_result.created_at, datetime)


class TestScenarioEngine(unittest.TestCase):
    """Test ScenarioEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = ScenarioEngine(max_workers=1)
    
    def test_scenario_engine_initialization(self):
        """Test scenario engine initialization."""
        self.assertIsInstance(self.engine.shock_generator, ShockGenerator)
        self.assertEqual(self.engine.max_workers, 1)
    
    def test_run_scenario(self):
        """Test running a scenario."""
        params = ScenarioParameters(
            name="Test Scenario",
            description="A test scenario",
            domain_key="venture_capital",
            num_iterations=10,  # Small number for testing
            time_horizon_days=365,
            seed=42
        )
        
        result = self.engine.run_scenario(params)
        
        self.assertIsInstance(result, ScenarioResult)
        self.assertEqual(result.scenario_name, "Test Scenario")
        self.assertEqual(result.domain_key, "venture_capital")
        self.assertEqual(result.num_iterations, 10)
        self.assertEqual(result.time_horizon_days, 365)
        self.assertEqual(result.seed, 42)
        self.assertEqual(len(result.results), 10)
        self.assertIsInstance(result.summary_stats, dict)
        self.assertIsInstance(result.percentiles, dict)
    
    def test_run_scenario_invalid_domain(self):
        """Test running scenario with invalid domain."""
        params = ScenarioParameters(
            name="Test Scenario",
            description="A test scenario",
            domain_key="invalid_domain",
            num_iterations=10,
            time_horizon_days=365
        )
        
        with self.assertRaises(ValueError):
            self.engine.run_scenario(params)
    
    def test_generate_scenario_shocks(self):
        """Test generating scenario shocks."""
        params = ScenarioParameters(
            name="Test Scenario",
            description="A test scenario",
            domain_key="venture_capital",
            shock_types=["policy_rate_change"],
            jurisdictions=["US"]
        )
        
        shocks = self.engine._generate_scenario_shocks(params)
        
        self.assertIsInstance(shocks, list)
        self.assertGreater(len(shocks), 0)
        for shock in shocks:
            self.assertIsInstance(shock, Shock)
            self.assertEqual(shock.type, "policy_rate_change")
            self.assertEqual(shock.jurisdiction, "US")
    
    def test_generate_random_features(self):
        """Test generating random features."""
        domain = VentureCapitalDomain()
        features = self.engine._generate_random_features(domain)
        
        self.assertIsInstance(features, dict)
        self.assertIn("dry_powder", features)
        self.assertIn("fund_age_years", features)
        self.assertIn("dpi", features)
        
        # Check that features are within reasonable ranges
        self.assertGreaterEqual(features["dry_powder"], 0.0)
        self.assertLessEqual(features["dry_powder"], 1.0)
        self.assertGreaterEqual(features["fund_age_years"], 1)
        self.assertGreaterEqual(features["dpi"], 0.0)
    
    def test_calculate_summary_statistics(self):
        """Test calculating summary statistics."""
        results = [
            SimulationResult(
                iteration=1,
                shocks=[],
                features={},
                outcomes={"metric1": 1.0, "metric2": 2.0},
                timestamp=datetime.now()
            ),
            SimulationResult(
                iteration=2,
                shocks=[],
                features={},
                outcomes={"metric1": 3.0, "metric2": 4.0},
                timestamp=datetime.now()
            )
        ]
        
        stats = self.engine._calculate_summary_statistics(results)
        
        self.assertIn("metric1", stats)
        self.assertIn("metric2", stats)
        
        self.assertEqual(stats["metric1"]["mean"], 2.0)
        self.assertEqual(stats["metric1"]["std"], 1.0)
        self.assertEqual(stats["metric1"]["min"], 1.0)
        self.assertEqual(stats["metric1"]["max"], 3.0)
        self.assertEqual(stats["metric1"]["median"], 2.0)
    
    def test_calculate_percentiles(self):
        """Test calculating percentiles."""
        results = [
            SimulationResult(
                iteration=1,
                shocks=[],
                features={},
                outcomes={"metric": 1.0},
                timestamp=datetime.now()
            ),
            SimulationResult(
                iteration=2,
                shocks=[],
                features={},
                outcomes={"metric": 2.0},
                timestamp=datetime.now()
            ),
            SimulationResult(
                iteration=3,
                shocks=[],
                features={},
                outcomes={"metric": 3.0},
                timestamp=datetime.now()
            )
        ]
        
        percentiles = self.engine._calculate_percentiles(results)
        
        self.assertIn("metric", percentiles)
        self.assertEqual(len(percentiles["metric"]), 7)  # 5, 10, 25, 50, 75, 90, 95
    
    def test_compare_scenarios(self):
        """Test comparing scenarios."""
        # Create mock scenario results
        scenario1 = Mock()
        scenario1.scenario_name = "Scenario 1"
        scenario1.summary_stats = {"metric": {"mean": 1.0}}
        
        scenario2 = Mock()
        scenario2.scenario_name = "Scenario 2"
        scenario2.summary_stats = {"metric": {"mean": 2.0}}
        
        comparison = self.engine.compare_scenarios([scenario1, scenario2])
        
        self.assertIn("scenarios", comparison)
        self.assertIn("metrics", comparison)
        self.assertIn("differences", comparison)
        self.assertEqual(comparison["scenarios"], ["Scenario 1", "Scenario 2"])
    
    def test_compare_scenarios_insufficient(self):
        """Test comparing scenarios with insufficient data."""
        scenario1 = Mock()
        scenario1.scenario_name = "Scenario 1"
        scenario1.summary_stats = {"metric": {"mean": 1.0}}
        
        with self.assertRaises(ValueError):
            self.engine.compare_scenarios([scenario1])


class TestDomainResponse(unittest.TestCase):
    """Test DomainResponse dataclass."""
    
    def test_domain_response_creation(self):
        """Test creating domain response."""
        features = {"dry_powder": 0.6, "fund_age_years": 3}
        shocks = [
            Shock(
                type="policy_rate_change",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date=datetime.now(),
                confidence=0.8,
                source_refs=["test"]
            )
        ]
        outcomes = {"portfolio_VaR": 0.1, "downround_prob": 0.2}
        
        response = DomainResponse(
            domain_key="venture_capital",
            features=features,
            shocks=shocks,
            outcomes=outcomes,
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        self.assertEqual(response.domain_key, "venture_capital")
        self.assertEqual(response.features, features)
        self.assertEqual(response.shocks, shocks)
        self.assertEqual(response.outcomes, outcomes)
        self.assertEqual(response.confidence, 0.8)
        self.assertIsInstance(response.timestamp, datetime)


class TestDomainResponseSimulator(unittest.TestCase):
    """Test DomainResponseSimulator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simulator = DomainResponseSimulator()
    
    def test_simulator_initialization(self):
        """Test simulator initialization."""
        self.assertIsInstance(self.simulator.response_models, dict)
        self.assertIn("venture_capital", self.simulator.response_models)
        self.assertIn("saas", self.simulator.response_models)
        self.assertIn("fintech", self.simulator.response_models)
    
    def test_simulate_domain_response(self):
        """Test simulating domain response."""
        features = {"dry_powder": 0.6, "fund_age_years": 3}
        shocks = [
            Shock(
                type="policy_rate_change",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date=datetime.now(),
                confidence=0.8,
                source_refs=["test"]
            )
        ]
        
        response = self.simulator.simulate_domain_response("venture_capital", features, shocks)
        
        self.assertIsInstance(response, DomainResponse)
        self.assertEqual(response.domain_key, "venture_capital")
        self.assertEqual(response.features, features)
        self.assertEqual(response.shocks, shocks)
        self.assertIsInstance(response.outcomes, dict)
        self.assertGreater(response.confidence, 0.0)
        self.assertLessEqual(response.confidence, 1.0)
    
    def test_simulate_domain_response_invalid_domain(self):
        """Test simulating domain response with invalid domain."""
        features = {"dry_powder": 0.6, "fund_age_years": 3}
        shocks = [
            Shock(
                type="policy_rate_change",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date=datetime.now(),
                confidence=0.8,
                source_refs=["test"]
            )
        ]
        
        with self.assertRaises(ValueError):
            self.simulator.simulate_domain_response("invalid_domain", features, shocks)
    
    def test_simulate_multi_domain_response(self):
        """Test simulating multi-domain response."""
        domain_features = {
            "venture_capital": {"dry_powder": 0.6, "fund_age_years": 3},
            "saas": {"arr": 1000000, "gross_churn": 0.05}
        }
        shocks = [
            Shock(
                type="policy_rate_change",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date=datetime.now(),
                confidence=0.8,
                source_refs=["test"]
            )
        ]
        
        responses = self.simulator.simulate_multi_domain_response(domain_features, shocks)
        
        self.assertIsInstance(responses, dict)
        self.assertIn("venture_capital", responses)
        self.assertIn("saas", responses)
        
        for response in responses.values():
            self.assertIsInstance(response, DomainResponse)
    
    def test_analyze_shock_impact(self):
        """Test analyzing shock impact."""
        features = {"dry_powder": 0.6, "fund_age_years": 3}
        shock = Shock(
            type="liquidity_tightening",
            jurisdiction="US",
            intensity=0.5,
            duration_days=30,
            start_date=datetime.now(),
            confidence=0.8,
            source_refs=["test"]
        )
        
        impact = self.simulator.analyze_shock_impact("venture_capital", features, shock)
        
        self.assertIsInstance(impact, dict)
        self.assertIn("portfolio_VaR", impact)
        self.assertIn("downround_prob", impact)
        self.assertIn("follow_on_shortfall", impact)
    
    def test_calculate_risk_metrics(self):
        """Test calculating risk metrics."""
        responses = [
            DomainResponse(
                domain_key="venture_capital",
                features={},
                shocks=[],
                outcomes={"portfolio_VaR": 0.1, "downround_prob": 0.2},
                confidence=0.8,
                timestamp=datetime.now()
            ),
            DomainResponse(
                domain_key="saas",
                features={},
                shocks=[],
                outcomes={"portfolio_VaR": 0.15, "downround_prob": 0.25},
                confidence=0.8,
                timestamp=datetime.now()
            )
        ]
        
        risk_metrics = self.simulator.calculate_risk_metrics(responses)
        
        self.assertIsInstance(risk_metrics, dict)
        self.assertIn("portfolio_VaR_mean", risk_metrics)
        self.assertIn("portfolio_VaR_std", risk_metrics)
        self.assertIn("portfolio_VaR_var_95", risk_metrics)
        self.assertIn("portfolio_VaR_var_99", risk_metrics)
        self.assertIn("portfolio_VaR_max_loss", risk_metrics)
    
    def test_generate_stress_test_scenarios(self):
        """Test generating stress test scenarios."""
        scenarios = self.simulator.generate_stress_test_scenarios("venture_capital", {})
        
        self.assertIsInstance(scenarios, dict)
        self.assertIn("liquidity_crisis", scenarios)
        self.assertIn("severe_recession", scenarios)
        self.assertIn("black_swan", scenarios)
        
        for scenario_name, shocks in scenarios.items():
            self.assertIsInstance(shocks, list)
            for shock in shocks:
                self.assertIsInstance(shock, Shock)
    
    def test_run_stress_tests(self):
        """Test running stress tests."""
        features = {"dry_powder": 0.6, "fund_age_years": 3}
        
        results = self.simulator.run_stress_tests("venture_capital", features)
        
        self.assertIsInstance(results, dict)
        self.assertIn("liquidity_crisis", results)
        self.assertIn("severe_recession", results)
        self.assertIn("black_swan", results)
        
        for scenario_name, response in results.items():
            self.assertIsInstance(response, DomainResponse)
            self.assertEqual(response.domain_key, "venture_capital")
    
    def test_calculate_portfolio_risk(self):
        """Test calculating portfolio risk."""
        portfolio_responses = {
            "venture_capital": DomainResponse(
                domain_key="venture_capital",
                features={},
                shocks=[],
                outcomes={"portfolio_VaR": 0.1},
                confidence=0.8,
                timestamp=datetime.now()
            ),
            "saas": DomainResponse(
                domain_key="saas",
                features={},
                shocks=[],
                outcomes={"portfolio_VaR": 0.15},
                confidence=0.8,
                timestamp=datetime.now()
            )
        }
        
        weights = {"venture_capital": 0.6, "saas": 0.4}
        
        portfolio_metrics = self.simulator.calculate_portfolio_risk(portfolio_responses, weights)
        
        self.assertIsInstance(portfolio_metrics, dict)
        self.assertIn("portfolio_portfolio_VaR_total", portfolio_metrics)
        self.assertIn("portfolio_portfolio_VaR_weighted_avg", portfolio_metrics)
        self.assertIn("portfolio_portfolio_VaR_std", portfolio_metrics)


if __name__ == "__main__":
    unittest.main()








