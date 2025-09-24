#!/usr/bin/env python3
"""
Test runner script for the startup performance prediction system.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_domain_tests():
    """Run domain tests."""
    print("Running domain tests...")
    try:
        from tests.test_domains import (
            TestBaseDomain, TestVentureCapitalDomain, TestSaaSDomain, 
            TestFinTechDomain, TestHealthTechBiotechDomain, TestGreenTechDomain,
            TestRegTechPolicyDomain, TestCrossBorderDomain, TestPublicSectorFundedDomain,
            TestMediaTechPoliticalTechDomain, TestAcceleratorsDomain, TestDomainRegistry,
            TestRegistryUtils
        )
        
        # Test BaseDomain
        print("  Testing BaseDomain...")
        test_base = TestBaseDomain()
        test_base.test_base_domain_abstract()
        test_base.test_shock_dataclass()
        test_base.test_event_dataclass()
        print("  ✓ BaseDomain tests passed")
        
        # Test VentureCapitalDomain
        print("  Testing VentureCapitalDomain...")
        test_vc = TestVentureCapitalDomain()
        test_vc.setUp()
        test_vc.test_domain_key()
        test_vc.test_domain_name()
        test_vc.test_feature_spec()
        test_vc.test_extract_features()
        test_vc.test_risk_factors()
        test_vc.test_reporting_metrics()
        test_vc.test_simulate_response()
        print("  ✓ VentureCapitalDomain tests passed")
        
        # Test SaaSDomain
        print("  Testing SaaSDomain...")
        test_saas = TestSaaSDomain()
        test_saas.setUp()
        test_saas.test_domain_key()
        test_saas.test_feature_spec()
        test_saas.test_simulate_response()
        print("  ✓ SaaSDomain tests passed")
        
        # Test FinTechDomain
        print("  Testing FinTechDomain...")
        test_fintech = TestFinTechDomain()
        test_fintech.setUp()
        test_fintech.test_domain_key()
        test_fintech.test_feature_spec()
        test_fintech.test_simulate_response()
        print("  ✓ FinTechDomain tests passed")
        
        print("✓ All domain tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Domain tests failed: {e}")
        return False

def run_simulation_tests():
    """Run simulation tests."""
    print("Running simulation tests...")
    try:
        from tests.test_simulation import (
            TestShock, TestShockGenerator, TestScenarioParameters, 
            TestSimulationResult, TestScenarioResult, TestScenarioEngine,
            TestDomainResponse, TestDomainResponseSimulator
        )
        
        # Test Shock
        print("  Testing Shock...")
        test_shock = TestShock()
        test_shock.test_shock_creation()
        test_shock.test_shock_default_description()
        print("  ✓ Shock tests passed")
        
        # Test ShockGenerator
        print("  Testing ShockGenerator...")
        test_generator = TestShockGenerator()
        test_generator.setUp()
        test_generator.test_shock_types()
        test_generator.test_generate_random_shock()
        test_generator.test_generate_shock_sequence()
        test_generator.test_validate_shock()
        print("  ✓ ShockGenerator tests passed")
        
        # Test ScenarioEngine
        print("  Testing ScenarioEngine...")
        test_engine = TestScenarioEngine()
        test_engine.setUp()
        test_engine.test_scenario_engine_initialization()
        test_engine.test_generate_random_features()
        print("  ✓ ScenarioEngine tests passed")
        
        print("✓ All simulation tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Simulation tests failed: {e}")
        return False

def run_utils_tests():
    """Run utils tests."""
    print("Running utils tests...")
    try:
        from tests.test_utils import TestValidators, TestHelpers
        
        # Test Validators
        print("  Testing Validators...")
        test_validators = TestValidators()
        test_validators.test_validate_domain_key()
        test_validators.test_validate_feature_spec()
        test_validators.test_validate_features()
        test_validators.test_validate_shock_data()
        test_validators.test_validate_portfolio_data()
        test_validators.test_validate_policy_data()
        test_validators.test_validate_scenario_parameters()
        test_validators.test_validate_date_range()
        test_validators.test_validate_email()
        test_validators.test_validate_url()
        print("  ✓ Validators tests passed")
        
        # Test Helpers
        print("  Testing Helpers...")
        test_helpers = TestHelpers()
        test_helpers.test_generate_unique_id()
        test_helpers.test_hash_content()
        test_helpers.test_safe_json_serialize()
        test_helpers.test_safe_json_deserialize()
        test_helpers.test_format_currency()
        test_helpers.test_format_percentage()
        test_helpers.test_format_duration()
        test_helpers.test_truncate_text()
        test_helpers.test_chunk_list()
        test_helpers.test_flatten_list()
        test_helpers.test_merge_dicts()
        test_helpers.test_filter_dict()
        test_helpers.test_sort_dict_by_value()
        test_helpers.test_get_nested_value()
        test_helpers.test_set_nested_value()
        test_helpers.test_calculate_percentile()
        test_helpers.test_calculate_statistics()
        test_helpers.test_normalize_value()
        test_helpers.test_create_date_range()
        test_helpers.test_is_business_day()
        test_helpers.test_retry_decorator()
        test_helpers.test_memoize_decorator()
        test_helpers.test_batch_process()
        print("  ✓ Helpers tests passed")
        
        print("✓ All utils tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Utils tests failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Starting test suite...")
    print("=" * 50)
    
    results = []
    
    # Run domain tests
    results.append(run_domain_tests())
    print()
    
    # Run simulation tests
    results.append(run_simulation_tests())
    print()
    
    # Run utils tests
    results.append(run_utils_tests())
    print()
    
    # Summary
    print("=" * 50)
    print("Test Summary:")
    print(f"  Domain tests: {'✓ PASSED' if results[0] else '✗ FAILED'}")
    print(f"  Simulation tests: {'✓ PASSED' if results[1] else '✗ FAILED'}")
    print(f"  Utils tests: {'✓ PASSED' if results[2] else '✗ FAILED'}")
    
    if all(results):
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
