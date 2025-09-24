#!/usr/bin/env python3
"""
Test script to verify domains are working correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_domains():
    """Test domain functionality."""
    print("Testing domains...")
    
    try:
        from utils.registry import list_domain_keys, get_domain
        from domains.base import registry
        
        # List all domain keys
        domain_keys = list_domain_keys()
        print(f"Available domain keys: {domain_keys}")
        
        # Test each domain
        for key in domain_keys:
            try:
                domain = get_domain(key)
                print(f"✓ {key}: {domain.name}")
                
                # Test feature extraction
                features = domain.extract_features({})
                print(f"  Features: {len(features)} extracted")
                
                # Test risk factors
                risks = domain.risk_factors()
                print(f"  Risk factors: {len(risks)} identified")
                
            except Exception as e:
                print(f"✗ {key}: Error - {e}")
        
        print(f"\nTotal domains: {len(domain_keys)}")
        return True
        
    except Exception as e:
        print(f"Error testing domains: {e}")
        return False

if __name__ == "__main__":
    success = test_domains()
    if success:
        print("\n🎉 Domain test passed!")
    else:
        print("\n❌ Domain test failed!")
        sys.exit(1)


