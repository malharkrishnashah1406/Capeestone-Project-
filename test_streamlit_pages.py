#!/usr/bin/env python3
"""
Test script to verify Streamlit pages are working correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_streamlit_imports():
    """Test that all Streamlit pages can be imported without errors."""
    print("Testing Streamlit page imports...")
    
    try:
        # Test main page
        print("Testing main page...")
        import streamlit_app.main
        print("✓ Main page imported successfully")
        
        # Test individual pages
        pages_dir = Path("streamlit_app/pages")
        for page_file in pages_dir.glob("*.py"):
            if page_file.name != "__init__.py":
                print(f"Testing {page_file.name}...")
                try:
                    # Import the page module
                    module_name = f"streamlit_app.pages.{page_file.stem}"
                    __import__(module_name)
                    print(f"✓ {page_file.name} imported successfully")
                except Exception as e:
                    print(f"✗ {page_file.name} failed: {e}")
                    return False
        
        return True
        
    except Exception as e:
        print(f"Error testing Streamlit pages: {e}")
        return False

def test_domain_integration():
    """Test that domains work with Streamlit pages."""
    print("\nTesting domain integration...")
    
    try:
        from utils.registry import list_domain_keys, get_domain
        
        # Test domain registry
        domain_keys = list_domain_keys()
        print(f"✓ Found {len(domain_keys)} domains")
        
        # Test domain access
        for key in domain_keys:
            domain = get_domain(key)
            print(f"✓ {key}: {domain.name}")
        
        return True
        
    except Exception as e:
        print(f"Error testing domain integration: {e}")
        return False

if __name__ == "__main__":
    print("Running Streamlit page tests...")
    print("=" * 50)
    
    # Test imports
    import_success = test_streamlit_imports()
    
    # Test domain integration
    domain_success = test_domain_integration()
    
    print("\n" + "=" * 50)
    if import_success and domain_success:
        print("🎉 All Streamlit tests passed!")
        print("\nThe dashboard should be accessible at: http://localhost:8501")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


