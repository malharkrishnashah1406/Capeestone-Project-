"""
Stance Detection Module.

This module detects stances (support/oppose/neutral) towards policy targets
in debate segments and claims.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .ingestion import DebateSegment
from .claim_detection import Claim
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class Stance:
    """Represents a detected stance towards a target."""
    stance_label: str  # support, oppose, neutral
    stance_target: str  # Policy, bill, regulation, etc.
    confidence: float
    evidence_text: str
    source_segment: DebateSegment


class StanceDetector:
    """Detects stances in policy documents and debate segments."""
    
    def __init__(self):
        self.support_indicators = [
            r'\b(support|favor|agree|approve|endorse|back|advocate)\b',
            r'\b(good|beneficial|positive|effective|successful|valuable)\b',
            r'\b(should|must|need|require|essential|necessary)\b',
            r'\b(help|assist|improve|enhance|strengthen|promote)\b',
        ]
        
        self.oppose_indicators = [
            r'\b(oppose|against|disagree|reject|denounce|condemn)\b',
            r'\b(bad|harmful|negative|ineffective|unsuccessful|damaging)\b',
            r'\b(should\s+not|must\s+not|need\s+not|avoid|prevent)\b',
            r'\b(hurt|harm|damage|weaken|undermine|threaten)\b',
        ]
        
        self.neutral_indicators = [
            r'\b(neutral|unclear|uncertain|undecided|mixed)\b',
            r'\b(maybe|perhaps|possibly|potentially|could)\b',
            r'\b(consider|examine|study|analyze|review)\b',
        ]
        
        self.target_patterns = [
            r'\b(policy|policies)\b',
            r'\b(bill|bills|legislation)\b',
            r'\b(regulation|regulations)\b',
            r'\b(law|laws)\b',
            r'\b(proposal|proposals)\b',
            r'\b(initiative|initiatives)\b',
        ]
    
    def detect_stances(self, segment: DebateSegment) -> List[Stance]:
        """
        Detect stances in a debate segment.
        
        Args:
            segment: Debate segment to analyze
            
        Returns:
            List of detected stances
        """
        stances = []
        
        # Extract stance targets
        targets = self._extract_stance_targets(segment.text)
        
        for target in targets:
            stance = self._analyze_stance_towards_target(segment, target)
            if stance:
                stances.append(stance)
        
        return stances
    
    def detect_stances_from_claims(self, claims: List[Claim]) -> List[Stance]:
        """
        Detect stances from claims.
        
        Args:
            claims: List of claims to analyze
            
        Returns:
            List of detected stances
        """
        stances = []
        
        for claim in claims:
            targets = self._extract_stance_targets(claim.text)
            
            for target in targets:
                stance = self._analyze_stance_from_claim(claim, target)
                if stance:
                    stances.append(stance)
        
        return stances
    
    def _extract_stance_targets(self, text: str) -> List[str]:
        """
        Extract stance targets from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of stance targets
        """
        targets = []
        text_lower = text.lower()
        
        for pattern in self.target_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            targets.extend(matches)
        
        # Remove duplicates and return
        return list(set(targets))
    
    def _analyze_stance_towards_target(self, segment: DebateSegment, target: str) -> Optional[Stance]:
        """
        Analyze stance towards a specific target.
        
        Args:
            segment: Debate segment
            target: Stance target
            
        Returns:
            Stance object if detected, None otherwise
        """
        text_lower = segment.text.lower()
        
        # Calculate stance scores
        support_score = self._calculate_support_score(text_lower)
        oppose_score = self._calculate_oppose_score(text_lower)
        neutral_score = self._calculate_neutral_score(text_lower)
        
        # Determine stance
        if support_score > oppose_score and support_score > neutral_score:
            stance_label = "support"
            confidence = support_score
        elif oppose_score > support_score and oppose_score > neutral_score:
            stance_label = "oppose"
            confidence = oppose_score
        elif neutral_score > 0.3:  # Threshold for neutral
            stance_label = "neutral"
            confidence = neutral_score
        else:
            return None
        
        # Extract evidence text
        evidence_text = self._extract_evidence_for_target(segment.text, target)
        
        return Stance(
            stance_label=stance_label,
            stance_target=target,
            confidence=confidence,
            evidence_text=evidence_text,
            source_segment=segment
        )
    
    def _analyze_stance_from_claim(self, claim: Claim, target: str) -> Optional[Stance]:
        """
        Analyze stance from a claim towards a target.
        
        Args:
            claim: Claim to analyze
            target: Stance target
            
        Returns:
            Stance object if detected, None otherwise
        """
        text_lower = claim.text.lower()
        
        # Calculate stance scores
        support_score = self._calculate_support_score(text_lower)
        oppose_score = self._calculate_oppose_score(text_lower)
        neutral_score = self._calculate_neutral_score(text_lower)
        
        # Determine stance
        if support_score > oppose_score and support_score > neutral_score:
            stance_label = "support"
            confidence = support_score * claim.confidence  # Weight by claim confidence
        elif oppose_score > support_score and oppose_score > neutral_score:
            stance_label = "oppose"
            confidence = oppose_score * claim.confidence
        elif neutral_score > 0.3:
            stance_label = "neutral"
            confidence = neutral_score * claim.confidence
        else:
            return None
        
        # Extract evidence text
        evidence_text = self._extract_evidence_for_target(claim.text, target)
        
        return Stance(
            stance_label=stance_label,
            stance_target=target,
            confidence=confidence,
            evidence_text=evidence_text,
            source_segment=claim.source_segment
        )
    
    def _calculate_support_score(self, text: str) -> float:
        """Calculate support score for text."""
        score = 0.0
        
        for pattern in self.support_indicators:
            matches = re.findall(pattern, text, re.IGNORECASE)
            score += len(matches) * 0.2
        
        return min(1.0, score)
    
    def _calculate_oppose_score(self, text: str) -> float:
        """Calculate oppose score for text."""
        score = 0.0
        
        for pattern in self.oppose_indicators:
            matches = re.findall(pattern, text, re.IGNORECASE)
            score += len(matches) * 0.2
        
        return min(1.0, score)
    
    def _calculate_neutral_score(self, text: str) -> float:
        """Calculate neutral score for text."""
        score = 0.0
        
        for pattern in self.neutral_indicators:
            matches = re.findall(pattern, text, re.IGNORECASE)
            score += len(matches) * 0.15
        
        return min(1.0, score)
    
    def _extract_evidence_for_target(self, text: str, target: str) -> str:
        """
        Extract evidence text for a specific target.
        
        Args:
            text: Full text
            target: Target to find evidence for
            
        Returns:
            Evidence text
        """
        # Simple implementation: return sentences containing the target
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            if target.lower() in sentence.lower():
                return sentence.strip()
        
        return text[:100] + "..." if len(text) > 100 else text
    
    def validate_stance(self, stance: Stance) -> bool:
        """
        Validate a detected stance.
        
        Args:
            stance: Stance to validate
            
        Returns:
            True if valid, False otherwise
        """
        if stance.stance_label not in ["support", "oppose", "neutral"]:
            return False
        
        if not stance.stance_target:
            return False
        
        if stance.confidence < 0.1 or stance.confidence > 1.0:
            return False
        
        if not stance.evidence_text:
            return False
        
        return True























