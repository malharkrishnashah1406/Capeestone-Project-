"""
Entity Linking Module.

This module links mentions in policy documents to organizations, policies,
jurisdictions, and external identifiers.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from .ingestion import DebateSegment
from .claim_detection import Claim
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents a linked entity."""
    entity_id: str
    entity_type: str  # organization, policy, jurisdiction, person
    name: str
    confidence: float
    source_text: str
    external_id: Optional[str] = None


@dataclass
class EntityMention:
    """Represents a mention of an entity in text."""
    text: str
    entity_type: str
    start_pos: int
    end_pos: int
    confidence: float
    source_segment: DebateSegment


class EntityLinker:
    """Links entity mentions to known entities and external identifiers."""
    
    def __init__(self):
        # Known organizations (stub data)
        self.known_organizations = {
            'federal reserve': {'id': 'org_fed', 'type': 'organization', 'external_id': 'FED'},
            'sec': {'id': 'org_sec', 'type': 'organization', 'external_id': 'SEC'},
            'fda': {'id': 'org_fda', 'type': 'organization', 'external_id': 'FDA'},
            'epa': {'id': 'org_epa', 'type': 'organization', 'external_id': 'EPA'},
            'congress': {'id': 'org_congress', 'type': 'organization', 'external_id': 'CONGRESS'},
            'senate': {'id': 'org_senate', 'type': 'organization', 'external_id': 'SENATE'},
            'house': {'id': 'org_house', 'type': 'organization', 'external_id': 'HOUSE'},
        }
        
        # Known jurisdictions
        self.known_jurisdictions = {
            'united states': {'id': 'jur_us', 'type': 'jurisdiction', 'external_id': 'US'},
            'california': {'id': 'jur_ca', 'type': 'jurisdiction', 'external_id': 'CA'},
            'new york': {'id': 'jur_ny', 'type': 'jurisdiction', 'external_id': 'NY'},
            'texas': {'id': 'jur_tx', 'type': 'jurisdiction', 'external_id': 'TX'},
            'florida': {'id': 'jur_fl', 'type': 'jurisdiction', 'external_id': 'FL'},
        }
        
        # Entity patterns
        self.entity_patterns = {
            'organization': [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Corporation|Corp|Inc|LLC|Ltd|Company|Co))\b',
                r'\b([A-Z]{2,}(?:\s+[A-Z]{2,})*)\b',  # Acronyms
                r'\b(Federal\s+Reserve|SEC|FDA|EPA|Congress|Senate|House)\b',
            ],
            'policy': [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Act|Bill|Law|Regulation|Policy))\b',
                r'\b(Act\s+\d+|Bill\s+\d+|Law\s+\d+)\b',
            ],
            'jurisdiction': [
                r'\b(United\s+States|California|New\s+York|Texas|Florida)\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:State|County|City))\b',
            ],
            'person': [
                r'\b(Mr\.|Mrs\.|Ms\.|Dr\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # Simple name pattern
            ]
        }
    
    def extract_entities(self, segment: DebateSegment) -> List[EntityMention]:
        """
        Extract entity mentions from a debate segment.
        
        Args:
            segment: Debate segment to analyze
            
        Returns:
            List of entity mentions
        """
        mentions = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, segment.text, re.IGNORECASE)
                for match in matches:
                    mention = EntityMention(
                        text=match.group(),
                        entity_type=entity_type,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.7,  # Base confidence
                        source_segment=segment
                    )
                    mentions.append(mention)
        
        return mentions
    
    def link_entities(self, mentions: List[EntityMention]) -> List[Entity]:
        """
        Link entity mentions to known entities.
        
        Args:
            mentions: List of entity mentions
            
        Returns:
            List of linked entities
        """
        entities = []
        
        for mention in mentions:
            entity = self._link_mention(mention)
            if entity:
                entities.append(entity)
        
        return entities
    
    def _link_mention(self, mention: EntityMention) -> Optional[Entity]:
        """
        Link a single mention to a known entity.
        
        Args:
            mention: Entity mention to link
            
        Returns:
            Linked entity if found, None otherwise
        """
        text_lower = mention.text.lower()
        
        # Check organizations
        if mention.entity_type == 'organization':
            for org_name, org_data in self.known_organizations.items():
                if org_name in text_lower or text_lower in org_name:
                    return Entity(
                        entity_id=org_data['id'],
                        entity_type=org_data['type'],
                        name=mention.text,
                        confidence=mention.confidence,
                        source_text=mention.text,
                        external_id=org_data['external_id']
                    )
        
        # Check jurisdictions
        elif mention.entity_type == 'jurisdiction':
            for jur_name, jur_data in self.known_jurisdictions.items():
                if jur_name in text_lower or text_lower in jur_name:
                    return Entity(
                        entity_id=jur_data['id'],
                        entity_type=jur_data['type'],
                        name=mention.text,
                        confidence=mention.confidence,
                        source_text=mention.text,
                        external_id=jur_data['external_id']
                    )
        
        # For other types, create generic entities
        else:
            entity_id = f"{mention.entity_type}_{hash(mention.text) % 10000}"
            return Entity(
                entity_id=entity_id,
                entity_type=mention.entity_type,
                name=mention.text,
                confidence=mention.confidence * 0.5,  # Lower confidence for unlinked entities
                source_text=mention.text
            )
        
        return None
    
    def extract_entities_from_claims(self, claims: List[Claim]) -> List[Entity]:
        """
        Extract entities from claims.
        
        Args:
            claims: List of claims to analyze
            
        Returns:
            List of entities
        """
        all_entities = []
        
        for claim in claims:
            # Extract mentions from claim text
            mentions = self._extract_mentions_from_text(claim.text, claim.source_segment)
            
            # Link mentions to entities
            entities = self.link_entities(mentions)
            
            # Weight confidence by claim confidence
            for entity in entities:
                entity.confidence *= claim.confidence
            
            all_entities.extend(entities)
        
        return all_entities
    
    def _extract_mentions_from_text(self, text: str, segment: DebateSegment) -> List[EntityMention]:
        """
        Extract entity mentions from text.
        
        Args:
            text: Text to analyze
            segment: Source segment
            
        Returns:
            List of entity mentions
        """
        mentions = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    mention = EntityMention(
                        text=match.group(),
                        entity_type=entity_type,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.7,
                        source_segment=segment
                    )
                    mentions.append(mention)
        
        return mentions
    
    def get_entity_statistics(self, entities: List[Entity]) -> Dict[str, Any]:
        """
        Get statistics about entities.
        
        Args:
            entities: List of entities
            
        Returns:
            Dictionary with entity statistics
        """
        stats = {
            'total_entities': len(entities),
            'by_type': {},
            'by_confidence': {
                'high': 0,    # > 0.8
                'medium': 0,  # 0.5-0.8
                'low': 0      # < 0.5
            }
        }
        
        for entity in entities:
            # Count by type
            if entity.entity_type not in stats['by_type']:
                stats['by_type'][entity.entity_type] = 0
            stats['by_type'][entity.entity_type] += 1
            
            # Count by confidence
            if entity.confidence > 0.8:
                stats['by_confidence']['high'] += 1
            elif entity.confidence > 0.5:
                stats['by_confidence']['medium'] += 1
            else:
                stats['by_confidence']['low'] += 1
        
        return stats
    
    def validate_entity(self, entity: Entity) -> bool:
        """
        Validate a linked entity.
        
        Args:
            entity: Entity to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not entity.entity_id or not entity.name:
            return False
        
        if entity.confidence < 0.1 or entity.confidence > 1.0:
            return False
        
        valid_types = ['organization', 'policy', 'jurisdiction', 'person']
        if entity.entity_type not in valid_types:
            return False
        
        return True
    
    def get_entity_relationships(self, entities: List[Entity]) -> Dict[str, List[str]]:
        """
        Get relationships between entities.
        
        Args:
            entities: List of entities
            
        Returns:
            Dictionary mapping entity IDs to related entity IDs
        """
        relationships = {}
        
        # Simple relationship detection based on co-occurrence
        for i, entity1 in enumerate(entities):
            if entity1.entity_id not in relationships:
                relationships[entity1.entity_id] = []
            
            for j, entity2 in enumerate(entities):
                if i != j:
                    # Check if entities are from the same segment
                    if hasattr(entity1, 'source_segment') and hasattr(entity2, 'source_segment'):
                        if entity1.source_segment == entity2.source_segment:
                            relationships[entity1.entity_id].append(entity2.entity_id)
        
        return relationships























