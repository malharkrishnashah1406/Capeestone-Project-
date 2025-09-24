"""
Tests for domains module.
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from domains.base import BaseDomain, Shock, Event, DomainRegistry
from domains.venture_capital import VentureCapitalDomain
from domains.saas import SaaSDomain
from domains.fintech import FinTechDomain
from domains.healthtech_biotech import HealthTechBiotechDomain
from domains.greentech import GreenTechDomain
from domains.regtech_policy import RegTechPolicyDomain
from domains.cross_border import CrossBorderDomain
from domains.public_sector_funded import PublicSectorFundedDomain
from domains.mediatech_politicaltech import MediaTechPoliticalTechDomain
from domains.accelerators import AcceleratorsDomain
from utils.registry import get_domain, list_domains, list_domain_keys, get_all_domain_info


class TestBaseDomain(unittest.TestCase):
    """Test BaseDomain abstract class."""
    
    def test_base_domain_abstract(self):
        """Test that BaseDomain cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            BaseDomain()
    
    def test_shock_dataclass(self):
        """Test Shock dataclass."""
        shock = Shock(
            type="policy_rate_change",
            jurisdiction="US",
            intensity=0.5,
            duration_days=30,
            start_date="2024-01-01",
            confidence=0.8,
            source_refs=["test"],
            description="Test shock"
        )
        
        self.assertEqual(shock.type, "policy_rate_change")
        self.assertEqual(shock.jurisdiction, "US")
        self.assertEqual(shock.intensity, 0.5)
        self.assertEqual(shock.duration_days, 30)
        self.assertEqual(shock.confidence, 0.8)
    
    def test_event_dataclass(self):
        """Test Event dataclass."""
        event = Event(
            type="policy_change",
            source="test",
            timestamp="2024-01-01",
            confidence=0.8,
            impact_score=0.6,
            description="Test event"
        )
        
        self.assertEqual(event.type, "policy_change")
        self.assertEqual(event.source, "test")
        self.assertEqual(event.confidence, 0.8)
        self.assertEqual(event.impact_score, 0.6)


