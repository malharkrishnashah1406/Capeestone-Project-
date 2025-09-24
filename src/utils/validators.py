"""
Validators Module.

This module provides validation utilities for the startup performance
prediction system.
"""

from typing import Any, Dict, List, Optional, Union
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error."""
    pass


def validate_domain_key(domain_key: str) -> bool:
    """
    Validate domain key format.
    
    Args:
        domain_key: Domain key to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(domain_key, str):
        return False
    
    # Domain keys should be lowercase with underscores
    pattern = r'^[a-z_]+$'
    return bool(re.match(pattern, domain_key))


def validate_feature_spec(feature_spec: Dict[str, str]) -> bool:
    """
    Validate feature specification.
    
    Args:
        feature_spec: Feature specification to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(feature_spec, dict):
        return False
    
    for feature_name, feature_desc in feature_spec.items():
        if not isinstance(feature_name, str) or not isinstance(feature_desc, str):
            return False
        
        # Feature names should be valid identifiers
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', feature_name):
            return False
    
    return True


def validate_features(features: Dict[str, Any], feature_spec: Dict[str, str]) -> bool:
    """
    Validate features against feature specification.
    
    Args:
        features: Features to validate
        feature_spec: Feature specification
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(features, dict):
        return False
    
    for feature_name, feature_value in features.items():
        if feature_name not in feature_spec:
            logger.warning(f"Unknown feature: {feature_name}")
            continue
        
        # Basic type validation based on feature description
        feature_desc = feature_spec[feature_name].lower()
        
        if 'float' in feature_desc:
            if not isinstance(feature_value, (int, float)):
                return False
        elif 'int' in feature_desc:
            if not isinstance(feature_value, int):
                return False
        elif 'dict' in feature_desc:
            if not isinstance(feature_value, dict):
                return False
        elif 'list' in feature_desc:
            if not isinstance(feature_value, list):
                return False
        elif 'str' in feature_desc:
            if not isinstance(feature_value, str):
                return False
    
    return True


def validate_shock_data(shock_data: Dict[str, Any]) -> bool:
    """
    Validate shock data.
    
    Args:
        shock_data: Shock data to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['type', 'jurisdiction', 'intensity', 'duration_days']
    
    for field in required_fields:
        if field not in shock_data:
            return False
    
    # Validate field types
    if not isinstance(shock_data['type'], str):
        return False
    
    if not isinstance(shock_data['jurisdiction'], str):
        return False
    
    if not isinstance(shock_data['intensity'], (int, float)):
        return False
    
    if not isinstance(shock_data['duration_days'], int):
        return False
    
    # Validate ranges
    if not (0.0 <= shock_data['intensity'] <= 1.0):
        return False
    
    if shock_data['duration_days'] < 1:
        return False
    
    return True


def validate_portfolio_data(portfolio_data: Dict[str, Any]) -> bool:
    """
    Validate portfolio data.
    
    Args:
        portfolio_data: Portfolio data to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['name', 'holdings']
    
    for field in required_fields:
        if field not in portfolio_data:
            return False
    
    # Validate name
    if not isinstance(portfolio_data['name'], str) or not portfolio_data['name'].strip():
        return False
    
    # Validate holdings
    holdings = portfolio_data['holdings']
    if not isinstance(holdings, list) or len(holdings) == 0:
        return False
    
    total_weight = 0
    for holding in holdings:
        if not isinstance(holding, dict):
            return False
        
        # Validate required holding fields
        if 'domain_key' not in holding or 'weight' not in holding:
            return False
        
        # Validate domain key
        if not validate_domain_key(holding['domain_key']):
            return False
        
        # Validate weight
        weight = holding['weight']
        if not isinstance(weight, (int, float)) or weight < 0:
            return False
        
        total_weight += weight
    
    # Validate total weight
    if abs(total_weight - 1.0) > 0.01:
        return False
    
    return True


