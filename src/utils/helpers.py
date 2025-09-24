"""
Helpers Module.

This module provides helper utilities for the startup performance
prediction system.
"""

from typing import Any, Dict, List, Optional, Union, Tuple
import json
import hashlib
import uuid
from datetime import datetime, timedelta
import logging
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


def generate_id(prefix: str = "id") -> str:
    """
    Generate a unique ID.
    
    Args:
        prefix: ID prefix
        
    Returns:
        Unique ID string
    """
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def hash_content(content: str) -> str:
    """
    Generate hash for content.
    
    Args:
        content: Content to hash
        
    Returns:
        Hash string
    """
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def safe_json_dumps(obj: Any, default: Any = None) -> str:
    """
    Safely serialize object to JSON.
    
    Args:
        obj: Object to serialize
        default: Default value for non-serializable objects
        
    Returns:
        JSON string
    """
    try:
        return json.dumps(obj, default=default or str)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to serialize object to JSON: {e}")
        return json.dumps({"error": "Serialization failed", "object_type": str(type(obj))})


def safe_json_loads(json_str: str) -> Any:
    """
    Safely deserialize JSON string.
    
    Args:
        json_str: JSON string to deserialize
        
    Returns:
        Deserialized object or None if failed
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to deserialize JSON: {e}")
        return None


def load_yaml_config(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load YAML configuration file.
    
    Args:
        file_path: Path to YAML file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in {file_path}: {e}")


def save_yaml_config(config: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """
    Save configuration to YAML file.
    
    Args:
        config: Configuration dictionary
        file_path: Path to save YAML file
        
    Raises:
        IOError: If file cannot be written
    """
    file_path = Path(file_path)
    
    try:
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
    except IOError as e:
        raise IOError(f"Failed to save configuration to {file_path}: {e}")


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount.
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "INR": "₹"
    }
    
    symbol = currency_symbols.get(currency, currency)
    
    if currency == "JPY":
        return f"{symbol}{amount:,.0f}"
    else:
        return f"{symbol}{amount:,.2f}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format percentage value.
    
    Args:
        value: Value to format (0.0 to 1.0)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    percentage = value * 100
    return f"{percentage:.{decimal_places}f}%"


def format_duration(days: int) -> str:
    """
    Format duration in days to human readable string.
    
    Args:
        days: Number of days
        
    Returns:
        Formatted duration string
    """
    if days < 1:
        return "Less than 1 day"
    elif days == 1:
        return "1 day"
    elif days < 7:
        return f"{days} days"
    elif days < 30:
        weeks = days // 7
        remaining_days = days % 7
        if remaining_days == 0:
            return f"{weeks} week{'s' if weeks > 1 else ''}"
        else:
            return f"{weeks} week{'s' if weeks > 1 else ''}, {remaining_days} day{'s' if remaining_days > 1 else ''}"
    elif days < 365:
        months = days // 30
        remaining_days = days % 30
        if remaining_days == 0:
            return f"{months} month{'s' if months > 1 else ''}"
        else:
            return f"{months} month{'s' if months > 1 else ''}, {remaining_days} day{'s' if remaining_days > 1 else ''}"
    else:
        years = days // 365
        remaining_days = days % 365
        if remaining_days == 0:
            return f"{years} year{'s' if years > 1 else ''}"
        else:
            return f"{years} year{'s' if years > 1 else ''}, {remaining_days} day{'s' if remaining_days > 1 else ''}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(nested_list: List[Any]) -> List[Any]:
    """
    Flatten nested list.
    
    Args:
        nested_list: Nested list to flatten
        
    Returns:
        Flattened list
    """
    flattened = []
    for item in nested_list:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))
        else:
            flattened.append(item)
    return flattened


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any], 
                overwrite: bool = True) -> Dict[str, Any]:
    """
    Merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        overwrite: Whether to overwrite existing keys
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key not in result or overwrite:
            result[key] = value
        elif isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value, overwrite)
    
    return result


def get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Get nested value from dictionary using dot notation.
    
    Args:
        data: Dictionary to search
        path: Dot-separated path (e.g., "user.profile.name")
        default: Default value if path not found
        
    Returns:
        Value at path or default
    """
    keys = path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def set_nested_value(data: Dict[str, Any], path: str, value: Any) -> None:
    """
    Set nested value in dictionary using dot notation.
    
    Args:
        data: Dictionary to modify
        path: Dot-separated path (e.g., "user.profile.name")
        value: Value to set
    """
    keys = path.split('.')
    current = data
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value


def filter_dict(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    Filter dictionary to include only specified keys.
    
    Args:
        data: Dictionary to filter
        keys: Keys to include
        
    Returns:
        Filtered dictionary
    """
    return {key: data[key] for key in keys if key in data}


