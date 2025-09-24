"""
Domains package initialization.

This module registers all available domains with the global registry.
"""

from .base import registry
from .venture_capital import VentureCapitalDomain
from .saas import SaaSDomain
from .fintech import FinTechDomain
from .healthtech_biotech import HealthTechBiotechDomain
from .greentech import GreenTechDomain
from .accelerators import AcceleratorsDomain
from .cross_border import CrossBorderDomain
from .public_sector_funded import PublicSectorFundedDomain
from .mediatech_politicaltech import MediaTechPoliticalTechDomain

# Register all domains
registry.register(VentureCapitalDomain())
registry.register(SaaSDomain())
registry.register(FinTechDomain())
registry.register(HealthTechBiotechDomain())
registry.register(GreenTechDomain())
registry.register(AcceleratorsDomain())
registry.register(CrossBorderDomain())
registry.register(PublicSectorFundedDomain())
registry.register(MediaTechPoliticalTechDomain())

__all__ = [
    'VentureCapitalDomain',
    'SaaSDomain', 
    'FinTechDomain',
    'HealthTechBiotechDomain',
    'GreenTechDomain',
    'AcceleratorsDomain',
    'CrossBorderDomain',
    'PublicSectorFundedDomain',
    'MediaTechPoliticalTechDomain'
]