def validate_policy_data(policy_data: Dict[str, Any]) -> bool:
    """
    Validate policy data.
    
    Args:
        policy_data: Policy data to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['title', 'body_text', 'jurisdiction', 'policy_type']
    
    for field in required_fields:
        if field not in policy_data:
            return False
    
    # Validate title
    if not isinstance(policy_data['title'], str) or not policy_data['title'].strip():
        return False
    
    # Validate body text
    if not isinstance(policy_data['body_text'], str) or len(policy_data['body_text']) < 10:
        return False
    
    # Validate jurisdiction
    if not isinstance(policy_data['jurisdiction'], str):
        return False
    
    # Validate policy type
    valid_policy_types = ['regulation', 'guidance', 'legislation', 'executive_order', 'circular']
    if policy_data['policy_type'] not in valid_policy_types:
        return False
    
    return True


def validate_scenario_parameters(params: Dict[str, Any]) -> bool:
    """
    Validate scenario parameters.
    
    Args:
        params: Scenario parameters to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['name', 'domain_key', 'num_iterations', 'time_horizon_days']
    
    for field in required_fields:
        if field not in params:
            return False
    
    # Validate name
    if not isinstance(params['name'], str) or not params['name'].strip():
        return False
    
    # Validate domain key
    if not validate_domain_key(params['domain_key']):
        return False
    
    # Validate numeric fields
    if not isinstance(params['num_iterations'], int) or params['num_iterations'] < 1:
        return False
    
    if not isinstance(params['time_horizon_days'], int) or params['time_horizon_days'] < 1:
        return False
    
    # Validate optional fields
    if 'seed' in params and params['seed'] is not None:
        if not isinstance(params['seed'], int):
            return False
    
    if 'correlation_probability' in params:
        prob = params['correlation_probability']
        if not isinstance(prob, (int, float)) or not (0.0 <= prob <= 1.0):
            return False
    
    return True


def validate_date_range(start_date: str, end_date: str) -> bool:
    """
    Validate date range.
    
    Args:
        start_date: Start date string
        end_date: End date string
        
    Returns:
        True if valid, False otherwise
    """
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if start >= end:
            return False
        
        return True
    except (ValueError, TypeError):
        return False


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def validate_json_structure(data: Any, schema: Dict[str, Any]) -> bool:
    """
    Validate JSON structure against schema.
    
    Args:
        data: Data to validate
        schema: Schema definition
        
    Returns:
        True if valid, False otherwise
    """
    def validate_field(value: Any, field_schema: Dict[str, Any]) -> bool:
        field_type = field_schema.get('type')
        required = field_schema.get('required', True)
        
        # Check if field is present
        if value is None:
            return not required
        
        # Type validation
        if field_type == 'string':
            if not isinstance(value, str):
                return False
        elif field_type == 'number':
            if not isinstance(value, (int, float)):
                return False
        elif field_type == 'integer':
            if not isinstance(value, int):
                return False
        elif field_type == 'boolean':
            if not isinstance(value, bool):
                return False
        elif field_type == 'array':
            if not isinstance(value, list):
                return False
            # Validate array items if schema provided
            if 'items' in field_schema:
                for item in value:
                    if not validate_field(item, field_schema['items']):
                        return False
        elif field_type == 'object':
            if not isinstance(value, dict):
                return False
            # Validate object properties if schema provided
            if 'properties' in field_schema:
                for prop_name, prop_schema in field_schema['properties'].items():
                    if prop_name in value:
                        if not validate_field(value[prop_name], prop_schema):
                            return False
        
        # Additional validation
        if 'min' in field_schema and value < field_schema['min']:
            return False
        
        if 'max' in field_schema and value > field_schema['max']:
            return False
        
        if 'pattern' in field_schema:
            if not re.match(field_schema['pattern'], str(value)):
                return False
        
        return True
    
    return validate_field(data, schema)


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize input text.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove null bytes and control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Strip whitespace
    text = text.strip()
    
    return text


def validate_and_sanitize_features(features: Dict[str, Any], 
                                 feature_spec: Dict[str, str]) -> Dict[str, Any]:
    """
    Validate and sanitize features.
    
    Args:
        features: Features to validate and sanitize
        feature_spec: Feature specification
        
    Returns:
        Sanitized features
        
    Raises:
        ValidationError: If validation fails
    """
    if not validate_features(features, feature_spec):
        raise ValidationError("Invalid features")
    
    sanitized_features = {}
    
    for feature_name, feature_value in features.items():
        if feature_name in feature_spec:
            feature_desc = feature_spec[feature_name].lower()
            
            # Sanitize based on type
            if 'str' in feature_desc and isinstance(feature_value, str):
                sanitized_features[feature_name] = sanitize_input(feature_value)
            else:
                sanitized_features[feature_name] = feature_value
    
    return sanitized_features