def exclude_dict_keys(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    Filter dictionary to exclude specified keys.
    
    Args:
        data: Dictionary to filter
        keys: Keys to exclude
        
    Returns:
        Filtered dictionary
    """
    return {key: value for key, value in data.items() if key not in keys}


def sort_dict_by_value(data: Dict[str, Any], reverse: bool = False) -> Dict[str, Any]:
    """
    Sort dictionary by values.
    
    Args:
        data: Dictionary to sort
        reverse: Whether to sort in reverse order
        
    Returns:
        Sorted dictionary
    """
    return dict(sorted(data.items(), key=lambda x: x[1], reverse=reverse))


def sort_dict_by_key(data: Dict[str, Any], reverse: bool = False) -> Dict[str, Any]:
    """
    Sort dictionary by keys.
    
    Args:
        data: Dictionary to sort
        reverse: Whether to sort in reverse order
        
    Returns:
        Sorted dictionary
    """
    return dict(sorted(data.items(), key=lambda x: x[0], reverse=reverse))


def calculate_percentile(values: List[float], percentile: float) -> float:
    """
    Calculate percentile of values.
    
    Args:
        values: List of values
        percentile: Percentile to calculate (0-100)
        
    Returns:
        Percentile value
    """
    if not values:
        return 0.0
    
    sorted_values = sorted(values)
    index = (percentile / 100) * (len(sorted_values) - 1)
    
    if index.is_integer():
        return sorted_values[int(index)]
    else:
        lower_index = int(index)
        upper_index = lower_index + 1
        weight = index - lower_index
        return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """
    Calculate basic statistics for values.
    
    Args:
        values: List of values
        
    Returns:
        Dictionary with statistics
    """
    if not values:
        return {
            'count': 0,
            'mean': 0.0,
            'std': 0.0,
            'min': 0.0,
            'max': 0.0,
            'median': 0.0,
            'q25': 0.0,
            'q75': 0.0
        }
    
    sorted_values = sorted(values)
    count = len(values)
    mean = sum(values) / count
    
    # Calculate standard deviation
    variance = sum((x - mean) ** 2 for x in values) / count
    std = variance ** 0.5
    
    # Calculate percentiles
    median = calculate_percentile(values, 50)
    q25 = calculate_percentile(values, 25)
    q75 = calculate_percentile(values, 75)
    
    return {
        'count': count,
        'mean': mean,
        'std': std,
        'min': min(values),
        'max': max(values),
        'median': median,
        'q25': q25,
        'q75': q75
    }


def normalize_values(values: List[float], method: str = 'min_max') -> List[float]:
    """
    Normalize values using specified method.
    
    Args:
        values: List of values to normalize
        method: Normalization method ('min_max', 'z_score', 'decimal')
        
    Returns:
        List of normalized values
    """
    if not values:
        return []
    
    if method == 'min_max':
        min_val = min(values)
        max_val = max(values)
        if max_val == min_val:
            return [0.5] * len(values)
        return [(x - min_val) / (max_val - min_val) for x in values]
    
    elif method == 'z_score':
        mean_val = sum(values) / len(values)
        std_val = (sum((x - mean_val) ** 2 for x in values) / len(values)) ** 0.5
        if std_val == 0:
            return [0.0] * len(values)
        return [(x - mean_val) / std_val for x in values]
    
    elif method == 'decimal':
        max_abs = max(abs(x) for x in values)
        if max_abs == 0:
            return [0.0] * len(values)
        return [x / max_abs for x in values]
    
    else:
        raise ValueError(f"Unknown normalization method: {method}")


def create_date_range(start_date: datetime, end_date: datetime, 
                     interval_days: int = 1) -> List[datetime]:
    """
    Create list of dates between start and end date.
    
    Args:
        start_date: Start date
        end_date: End date
        interval_days: Interval between dates in days
        
    Returns:
        List of dates
    """
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=interval_days)
    
    return dates


def is_business_day(date: datetime) -> bool:
    """
    Check if date is a business day (Monday-Friday).
    
    Args:
        date: Date to check
        
    Returns:
        True if business day, False otherwise
    """
    return date.weekday() < 5  # Monday = 0, Friday = 4


def get_business_days(start_date: datetime, end_date: datetime) -> List[datetime]:
    """
    Get list of business days between start and end date.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        List of business days
    """
    all_dates = create_date_range(start_date, end_date)
    return [date for date in all_dates if is_business_day(date)]


def retry_on_exception(func, max_retries: int = 3, delay: float = 1.0, 
                      exceptions: Tuple = (Exception,)):
    """
    Decorator to retry function on exception.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch
        
    Returns:
        Decorated function
    """
    import time
    
    def wrapper(*args, **kwargs):
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                if attempt < max_retries:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {max_retries + 1} attempts failed. Last error: {e}")
        
        raise last_exception
    
    return wrapper


def memoize(func):
    """
    Simple memoization decorator.
    
    Args:
        func: Function to memoize
        
    Returns:
        Memoized function
    """
    cache = {}
    
    def wrapper(*args, **kwargs):
        # Create cache key from arguments
        key = str(args) + str(sorted(kwargs.items()))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        
        return cache[key]
    
    return wrapper


def batch_process(items: List[Any], batch_size: int, 
                  processor_func, *args, **kwargs) -> List[Any]:
    """
    Process items in batches.
    
    Args:
        items: List of items to process
        batch_size: Size of each batch
        processor_func: Function to process each batch
        *args: Additional arguments for processor function
        **kwargs: Additional keyword arguments for processor function
        
    Returns:
        List of results
    """
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = processor_func(batch, *args, **kwargs)
        results.extend(batch_results)
    
    return results