class TestVentureCapitalDomain(unittest.TestCase):
    """Test VentureCapitalDomain."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.domain = VentureCapitalDomain()
    
    def test_domain_key(self):
        """Test domain key."""
        self.assertEqual(self.domain.domain_key(), "venture_capital")
    
    def test_domain_name(self):
        """Test domain name."""
        self.assertEqual(self.domain.domain_name(), "Venture Capital & Private Equity")
    
    def test_feature_spec(self):
        """Test feature specification."""
        feature_spec = self.domain.feature_spec()
        
        self.assertIsInstance(feature_spec, dict)
        self.assertIn("dry_powder", feature_spec)
        self.assertIn("fund_age_years", feature_spec)
        self.assertIn("dpi", feature_spec)
        self.assertIn("tvpi", feature_spec)
        self.assertIn("irr", feature_spec)
    
    def test_extract_features(self):
        """Test feature extraction."""
        input_data = {
            "dry_powder": 0.6,
            "fund_age_years": 3,
            "dpi": 1.2,
            "tvpi": 1.8,
            "irr": 0.15
        }
        
        features = self.domain.extract_features(input_data)
        
        self.assertIsInstance(features, dict)
        self.assertEqual(features["dry_powder"], 0.6)
        self.assertEqual(features["fund_age_years"], 3)
    
    def test_risk_factors(self):
        """Test risk factors."""
        risk_factors = self.domain.risk_factors()
        
        self.assertIsInstance(risk_factors, list)
        self.assertIn("liquidity_tightening", risk_factors)
        self.assertIn("rate_hikes", risk_factors)
        self.assertIn("exit_window_closure", risk_factors)
    
    def test_reporting_metrics(self):
        """Test reporting metrics."""
        metrics = self.domain.reporting_metrics()
        
        self.assertIsInstance(metrics, list)
        self.assertIn("portfolio_VaR", metrics)
        self.assertIn("downround_prob", metrics)
        self.assertIn("follow_on_shortfall", metrics)
    
    def test_simulate_response(self):
        """Test simulation response."""
        features = {
            "dry_powder": 0.6,
            "fund_age_years": 3,
            "dpi": 1.2
        }
        
        shocks = [
            Shock(
                type="policy_rate_change",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date="2024-01-01",
                confidence=0.8,
                source_refs=["test"]
            )
        ]
        
        outcomes = self.domain.simulate_response(features, shocks)
        
        self.assertIsInstance(outcomes, dict)
        self.assertIn("portfolio_VaR", outcomes)
        self.assertIn("downround_prob", outcomes)
        self.assertIn("follow_on_shortfall", outcomes)


class TestSaaSDomain(unittest.TestCase):
    """Test SaaSDomain."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.domain = SaaSDomain()
    
    def test_domain_key(self):
        """Test domain key."""
        self.assertEqual(self.domain.domain_key(), "saas")
    
    def test_feature_spec(self):
        """Test feature specification."""
        feature_spec = self.domain.feature_spec()
        
        self.assertIsInstance(feature_spec, dict)
        self.assertIn("arr", feature_spec)
        self.assertIn("gross_churn", feature_spec)
        self.assertIn("ltv_cac_ratio", feature_spec)
    
    def test_simulate_response(self):
        """Test simulation response."""
        features = {
            "arr": 1000000,
            "gross_churn": 0.05,
            "ltv_cac_ratio": 3.0
        }
        
        shocks = [
            Shock(
                type="competitor_mega_round",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date="2024-01-01",
                confidence=0.8,
                source_refs=["test"]
            )
        ]
        
        outcomes = self.domain.simulate_response(features, shocks)
        
        self.assertIsInstance(outcomes, dict)
        self.assertIn("arr_growth_delta", outcomes)
        self.assertIn("churn_delta", outcomes)
        self.assertIn("runway_change", outcomes)


class TestFinTechDomain(unittest.TestCase):
    """Test FinTechDomain."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.domain = FinTechDomain()
    
    def test_domain_key(self):
        """Test domain key."""
        self.assertEqual(self.domain.domain_key(), "fintech")
    
    def test_feature_spec(self):
        """Test feature specification."""
        feature_spec = self.domain.feature_spec()
        
        self.assertIsInstance(feature_spec, dict)
        self.assertIn("tpv", feature_spec)
        self.assertIn("fraud_rate", feature_spec)
        self.assertIn("interchange_yield", feature_spec)
    
    def test_simulate_response(self):
        """Test simulation response."""
        features = {
            "tpv": 10000000,
            "fraud_rate": 0.02,
            "interchange_yield": 0.03
        }
        
        shocks = [
            Shock(
                type="policy_rate_change",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date="2024-01-01",
                confidence=0.8,
                source_refs=["test"]
            )
        ]
        
        outcomes = self.domain.simulate_response(features, shocks)
        
        self.assertIsInstance(outcomes, dict)
        self.assertIn("tpv_growth_delta", outcomes)
        self.assertIn("loss_rate_delta", outcomes)
        self.assertIn("unit_econ_delta", outcomes)


class TestHealthTechBiotechDomain(unittest.TestCase):
    """Test HealthTechBiotechDomain."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.domain = HealthTechBiotechDomain()
    
    def test_domain_key(self):
        """Test domain key."""
        self.assertEqual(self.domain.domain_key(), "healthtech_biotech")
    
    def test_feature_spec(self):
        """Test feature specification."""
        feature_spec = self.domain.feature_spec()
        
        self.assertIsInstance(feature_spec, dict)
        self.assertIn("trial_phase", feature_spec)
        self.assertIn("rd_burn", feature_spec)
        self.assertIn("regulatory_stage", feature_spec)
    
    def test_simulate_response(self):
        """Test simulation response."""
        features = {
            "trial_phase": 2,
            "rd_burn": 500000,
            "regulatory_stage": 2
        }
        
        shocks = [
            Shock(
                type="approval_crl",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date="2024-01-01",
                confidence=0.8,
                source_refs=["test"]
            )
        ]
        
        outcomes = self.domain.simulate_response(features, shocks)
        
        self.assertIsInstance(outcomes, dict)
        self.assertIn("prob_approval_delta", outcomes)
        self.assertIn("cash_runway_months", outcomes)
        self.assertIn("valuation_sensitivity", outcomes)


