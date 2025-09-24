"""
Tests for utils module.
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path
import json
import yaml
from datetime import datetime, timedelta

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from utils.validators import (
    validate_domain_key, validate_feature_spec, validate_features,
    validate_shock_data, validate_portfolio_data, validate_policy_data,
    validate_scenario_parameters, validate_date_range, validate_email,
    validate_url, ValidationError
)
from utils.helpers import (
    generate_unique_id, hash_content, safe_json_serialize, safe_json_deserialize,
    load_yaml_config, save_yaml_config, format_currency, format_percentage,
    format_duration, truncate_text, chunk_list, flatten_list, merge_dicts,
    filter_dict, sort_dict_by_value, get_nested_value, set_nested_value,
    calculate_percentile, calculate_statistics, normalize_value,
    create_date_range, is_business_day, retry, memoize, batch_process
)


class TestValidators(unittest.TestCase):
    """Test validation functions."""
    
    def test_validate_domain_key(self):
        """Test domain key validation."""
        # Valid domain keys
        self.assertTrue(validate_domain_key("venture_capital"))
        self.assertTrue(validate_domain_key("saas"))
        self.assertTrue(validate_domain_key("fintech"))
        self.assertTrue(validate_domain_key("healthtech_biotech"))
        
        # Invalid domain keys
        self.assertFalse(validate_domain_key("Venture Capital"))  # Spaces
        self.assertFalse(validate_domain_key("venture-capital"))  # Hyphens
        self.assertFalse(validate_domain_key("ventureCapital"))   # CamelCase
        self.assertFalse(validate_domain_key("123domain"))        # Starts with number
        self.assertFalse(validate_domain_key(""))                 # Empty
        self.assertFalse(validate_domain_key(None))               # None
        self.assertFalse(validate_domain_key(123))                # Not string
    
    def test_validate_feature_spec(self):
        """Test feature specification validation."""
        # Valid feature spec
        valid_spec = {
            "dry_powder": "float: Available capital ratio (0.0-1.0)",
            "fund_age_years": "int: Fund age in years",
            "dpi": "float: Distributed to Paid-In ratio"
        }
        self.assertTrue(validate_feature_spec(valid_spec))
        
        # Invalid feature spec - not dict
        self.assertFalse(validate_feature_spec([]))
        self.assertFalse(validate_feature_spec("not a dict"))
        
        # Invalid feature spec - invalid keys
        invalid_spec = {
            "invalid-key": "description",  # Hyphen not allowed
            "123feature": "description"    # Starts with number
        }
        self.assertFalse(validate_feature_spec(invalid_spec))
        
        # Invalid feature spec - non-string values
        invalid_spec = {
            "feature": 123  # Should be string
        }
        self.assertFalse(validate_feature_spec(invalid_spec))
    
    def test_validate_features(self):
        """Test features validation against spec."""
        feature_spec = {
            "dry_powder": "float: Available capital ratio (0.0-1.0)",
            "fund_age_years": "int: Fund age in years",
            "dpi": "float: Distributed to Paid-In ratio"
        }
        
        # Valid features
        valid_features = {
            "dry_powder": 0.6,
            "fund_age_years": 3,
            "dpi": 1.2
        }
        self.assertTrue(validate_features(valid_features, feature_spec))
        
        # Invalid features - not dict
        self.assertFalse(validate_features([], feature_spec))
        
        # Invalid features - wrong type
        invalid_features = {
            "dry_powder": "not a float",  # Should be float
            "fund_age_years": 3,
            "dpi": 1.2
        }
        self.assertFalse(validate_features(invalid_features, feature_spec))
    
    def test_validate_shock_data(self):
        """Test shock data validation."""
        # Valid shock data
        valid_shock = {
            "type": "policy_rate_change",
            "jurisdiction": "US",
            "intensity": 0.5,
            "duration_days": 30,
            "start_date": "2024-01-01",
            "confidence": 0.8,
            "source_refs": ["test"],
            "description": "Test shock"
        }
        self.assertTrue(validate_shock_data(valid_shock))
        
        # Invalid shock data - missing required fields
        invalid_shock = {
            "type": "policy_rate_change",
            "jurisdiction": "US"
            # Missing intensity, duration_days, etc.
        }
        self.assertFalse(validate_shock_data(invalid_shock))
        
        # Invalid shock data - wrong types
        invalid_shock = {
            "type": 123,  # Should be string
            "jurisdiction": "US",
            "intensity": "0.5",  # Should be number
            "duration_days": 30,
            "start_date": "2024-01-01",
            "confidence": 0.8,
            "source_refs": ["test"]
        }
        self.assertFalse(validate_shock_data(invalid_shock))
        
        # Invalid shock data - out of range values
        invalid_shock = {
            "type": "policy_rate_change",
            "jurisdiction": "US",
            "intensity": 1.5,  # > 1.0
            "duration_days": 0,  # < 1
            "start_date": "2024-01-01",
            "confidence": 1.5,  # > 1.0
            "source_refs": ["test"]
        }
        self.assertFalse(validate_shock_data(invalid_shock))
    
    def test_validate_portfolio_data(self):
        """Test portfolio data validation."""
        # Valid portfolio data
        valid_portfolio = {
            "name": "Test Portfolio",
            "holdings": [
                {
                    "domain_key": "venture_capital",
                    "weight": 0.6,
                    "features": {"dry_powder": 0.6}
                },
                {
                    "domain_key": "saas",
                    "weight": 0.4,
                    "features": {"arr": 1000000}
                }
            ]
        }
        self.assertTrue(validate_portfolio_data(valid_portfolio))
        
        # Invalid portfolio data - missing required fields
        invalid_portfolio = {
            "name": "Test Portfolio"
            # Missing holdings
        }
        self.assertFalse(validate_portfolio_data(invalid_portfolio))
        
        # Invalid portfolio data - invalid name
        invalid_portfolio = {
            "name": "",  # Empty name
            "holdings": []
        }
        self.assertFalse(validate_portfolio_data(invalid_portfolio))
        
        # Invalid portfolio data - empty holdings
        invalid_portfolio = {
            "name": "Test Portfolio",
            "holdings": []
        }
        self.assertFalse(validate_portfolio_data(invalid_portfolio))
        
        # Invalid portfolio data - invalid domain key
        invalid_portfolio = {
            "name": "Test Portfolio",
            "holdings": [
                {
                    "domain_key": "invalid-domain",  # Invalid domain key
                    "weight": 0.6,
                    "features": {}
                }
            ]
        }
        self.assertFalse(validate_portfolio_data(invalid_portfolio))
        
        # Invalid portfolio data - weights don't sum to 1.0
        invalid_portfolio = {
            "name": "Test Portfolio",
            "holdings": [
                {
                    "domain_key": "venture_capital",
                    "weight": 0.6,
                    "features": {}
                },
                {
                    "domain_key": "saas",
                    "weight": 0.6,  # Total = 1.2 > 1.0
                    "features": {}
                }
            ]
        }
        self.assertFalse(validate_portfolio_data(invalid_portfolio))
    
    def test_validate_policy_data(self):
        """Test policy data validation."""
        # Valid policy data
        valid_policy = {
            "title": "Test Policy",
            "body_text": "This is a test policy with sufficient content for validation.",
            "jurisdiction": "US",
            "policy_type": "regulation"
        }
        self.assertTrue(validate_policy_data(valid_policy))
        
        # Invalid policy data - missing required fields
        invalid_policy = {
            "title": "Test Policy"
            # Missing body_text, jurisdiction, policy_type
        }
        self.assertFalse(validate_policy_data(invalid_policy))
        
        # Invalid policy data - empty title
        invalid_policy = {
            "title": "",
            "body_text": "Test content",
            "jurisdiction": "US",
            "policy_type": "regulation"
        }
        self.assertFalse(validate_policy_data(invalid_policy))
        
        # Invalid policy data - insufficient body text
        invalid_policy = {
            "title": "Test Policy",
            "body_text": "Short",  # < 10 characters
            "jurisdiction": "US",
            "policy_type": "regulation"
        }
        self.assertFalse(validate_policy_data(invalid_policy))
        
        # Invalid policy data - invalid policy type
        invalid_policy = {
            "title": "Test Policy",
            "body_text": "Test content",
            "jurisdiction": "US",
            "policy_type": "invalid_type"  # Not in allowed types
        }
        self.assertFalse(validate_policy_data(invalid_policy))
    
    def test_validate_scenario_parameters(self):
        """Test scenario parameters validation."""
        # Valid scenario parameters
        valid_params = {
            "name": "Test Scenario",
            "domain_key": "venture_capital",
            "num_iterations": 1000,
            "time_horizon_days": 365,
            "seed": 42,
            "correlation_probability": 0.3
        }
        self.assertTrue(validate_scenario_parameters(valid_params))
        
        # Invalid scenario parameters - missing required fields
        invalid_params = {
            "name": "Test Scenario"
            # Missing domain_key, num_iterations, time_horizon_days
        }
        self.assertFalse(validate_scenario_parameters(invalid_params))
        
        # Invalid scenario parameters - invalid domain key
        invalid_params = {
            "name": "Test Scenario",
            "domain_key": "invalid-domain",
            "num_iterations": 1000,
            "time_horizon_days": 365
        }
        self.assertFalse(validate_scenario_parameters(invalid_params))
        
        # Invalid scenario parameters - invalid numeric values
        invalid_params = {
            "name": "Test Scenario",
            "domain_key": "venture_capital",
            "num_iterations": 0,  # < 1
            "time_horizon_days": 365
        }
        self.assertFalse(validate_scenario_parameters(invalid_params))
        
        # Invalid scenario parameters - invalid correlation probability
        invalid_params = {
            "name": "Test Scenario",
            "domain_key": "venture_capital",
            "num_iterations": 1000,
            "time_horizon_days": 365,
            "correlation_probability": 1.5  # > 1.0
        }
        self.assertFalse(validate_scenario_parameters(invalid_params))
    
    def test_validate_date_range(self):
        """Test date range validation."""
        # Valid date range
        self.assertTrue(validate_date_range("2024-01-01", "2024-12-31"))
        self.assertTrue(validate_date_range("2024-01-01T00:00:00Z", "2024-12-31T23:59:59Z"))
        
        # Invalid date range - start >= end
        self.assertFalse(validate_date_range("2024-12-31", "2024-01-01"))
        self.assertFalse(validate_date_range("2024-01-01", "2024-01-01"))
        
        # Invalid date range - invalid date format
        self.assertFalse(validate_date_range("invalid-date", "2024-12-31"))
        self.assertFalse(validate_date_range("2024-01-01", "invalid-date"))
    
    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("user.name@domain.co.uk"))
        self.assertTrue(validate_email("user+tag@example.org"))
        
        # Invalid emails
        self.assertFalse(validate_email("invalid-email"))
        self.assertFalse(validate_email("@example.com"))
        self.assertFalse(validate_email("user@"))
        self.assertFalse(validate_email("user@.com"))
        self.assertFalse(validate_email("user@example"))
    
    def test_validate_url(self):
        """Test URL validation."""
        # Valid URLs
        self.assertTrue(validate_url("https://example.com"))
        self.assertTrue(validate_url("http://www.example.org/path"))
        self.assertTrue(validate_url("https://api.example.com/v1/endpoint"))
        
        # Invalid URLs
        self.assertFalse(validate_url("not-a-url"))
        self.assertFalse(validate_url("ftp://example.com"))  # Unsupported protocol
        self.assertFalse(validate_url("example.com"))  # Missing protocol


class TestHelpers(unittest.TestCase):
    """Test helper functions."""
    
    def test_generate_unique_id(self):
        """Test unique ID generation."""
        id1 = generate_unique_id()
        id2 = generate_unique_id()
        
        self.assertIsInstance(id1, str)
        self.assertIsInstance(id2, str)
        self.assertNotEqual(id1, id2)
        self.assertGreater(len(id1), 0)
    
    def test_hash_content(self):
        """Test content hashing."""
        content1 = "test content"
        content2 = "different content"
        
        hash1 = hash_content(content1)
        hash2 = hash_content(content1)  # Same content
        hash3 = hash_content(content2)  # Different content
        
        self.assertIsInstance(hash1, str)
        self.assertEqual(hash1, hash2)  # Same content should have same hash
        self.assertNotEqual(hash1, hash3)  # Different content should have different hash
    
    def test_safe_json_serialize(self):
        """Test safe JSON serialization."""
        # Test with simple data
        data = {"key": "value", "number": 123}
        json_str = safe_json_serialize(data)
        
        self.assertIsInstance(json_str, str)
        self.assertIn("key", json_str)
        self.assertIn("value", json_str)
        
        # Test with datetime (should be converted to string)
        data_with_datetime = {
            "timestamp": datetime.now(),
            "string": "test"
        }
        json_str = safe_json_serialize(data_with_datetime)
        
        self.assertIsInstance(json_str, str)
        self.assertIn("timestamp", json_str)
        self.assertIn("test", json_str)
        
        # Test with non-serializable data
        data_with_function = {
            "func": lambda x: x,
            "string": "test"
        }
        json_str = safe_json_serialize(data_with_function)
        
        self.assertIsInstance(json_str, str)
        self.assertIn("string", json_str)
    
    def test_safe_json_deserialize(self):
        """Test safe JSON deserialization."""
        # Test with valid JSON
        json_str = '{"key": "value", "number": 123}'
        data = safe_json_deserialize(json_str)
        
        self.assertIsInstance(data, dict)
        self.assertEqual(data["key"], "value")
        self.assertEqual(data["number"], 123)
        
        # Test with invalid JSON
        invalid_json = '{"key": "value", "number": 123'  # Missing closing brace
        data = safe_json_deserialize(invalid_json)
        
        self.assertIsNone(data)
    
    def test_load_yaml_config(self):
        """Test YAML config loading."""
        # Create a temporary YAML file for testing
        test_config = {
            "database": {
                "host": "localhost",
                "port": 5432
            },
            "api": {
                "key": "test_key"
            }
        }
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = yaml.dump(test_config)
            
            config = load_yaml_config("test_config.yaml")
            
            self.assertEqual(config, test_config)
    
    def test_save_yaml_config(self):
        """Test YAML config saving."""
        test_config = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        with patch('builtins.open', create=True) as mock_open:
            save_yaml_config(test_config, "test_config.yaml")
            
            # Verify that open was called
            mock_open.assert_called_once()
    
    def test_format_currency(self):
        """Test currency formatting."""
        # Test USD formatting
        self.assertEqual(format_currency(1234.56, "USD"), "$1,234.56")
        self.assertEqual(format_currency(1000000, "USD"), "$1,000,000.00")
        
        # Test EUR formatting
        self.assertEqual(format_currency(1234.56, "EUR"), "€1,234.56")
        
        # Test with different decimal places
        self.assertEqual(format_currency(1234.567, "USD", decimals=3), "$1,234.567")
    
    def test_format_percentage(self):
        """Test percentage formatting."""
        self.assertEqual(format_percentage(0.1234), "12.34%")
        self.assertEqual(format_percentage(0.5), "50.00%")
        self.assertEqual(format_percentage(1.0), "100.00%")
        
        # Test with different decimal places
        self.assertEqual(format_percentage(0.1234, decimals=1), "12.3%")
    
    def test_format_duration(self):
        """Test duration formatting."""
        # Test seconds
        self.assertEqual(format_duration(30), "30 seconds")
        self.assertEqual(format_duration(90), "1 minute 30 seconds")
        
        # Test minutes
        self.assertEqual(format_duration(3600), "1 hour")
        self.assertEqual(format_duration(3660), "1 hour 1 minute")
        
        # Test hours
        self.assertEqual(format_duration(86400), "1 day")
        self.assertEqual(format_duration(90000), "1 day 1 hour")
    
    def test_truncate_text(self):
        """Test text truncation."""
        text = "This is a long text that needs to be truncated"
        
        # Test truncation
        truncated = truncate_text(text, max_length=20)
        self.assertEqual(len(truncated), 20)
        self.assertTrue(truncated.endswith("..."))
        
        # Test no truncation needed
        truncated = truncate_text(text, max_length=100)
        self.assertEqual(truncated, text)
        
        # Test with custom suffix
        truncated = truncate_text(text, max_length=20, suffix="***")
        self.assertTrue(truncated.endswith("***"))
    
    def test_chunk_list(self):
        """Test list chunking."""
        test_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # Test chunking
        chunks = chunk_list(test_list, chunk_size=3)
        self.assertEqual(len(chunks), 4)
        self.assertEqual(chunks[0], [1, 2, 3])
        self.assertEqual(chunks[1], [4, 5, 6])
        self.assertEqual(chunks[2], [7, 8, 9])
        self.assertEqual(chunks[3], [10])
        
        # Test with chunk size larger than list
        chunks = chunk_list(test_list, chunk_size=20)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], test_list)
    
    def test_flatten_list(self):
        """Test list flattening."""
        nested_list = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
        flattened = flatten_list(nested_list)
        
        self.assertEqual(flattened, [1, 2, 3, 4, 5, 6, 7, 8, 9])
        
        # Test with empty lists
        nested_list = [[], [1, 2], [], [3, 4], []]
        flattened = flatten_list(nested_list)
        
        self.assertEqual(flattened, [1, 2, 3, 4])
    
    def test_merge_dicts(self):
        """Test dictionary merging."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        dict3 = {"d": 5}
        
        # Test merging two dicts
        merged = merge_dicts(dict1, dict2)
        self.assertEqual(merged, {"a": 1, "b": 3, "c": 4})
        
        # Test merging multiple dicts
        merged = merge_dicts(dict1, dict2, dict3)
        self.assertEqual(merged, {"a": 1, "b": 3, "c": 4, "d": 5})
        
        # Test with empty dicts
        merged = merge_dicts({}, dict1, {})
        self.assertEqual(merged, dict1)
    
    def test_filter_dict(self):
        """Test dictionary filtering."""
        test_dict = {"a": 1, "b": 2, "c": 3, "d": 4}
        
        # Test filtering by key
        filtered = filter_dict(test_dict, keys=["a", "c"])
        self.assertEqual(filtered, {"a": 1, "c": 3})
        
        # Test filtering by value
        filtered = filter_dict(test_dict, value_filter=lambda x: x > 2)
        self.assertEqual(filtered, {"c": 3, "d": 4})
        
        # Test filtering by both key and value
        filtered = filter_dict(test_dict, keys=["a", "b", "c"], value_filter=lambda x: x > 1)
        self.assertEqual(filtered, {"b": 2, "c": 3})
    
    def test_sort_dict_by_value(self):
        """Test dictionary sorting by value."""
        test_dict = {"a": 3, "b": 1, "c": 4, "d": 2}
        
        # Test ascending sort
        sorted_dict = sort_dict_by_value(test_dict, reverse=False)
        self.assertEqual(list(sorted_dict.values()), [1, 2, 3, 4])
        
        # Test descending sort
        sorted_dict = sort_dict_by_value(test_dict, reverse=True)
        self.assertEqual(list(sorted_dict.values()), [4, 3, 2, 1])
    
    def test_get_nested_value(self):
        """Test getting nested dictionary values."""
        test_dict = {
            "level1": {
                "level2": {
                    "level3": "value"
                }
            },
            "simple": "simple_value"
        }
        
        # Test getting nested value
        value = get_nested_value(test_dict, ["level1", "level2", "level3"])
        self.assertEqual(value, "value")
        
        # Test getting simple value
        value = get_nested_value(test_dict, ["simple"])
        self.assertEqual(value, "simple_value")
        
        # Test getting non-existent value
        value = get_nested_value(test_dict, ["level1", "nonexistent"])
        self.assertIsNone(value)
        
        # Test with default value
        value = get_nested_value(test_dict, ["level1", "nonexistent"], default="default")
        self.assertEqual(value, "default")
    
    def test_set_nested_value(self):
        """Test setting nested dictionary values."""
        test_dict = {}
        
        # Test setting nested value
        set_nested_value(test_dict, ["level1", "level2", "level3"], "value")
        self.assertEqual(test_dict["level1"]["level2"]["level3"], "value")
        
        # Test setting simple value
        set_nested_value(test_dict, ["simple"], "simple_value")
        self.assertEqual(test_dict["simple"], "simple_value")
        
        # Test overwriting existing value
        set_nested_value(test_dict, ["level1", "level2", "level3"], "new_value")
        self.assertEqual(test_dict["level1"]["level2"]["level3"], "new_value")
    
    def test_calculate_percentile(self):
        """Test percentile calculation."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # Test various percentiles
        self.assertEqual(calculate_percentile(data, 50), 5.5)  # Median
        self.assertEqual(calculate_percentile(data, 25), 3.25)  # Q1
        self.assertEqual(calculate_percentile(data, 75), 7.75)  # Q3
        self.assertEqual(calculate_percentile(data, 90), 9.1)   # 90th percentile
        
        # Test with empty data
        self.assertIsNone(calculate_percentile([], 50))
    
    def test_calculate_statistics(self):
        """Test statistics calculation."""
        data = [1, 2, 3, 4, 5]
        
        stats = calculate_statistics(data)
        
        self.assertEqual(stats["mean"], 3.0)
        self.assertEqual(stats["median"], 3.0)
        self.assertEqual(stats["min"], 1)
        self.assertEqual(stats["max"], 5)
        self.assertAlmostEqual(stats["std"], 1.5811388300841898)
        
        # Test with empty data
        stats = calculate_statistics([])
        self.assertEqual(stats["mean"], 0.0)
        self.assertEqual(stats["median"], 0.0)
        self.assertEqual(stats["min"], 0.0)
        self.assertEqual(stats["max"], 0.0)
        self.assertEqual(stats["std"], 0.0)
    
    def test_normalize_value(self):
        """Test value normalization."""
        # Test min-max normalization
        normalized = normalize_value(5, min_val=0, max_val=10)
        self.assertEqual(normalized, 0.5)
        
        normalized = normalize_value(0, min_val=0, max_val=10)
        self.assertEqual(normalized, 0.0)
        
        normalized = normalize_value(10, min_val=0, max_val=10)
        self.assertEqual(normalized, 1.0)
        
        # Test with custom range
        normalized = normalize_value(5, min_val=0, max_val=10, new_min=0, new_max=100)
        self.assertEqual(normalized, 50.0)
    
    def test_create_date_range(self):
        """Test date range creation."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 5)
        
        date_range = create_date_range(start_date, end_date)
        
        self.assertEqual(len(date_range), 5)
        self.assertEqual(date_range[0], datetime(2024, 1, 1))
        self.assertEqual(date_range[4], datetime(2024, 1, 5))
        
        # Test with step
        date_range = create_date_range(start_date, end_date, step_days=2)
        self.assertEqual(len(date_range), 3)
        self.assertEqual(date_range[0], datetime(2024, 1, 1))
        self.assertEqual(date_range[1], datetime(2024, 1, 3))
        self.assertEqual(date_range[2], datetime(2024, 1, 5))
    
    def test_is_business_day(self):
        """Test business day checking."""
        # Test Monday (business day)
        monday = datetime(2024, 1, 1)  # Monday
        self.assertTrue(is_business_day(monday))
        
        # Test Saturday (not business day)
        saturday = datetime(2024, 1, 6)  # Saturday
        self.assertFalse(is_business_day(saturday))
        
        # Test Sunday (not business day)
        sunday = datetime(2024, 1, 7)  # Sunday
        self.assertFalse(is_business_day(sunday))
    
    def test_retry_decorator(self):
        """Test retry decorator."""
        call_count = 0
        
        @retry(max_attempts=3, delay=0.1)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = failing_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)
    
    def test_memoize_decorator(self):
        """Test memoize decorator."""
        call_count = 0
        
        @memoize
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call
        result1 = expensive_function(1, 2)
        self.assertEqual(result1, 3)
        self.assertEqual(call_count, 1)
        
        # Second call with same arguments (should use cache)
        result2 = expensive_function(1, 2)
        self.assertEqual(result2, 3)
        self.assertEqual(call_count, 1)  # Should not increment
        
        # Third call with different arguments
        result3 = expensive_function(2, 3)
        self.assertEqual(result3, 5)
        self.assertEqual(call_count, 2)  # Should increment
    
    def test_batch_process(self):
        """Test batch processing."""
        def process_item(item):
            return item * 2
        
        items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # Test batch processing
        results = list(batch_process(items, process_item, batch_size=3))
        
        self.assertEqual(len(results), 10)
        self.assertEqual(results, [2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
        
        # Test with empty items
        results = list(batch_process([], process_item, batch_size=3))
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()








