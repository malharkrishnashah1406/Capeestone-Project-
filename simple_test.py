#!/usr/bin/env python3
"""
Simple test to verify basic functionality of the startup performance prediction system.
"""

import sys
import os
from pathlib import Path

# Add current directory and src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(src_dir))

# Debug: Print current Python path
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}...")

def test_domains():
    """Test basic domain functionality."""
    print("Testing domains...")
    try:
        from domains.venture_capital import VentureCapitalDomain
        from domains.saas import SaaSDomain
        from domains.fintech import FinTechDomain
        
        # Test VentureCapitalDomain
        vc_domain = VentureCapitalDomain()
        print(f"  ✓ VentureCapitalDomain: {vc_domain.key}")
        
        # Test SaaSDomain
        saas_domain = SaaSDomain()
        print(f"  ✓ SaaSDomain: {saas_domain.key}")
        
        # Test FinTechDomain
        fintech_domain = FinTechDomain()
        print(f"  ✓ FinTechDomain: {fintech_domain.key}")
        
        return True
    except Exception as e:
        print(f"  ✗ Domain test failed: {e}")
        return False

def test_simulation():
    """Test basic simulation functionality."""
    print("Testing simulation...")
    try:
        # First test if numpy is available
        import numpy as np
        print(f"  ✓ NumPy imported: {np.__version__}")
        
        from src.simulation.shocks import Shock, ShockGenerator
        
        # Test Shock
        shock = Shock(
            type="policy_rate_change",
            jurisdiction="US",
            intensity=0.5,
            duration_days=30,
            start_date="2024-01-01",
            confidence=0.8,
            source_refs=["test"]
        )
        print(f"  ✓ Shock created: {shock.type}")
        
        # Test ShockGenerator
        generator = ShockGenerator()
        random_shock = generator.generate_random_shock()
        print(f"  ✓ Random shock generated: {random_shock.type}")
        
        return True
    except Exception as e:
        print(f"  ✗ Simulation test failed: {e}")
        return False

def test_utils():
    """Test basic utils functionality."""
    print("Testing utils...")
    try:
        # First test if yaml is available
        import yaml
        print(f"  ✓ PyYAML imported: {yaml.__version__}")
        
        from utils.validators import validate_domain_key
        from utils.helpers import generate_id, hash_content
        
        # Test validators
        is_valid = validate_domain_key("venture_capital")
        print(f"  ✓ Domain key validation: {is_valid}")
        
        # Test helpers
        unique_id = generate_id()
        print(f"  ✓ Unique ID generated: {unique_id}")
        
        content_hash = hash_content("test content")
        print(f"  ✓ Content hashed: {content_hash}")
        
        return True
    except Exception as e:
        print(f"  ✗ Utils test failed: {e}")
        return False

def test_api():
    """Test basic API functionality."""
    print("Testing API...")
    try:
        # First test if fastapi is available
        import fastapi
        print(f"  ✓ FastAPI imported: {fastapi.__version__}")
        
        from src.api.server import app
        
        # Test that app can be created
        print(f"  ✓ FastAPI app created: {app.title}")
        
        return True
    except Exception as e:
        print(f"  ✗ API test failed: {e}")
        return False

def main():
    """Run all simple tests."""
    print("Running simple tests...")
    print("=" * 40)
    
    results = []
    
    # Test domains
    results.append(test_domains())
    print()
    
    # Test simulation
    results.append(test_simulation())
    print()
    
    # Test utils
    results.append(test_utils())
    print()
    
    # Test API
    results.append(test_api())
    print()
    
    # Summary
    print("=" * 40)
    print("Test Summary:")
    print(f"  Domains: {'✓ PASSED' if results[0] else '✗ FAILED'}")
    print(f"  Simulation: {'✓ PASSED' if results[1] else '✗ FAILED'}")
    print(f"  Utils: {'✓ PASSED' if results[2] else '✗ FAILED'}")
    print(f"  API: {'✓ PASSED' if results[3] else '✗ FAILED'}")
    
    if all(results):
        print("\n🎉 All simple tests passed!")
        return 0
    else:
        print("\n❌ Some simple tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