class TestGreenTechDomain(unittest.TestCase):
    """Test GreenTechDomain."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.domain = GreenTechDomain()
    
    def test_domain_key(self):
        """Test domain key."""
        self.assertEqual(self.domain.domain_key(), "greentech")
    
    def test_feature_spec(self):
        """Test feature specification."""
        feature_spec = self.domain.feature_spec()
        
        self.assertIsInstance(feature_spec, dict)
        self.assertIn("carbon_price_exposure", feature_spec)
        self.assertIn("capex_intensity", feature_spec)
        self.assertIn("ppa_coverage_ratio", feature_spec)
    
    def test_simulate_response(self):
        """Test simulation response."""
        features = {
            "carbon_price_exposure": 0.3,
            "capex_intensity": 0.6,
            "ppa_coverage_ratio": 0.7
        }
        
        shocks = [
            Shock(
                type="esg_regulation_shifts",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date="2024-01-01",
                confidence=0.8,
                source_refs=["test"]
            )
        ]
        
        outcomes = self.domain.simulate_response(features, shocks)
        
        self.assertIsInstance(outcomes, dict)
        self.assertIn("irr_delta", outcomes)
        self.assertIn("capex_overrun_risk", outcomes)
        self.assertIn("credit_risk_shift", outcomes)


class TestRegTechPolicyDomain(unittest.TestCase):
    """Test RegTechPolicyDomain."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.domain = RegTechPolicyDomain()
    
    def test_domain_key(self):
        """Test domain key."""
        self.assertEqual(self.domain.domain_key(), "regtech_policy")
    
    def test_feature_spec(self):
        """Test feature specification."""
        feature_spec = self.domain.feature_spec()
        
        self.assertIsInstance(feature_spec, dict)
        self.assertIn("regulatory_compliance_score", feature_spec)
        self.assertIn("policy_advocacy_budget", feature_spec)
        self.assertIn("stakeholder_network_size", feature_spec)
    
    def test_simulate_response(self):
        """Test simulation response."""
        features = {
            "regulatory_compliance_score": 0.8,
            "policy_advocacy_budget": 100000,
            "stakeholder_network_size": 50
        }
        
        shocks = [
            Shock(
                type="regulatory_change",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date="2024-01-01",
                confidence=0.8,
                source_refs=["test"]
            )
        ]
        
        outcomes = self.domain.simulate_response(features, shocks)
        
        self.assertIsInstance(outcomes, dict)
        self.assertIn("compliance_cost_delta", outcomes)
        self.assertIn("advocacy_effectiveness", outcomes)
        self.assertIn("policy_influence_score", outcomes)


