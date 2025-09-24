"""
Registry Module.

This module provides a registry for managing domain implementations
and other system components.
"""

from typing import Dict, List, Any, Optional, Type
import logging
from domains.base import BaseDomain, registry as domain_registry

logger = logging.getLogger(__name__)


def get_domain(domain_key: str) -> BaseDomain:
    """
    Get a domain by key.
    
    Args:
        domain_key: Domain key identifier
        
    Returns:
        Domain instance
        
    Raises:
        KeyError: If domain not found
    """
    return domain_registry.get(domain_key)


def list_domains() -> List[BaseDomain]:
    """
    List all registered domains.
    
    Returns:
        List of domain instances
    """
    return domain_registry.list_all()


def list_domain_keys() -> List[str]:
    """
    List all registered domain keys.
    
    Returns:
        List of domain keys
    """
    return domain_registry.list_keys()


def get_domain_info(domain_key: str) -> Optional[Dict[str, Any]]:
    """
    Get domain information.
    
    Args:
        domain_key: Domain key identifier
        
    Returns:
        Domain information dictionary or None if not found
    """
    try:
        domain = get_domain(domain_key)
        return domain.to_dict()
    except KeyError:
        return None


def get_all_domain_info() -> List[Dict[str, Any]]:
    """
    Get information for all domains.
    
    Returns:
        List of domain information dictionaries
    """
    domains = list_domains()
    return [domain.to_dict() for domain in domains]


def register_domain(domain: BaseDomain) -> None:
    """
    Register a domain.
    
    Args:
        domain: Domain instance to register
    """
    domain_registry.register(domain)
    logger.info(f"Registered domain: {domain.key}")


def is_domain_registered(domain_key: str) -> bool:
    """
    Check if a domain is registered.
    
    Args:
        domain_key: Domain key identifier
        
    Returns:
        True if registered, False otherwise
    """
    return domain_key in domain_registry.list_keys()


def get_domain_count() -> int:
    """
    Get the number of registered domains.
    
    Returns:
        Number of registered domains
    """
    return len(domain_registry.list_keys())


def get_domain_summary() -> Dict[str, Any]:
    """
    Get a summary of all domains.
    
    Returns:
        Summary dictionary
    """
    domains = list_domains()
    
    summary = {
        "total_domains": len(domains),
        "domain_keys": [domain.key for domain in domains],
        "domain_names": [domain.name for domain in domains],
        "categories": {}
    }
    
    # Group domains by category (if we had categories)
    for domain in domains:
        # For now, just use the domain key as category
        category = domain.key.split('_')[0] if '_' in domain.key else 'general'
        if category not in summary["categories"]:
            summary["categories"][category] = []
        summary["categories"][category].append(domain.key)
    
    return summary