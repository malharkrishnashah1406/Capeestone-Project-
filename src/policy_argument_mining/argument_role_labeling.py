"""
Argument Role Labeling Module.

This module classifies the role of arguments (claim/premise/attack/support)
in policy debates and discussions.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .ingestion import DebateSegment
from .claim_detection import Claim
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class ArgumentRole:
    """Represents the role of an argument in a debate."""
    role: str  # claim, premise, attack, support, rebut
    confidence: float
    evidence_text: str
    source_segment: DebateSegment


class ArgumentRoleLabeler:
    """Labels the role of arguments in policy debates."""
    
    def __init__(self):
        self.claim_indicators = [
            r'\b(claim|assert|argue|believe|think|know|prove|demonstrate)\b',
            r'\b(fact|truth|reality|certainly|definitely|clearly)\b',
            r'\b(conclude|conclusion|therefore|thus|hence)\b',
        ]
        
        self.premise_indicators = [
            r'\b(because|since|as|due to|given that|considering)\b',
            r'\b(evidence|data|study|research|analysis|report)\b',
            r'\b(example|instance|case|illustration)\b',
            r'\b(statistics|numbers|figures|results)\b',
        ]
        
        self.attack_indicators = [
            r'\b(but|however|nevertheless|nonetheless|yet|still)\b',
            r'\b(disagree|dispute|challenge|question|doubt)\b',
            r'\b(wrong|incorrect|false|mistaken|erroneous)\b',
            r'\b(flaw|problem|issue|concern|weakness)\b',
        ]
        
        self.support_indicators = [
            r'\b(agree|support|endorse|back|favor|approve)\b',
            r'\b(also|additionally|furthermore|moreover|besides)\b',
            r'\b(similarly|likewise|in the same way|correspondingly)\b',
            r'\b(confirm|verify|validate|corroborate)\b',
        ]
        
        self.rebut_indicators = [
            r'\b(rebut|refute|counter|respond|reply|answer)\b',
            r'\b(although|while|whereas|despite|in spite of)\b',
            r'\b(on the other hand|conversely|in contrast)\b',
            r'\b(nevertheless|nonetheless|however|but)\b',
        ]
    
    def label_argument_roles(self, segment: DebateSegment) -> List[ArgumentRole]:
        """
        Label argument roles in a debate segment.
        
        Args:
            segment: Debate segment to analyze
            
        Returns:
            List of argument roles
        """
        roles = []
        
        # Split into sentences
        sentences = self._split_sentences(segment.text)
        
        for sentence in sentences:
            role = self._classify_sentence_role(sentence, segment)
            if role:
                roles.append(role)
        
        return roles
    
    def label_claim_roles(self, claims: List[Claim]) -> List[ArgumentRole]:
        """
        Label roles for claims.
        
        Args:
            claims: List of claims to analyze
            
        Returns:
            List of argument roles
        """
        roles = []
        
        for claim in claims:
            role = self._classify_claim_role(claim)
            if role:
                roles.append(role)
        
        return roles
    
    def _classify_sentence_role(self, sentence: str, segment: DebateSegment) -> Optional[ArgumentRole]:
        """
        Classify the role of a sentence.
        
        Args:
            sentence: Sentence to classify
            segment: Source segment
            
        Returns:
            ArgumentRole if classified, None otherwise
        """
        text_lower = sentence.lower()
        
        # Calculate role scores
        claim_score = self._calculate_role_score(text_lower, self.claim_indicators)
        premise_score = self._calculate_role_score(text_lower, self.premise_indicators)
        attack_score = self._calculate_role_score(text_lower, self.attack_indicators)
        support_score = self._calculate_role_score(text_lower, self.support_indicators)
        rebut_score = self._calculate_role_score(text_lower, self.rebut_indicators)
        
        # Find the highest scoring role
        scores = {
            'claim': claim_score,
            'premise': premise_score,
            'attack': attack_score,
            'support': support_score,
            'rebut': rebut_score
        }
        
        best_role = max(scores, key=scores.get)
        best_score = scores[best_role]
        
        if best_score > 0.2:  # Threshold for role detection
            return ArgumentRole(
                role=best_role,
                confidence=best_score,
                evidence_text=sentence,
                source_segment=segment
            )
        
        return None
    
    def _classify_claim_role(self, claim: Claim) -> Optional[ArgumentRole]:
        """
        Classify the role of a claim.
        
        Args:
            claim: Claim to classify
            
        Returns:
            ArgumentRole if classified, None otherwise
        """
        text_lower = claim.text.lower()
        
        # Calculate role scores
        claim_score = self._calculate_role_score(text_lower, self.claim_indicators)
        premise_score = self._calculate_role_score(text_lower, self.premise_indicators)
        attack_score = self._calculate_role_score(text_lower, self.attack_indicators)
        support_score = self._calculate_role_score(text_lower, self.support_indicators)
        rebut_score = self._calculate_role_score(text_lower, self.rebut_indicators)
        
        # Find the highest scoring role
        scores = {
            'claim': claim_score,
            'premise': premise_score,
            'attack': attack_score,
            'support': support_score,
            'rebut': rebut_score
        }
        
        best_role = max(scores, key=scores.get)
        best_score = scores[best_role] * claim.confidence  # Weight by claim confidence
        
        if best_score > 0.15:  # Lower threshold for claims
            return ArgumentRole(
                role=best_role,
                confidence=best_score,
                evidence_text=claim.text,
                source_segment=claim.source_segment
            )
        
        return None
    
    def _calculate_role_score(self, text: str, indicators: List[str]) -> float:
        """
        Calculate role score based on indicators.
        
        Args:
            text: Text to analyze
            indicators: List of indicator patterns
            
        Returns:
            Role score between 0 and 1
        """
        score = 0.0
        
        for pattern in indicators:
            matches = re.findall(pattern, text, re.IGNORECASE)
            score += len(matches) * 0.2
        
        return min(1.0, score)
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def validate_argument_role(self, role: ArgumentRole) -> bool:
        """
        Validate an argument role.
        
        Args:
            role: Argument role to validate
            
        Returns:
            True if valid, False otherwise
        """
        valid_roles = ['claim', 'premise', 'attack', 'support', 'rebut']
        
        if role.role not in valid_roles:
            return False
        
        if role.confidence < 0.1 or role.confidence > 1.0:
            return False
        
        if not role.evidence_text:
            return False
        
        return True
    
    def get_role_distribution(self, roles: List[ArgumentRole]) -> Dict[str, int]:
        """
        Get distribution of argument roles.
        
        Args:
            roles: List of argument roles
            
        Returns:
            Dictionary mapping roles to counts
        """
        distribution = {
            'claim': 0,
            'premise': 0,
            'attack': 0,
            'support': 0,
            'rebut': 0
        }
        
        for role in roles:
            if role.role in distribution:
                distribution[role.role] += 1
        
        return distribution