class TestCrossBorderDomain(unittest.TestCase):
    """Test CrossBorderDomain."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.domain = CrossBorderDomain()
    
    def test_domain_key(self):
        """Test domain key."""
        self.assertEqual(self.domain.domain_key(), "cross_border")
    
    def test_feature_spec(self):
        """Test feature specification."""
        feature_spec = self.domain.feature_spec()
        
        self.assertIsInstance(feature_spec, dict)
        self.assertIn("geographic_diversification", feature_spec)
        self.assertIn("currency_exposure", feature_spec)
        self.assertIn("regulatory_complexity", feature_spec)
    
    def test_simulate_response(self):
        """Test simulation response."""
        features = {
            "geographic_diversification": 0.7,
            "currency_exposure": 0.4,
            "regulatory_complexity": 0.6
        }
        
        shocks = [
            Shock(
                type="trade_war",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date="2024-01-01",
                confidence=0.8,
                source_refs=["test"]
            )
        ]
        
        outcomes = self.domain.simulate_response(features, shocks)
        
        self.assertIsInstance(outcomes, dict)
        self.assertIn("market_access_risk", outcomes)
        self.assertIn("currency_volatility", outcomes)
        self.assertIn("regulatory_fragmentation", outcomes)


class TestPublicSectorFundedDomain(unittest.TestCase):
    """Test PublicSectorFundedDomain."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.domain = PublicSectorFundedDomain()
    
    def test_domain_key(self):
        """Test domain key."""
        self.assertEqual(self.domain.domain_key(), "public_sector_funded")
    
    def test_feature_spec(self):
        """Test feature specification."""
        feature_spec = self.domain.feature_spec()
        
        self.assertIsInstance(feature_spec, dict)
        self.assertIn("government_funding_ratio", feature_spec)
        self.assertIn("policy_alignment_score", feature_spec)
        self.assertIn("bureaucratic_complexity", feature_spec)
    
    def test_simulate_response(self):
        """Test simulation response."""
        features = {
            "government_funding_ratio": 0.6,
            "policy_alignment_score": 0.8,
            "bureaucratic_complexity": 0.5
        }
        
        shocks = [
            Shock(
                type="political_instability",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date="2024-01-01",
                confidence=0.8,
                source_refs=["test"]
            )
        ]
        
        outcomes = self.domain.simulate_response(features, shocks)
        
        self.assertIsInstance(outcomes, dict)
        self.assertIn("funding_continuity_risk", outcomes)
        self.assertIn("policy_shift_impact", outcomes)
        self.assertIn("bureaucratic_delay_risk", outcomes)


class TestMediaTechPoliticalTechDomain(unittest.TestCase):
    """Test MediaTechPoliticalTechDomain."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.domain = MediaTechPoliticalTechDomain()
    
    def test_domain_key(self):
        """Test domain key."""
        self.assertEqual(self.domain.domain_key(), "mediatech_politicaltech")
    
    def test_feature_spec(self):
        """Test feature specification."""
        feature_spec = self.domain.feature_spec()
        
        self.assertIsInstance(feature_spec, dict)
        self.assertIn("content_moderation_scale", feature_spec)
        self.assertIn("political_sensitivity", feature_spec)
        self.assertIn("user_engagement_metrics", feature_spec)
    
    def test_simulate_response(self):
        """Test simulation response."""
        features = {
            "content_moderation_scale": 0.7,
            "political_sensitivity": 0.6,
            "user_engagement_metrics": 0.8
        }
        
        shocks = [
            Shock(
                type="regulatory_change",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date="2024-01-01",
                confidence=0.8,
                source_refs=["test"]
            )
        ]
        
        outcomes = self.domain.simulate_response(features, shocks)
        
        self.assertIsInstance(outcomes, dict)
        self.assertIn("content_risk_score", outcomes)
        self.assertIn("regulatory_compliance_cost", outcomes)
        self.assertIn("user_trust_impact", outcomes)


class TestAcceleratorsDomain(unittest.TestCase):
    """Test AcceleratorsDomain."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.domain = AcceleratorsDomain()
    
    def test_domain_key(self):
        """Test domain key."""
        self.assertEqual(self.domain.domain_key(), "accelerators")
    
    def test_feature_spec(self):
        """Test feature specification."""
        feature_spec = self.domain.feature_spec()
        
        self.assertIsInstance(feature_spec, dict)
        self.assertIn("cohort_size", feature_spec)
        self.assertIn("success_rate", feature_spec)
        self.assertIn("network_strength", feature_spec)
    
    def test_simulate_response(self):
        """Test simulation response."""
        features = {
            "cohort_size": 20,
            "success_rate": 0.3,
            "network_strength": 0.7
        }
        
        shocks = [
            Shock(
                type="market_crash",
                jurisdiction="US",
                intensity=0.5,
                duration_days=30,
                start_date="2024-01-01",
                confidence=0.8,
                source_refs=["test"]
            )
        ]
        
        outcomes = self.domain.simulate_response(features, shocks)
        
        self.assertIsInstance(outcomes, dict)
        self.assertIn("cohort_success_impact", outcomes)
        self.assertIn("funding_availability", outcomes)
        self.assertIn("network_value_delta", outcomes)


