"""
Claim Detection Module.

This module identifies claims and assertions in policy documents and debate segments.
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from .ingestion import DebateSegment
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class Claim:
    """Represents a detected claim in policy text."""
    text: str
    confidence: float
    claim_type: str  # factual, normative, policy, etc.
    evidence_spans: List[Tuple[int, int]]  # Character spans for evidence
    source_segment: DebateSegment


class ClaimDetector:
    """Detects claims in policy documents and debate segments."""
    
    def __init__(self):
        self.claim_indicators = [
            r'\b(claim|assert|argue|believe|think|know|prove|demonstrate)\b',
            r'\b(evidence|data|study|research|analysis|report)\s+(shows|indicates|suggests|proves)\b',
            r'\b(fact|truth|reality|certainly|definitely|clearly)\b',
            r'\b(should|must|need|require|essential|necessary)\b',
            r'\b(impact|effect|result|consequence|outcome)\b',
        ]
        
        self.claim_types = {
            'factual': r'\b(fact|data|evidence|study|research)\b',
            'normative': r'\b(should|must|need|require|essential)\b',
            'policy': r'\b(policy|regulation|law|legislation|rule)\b',
            'causal': r'\b(cause|effect|impact|result|consequence)\b',
            'predictive': r'\b(will|would|could|might|may)\b',
        }
    
    def detect_claims(self, segment_or_segments) -> List[Claim]:
        """Detect claims from a DebateSegment or a list of DebateSegment."""
        if isinstance(segment_or_segments, list):
            return self.detect_claims_batch(segment_or_segments)
        segment: DebateSegment = segment_or_segments
        claims = []
        sentences = self._split_sentences(segment.text)
        for sentence in sentences:
            claim = self._analyze_sentence_for_claims(sentence, segment)
            if claim:
                claims.append(claim)
        return claims
    
    def detect_claims_batch(self, segments: List[DebateSegment]) -> List[Claim]:
        """
        Detect claims in multiple segments.
        
        Args:
            segments: List of debate segments
            
        Returns:
            List of detected claims
        """
        all_claims = []
        for segment in segments:
            claims = self.detect_claims(segment)
            all_claims.extend(claims)
        
        return all_claims
    
    def _analyze_sentence_for_claims(self, sentence: str, segment: DebateSegment) -> Optional[Claim]:
        """
        Analyze a sentence for claims.
        
        Args:
            sentence: Sentence to analyze
            segment: Source segment
            
        Returns:
            Claim object if found, None otherwise
        """
        # Check for claim indicators
        claim_score = self._calculate_claim_score(sentence)
        
        if claim_score > 0.3:  # Threshold for claim detection
            claim_type = self._classify_claim_type(sentence)
            evidence_spans = self._extract_evidence_spans(sentence)
            
            return Claim(
                text=sentence,
                confidence=claim_score,
                claim_type=claim_type,
                evidence_spans=evidence_spans,
                source_segment=segment
            )
        
        return None
    
    def _calculate_claim_score(self, text: str) -> float:
        """
        Calculate claim score for text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Claim score between 0 and 1
        """
        score = 0.0
        text_lower = text.lower()
        
        # Check for claim indicators
        for pattern in self.claim_indicators:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            score += len(matches) * 0.2
        
        # Check for strong language
        strong_words = ['definitely', 'certainly', 'clearly', 'obviously', 'undoubtedly']
        for word in strong_words:
            if word in text_lower:
                score += 0.1
        
        # Check for evidence indicators
        evidence_words = ['because', 'since', 'as', 'due to', 'according to']
        for word in evidence_words:
            if word in text_lower:
                score += 0.15
        
        return min(1.0, score)
    
    def _classify_claim_type(self, text: str) -> str:
        """
        Classify the type of claim.
        
        Args:
            text: Text to classify
            
        Returns:
            Claim type
        """
        text_lower = text.lower()
        
        for claim_type, pattern in self.claim_types.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                return claim_type
        
        return 'general'
    
    def _extract_evidence_spans(self, text: str) -> List[Tuple[int, int]]:
        """
        Extract evidence spans from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of character spans for evidence
        """
        spans = []
        
        # Look for quoted text as evidence
        quote_patterns = [
            r'"([^"]*)"',
            r"'([^']*)'",
        ]
        
        for pattern in quote_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                spans.append((match.start(), match.end()))
        
        # Look for citations
        citation_patterns = [
            r'\([^)]*\)',  # Parenthetical citations
            r'\[[^\]]*\]',  # Bracket citations
        ]
        
        for pattern in citation_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                spans.append((match.start(), match.end()))
        
        return spans
    
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
    
    def validate_claim(self, claim: Claim) -> bool:
        """
        Validate a detected claim.
        
        Args:
            claim: Claim to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not claim.text or len(claim.text.strip()) < 10:
            return False
        
        if claim.confidence < 0.1 or claim.confidence > 1.0:
            return False
        
        if not claim.claim_type:
            return False
        
        return True




