class TestDomainRegistry(unittest.TestCase):
    """Test DomainRegistry."""
    
    def test_registry_singleton(self):
        """Test that registry is a singleton."""
        registry1 = DomainRegistry()
        registry2 = DomainRegistry()
        
        self.assertIs(registry1, registry2)
    
    def test_register_and_get_domain(self):
        """Test registering and getting domains."""
        registry = DomainRegistry()
        
        # Create a mock domain
        mock_domain = Mock()
        mock_domain.domain_key.return_value = "test_domain"
        mock_domain.domain_name.return_value = "Test Domain"
        
        # Register domain
        registry.register_domain(mock_domain)
        
        # Get domain
        retrieved_domain = registry.get_domain("test_domain")
        self.assertIs(retrieved_domain, mock_domain)
    
    def test_get_nonexistent_domain(self):
        """Test getting a non-existent domain."""
        registry = DomainRegistry()
        
        with self.assertRaises(KeyError):
            registry.get_domain("nonexistent_domain")
    
    def test_list_domains(self):
        """Test listing all domains."""
        registry = DomainRegistry()
        
        # Clear registry for test
        registry._domains.clear()
        
        # Create mock domains
        mock_domain1 = Mock()
        mock_domain1.domain_key.return_value = "domain1"
        mock_domain1.domain_name.return_value = "Domain 1"
        
        mock_domain2 = Mock()
        mock_domain2.domain_key.return_value = "domain2"
        mock_domain2.domain_name.return_value = "Domain 2"
        
        # Register domains
        registry.register_domain(mock_domain1)
        registry.register_domain(mock_domain2)
        
        # List domains
        domains = registry.list_domains()
        
        self.assertEqual(len(domains), 2)
        self.assertIn("domain1", domains)
        self.assertIn("domain2", domains)


class TestRegistryUtils(unittest.TestCase):
    """Test registry utility functions."""
    
    def test_get_domain(self):
        """Test get_domain utility function."""
        # Test with existing domain
        domain = get_domain("venture_capital")
        self.assertIsInstance(domain, VentureCapitalDomain)
        
        # Test with non-existent domain
        with self.assertRaises(KeyError):
            get_domain("nonexistent_domain")
    
    def test_list_domains(self):
        """Test list_domains utility function."""
        domains = list_domains()
        
        self.assertIsInstance(domains, dict)
        self.assertIn("venture_capital", domains)
        self.assertIn("saas", domains)
        self.assertIn("fintech", domains)
    
    def test_list_domain_keys(self):
        """Test list_domain_keys utility function."""
        keys = list_domain_keys()
        
        self.assertIsInstance(keys, list)
        self.assertIn("venture_capital", keys)
        self.assertIn("saas", keys)
        self.assertIn("fintech", keys)
    
    def test_get_all_domain_info(self):
        """Test get_all_domain_info utility function."""
        info = get_all_domain_info()
        
        self.assertIsInstance(info, list)
        
        for domain_info in info:
            self.assertIn("key", domain_info)
            self.assertIn("name", domain_info)
            self.assertIn("description", domain_info)


if __name__ == "__main__":
    unittest.main()








