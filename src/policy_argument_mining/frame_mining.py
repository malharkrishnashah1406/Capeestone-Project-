"""
Frame Mining Module.

This module detects narrative frames and themes in policy discourse,
such as economic growth, public safety, consumer protection, etc.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .ingestion import DebateSegment
from .claim_detection import Claim
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class Frame:
    """Represents a detected narrative frame in policy discourse."""
    frame_label: str
    confidence: float
    evidence_text: str
    source_segment: DebateSegment


class FrameMiner:
    """Detects narrative frames in policy documents and debate segments."""
    
    def __init__(self):
        self.frame_patterns = {
            'economic_growth': [
                r'\b(economic\s+growth|economic\s+development|prosperity|wealth)\b',
                r'\b(jobs|employment|unemployment|workforce|labor)\b',
                r'\b(gdp|gross\s+domestic\s+product|economy|economic)\b',
                r'\b(investment|business|entrepreneurship|innovation)\b',
            ],
            'public_safety': [
                r'\b(public\s+safety|security|protection|safety)\b',
                r'\b(crime|criminal|law\s+enforcement|police)\b',
                r'\b(terrorism|terrorist|threat|danger)\b',
                r'\b(emergency|disaster|crisis|response)\b',
            ],
            'consumer_protection': [
                r'\b(consumer\s+protection|consumer\s+rights|consumers)\b',
                r'\b(fraud|scam|deception|misleading)\b',
                r'\b(privacy|data\s+protection|personal\s+information)\b',
                r'\b(transparency|disclosure|informed\s+choice)\b',
            ],
            'innovation': [
                r'\b(innovation|technology|digital|automation)\b',
                r'\b(research|development|rd|scientific)\b',
                r'\b(startup|entrepreneur|disruption|breakthrough)\b',
                r'\b(artificial\s+intelligence|ai|machine\s+learning)\b',
            ],
            'national_security': [
                r'\b(national\s+security|defense|military|armed\s+forces)\b',
                r'\b(cybersecurity|cyber\s+security|cyber\s+attack)\b',
                r'\b(intelligence|espionage|surveillance)\b',
                r'\b(border|immigration|foreign\s+policy)\b',
            ],
            'climate_risk': [
                r'\b(climate\s+change|global\s+warming|environmental)\b',
                r'\b(carbon|emissions|greenhouse|sustainability)\b',
                r'\b(renewable|clean\s+energy|fossil\s+fuels)\b',
                r'\b(conservation|biodiversity|ecosystem)\b',
            ],
            'health_care': [
                r'\b(health\s+care|healthcare|medical|health)\b',
                r'\b(patient|doctor|hospital|treatment)\b',
                r'\b(insurance|coverage|premium|deductible)\b',
                r'\b(public\s+health|epidemic|pandemic|disease)\b',
            ],
            'education': [
                r'\b(education|school|university|college)\b',
                r'\b(student|teacher|learning|academic)\b',
                r'\b(skill|training|workforce\s+development)\b',
                r'\b(literacy|knowledge|curriculum)\b',
            ],
            'social_justice': [
                r'\b(social\s+justice|equality|equity|fairness)\b',
                r'\b(discrimination|bias|prejudice|inclusion)\b',
                r'\b(minority|marginalized|underrepresented)\b',
                r'\b(civil\s+rights|human\s+rights|diversity)\b',
            ],
            'fiscal_responsibility': [
                r'\b(fiscal|budget|deficit|debt|spending)\b',
                r'\b(tax|taxation|revenue|cost|expense)\b',
                r'\b(efficiency|waste|overspending|fiscal\s+responsibility)\b',
                r'\b(balanced\s+budget|deficit\s+reduction)\b',
            ]
        }
    
    def detect_frames(self, segment: DebateSegment) -> List[Frame]:
        """
        Detect frames in a debate segment.
        
        Args:
            segment: Debate segment to analyze
            
        Returns:
            List of detected frames
        """
        frames = []
        
        # Check each frame pattern
        for frame_label, patterns in self.frame_patterns.items():
            frame = self._detect_frame_in_text(segment, frame_label, patterns)
            if frame:
                frames.append(frame)
        
        return frames
    
    def detect_frames_from_claims(self, claims: List[Claim]) -> List[Frame]:
        """
        Detect frames from claims.
        
        Args:
            claims: List of claims to analyze
            
        Returns:
            List of detected frames
        """
        frames = []
        
        for claim in claims:
            for frame_label, patterns in self.frame_patterns.items():
                frame = self._detect_frame_in_claim(claim, frame_label, patterns)
                if frame:
                    frames.append(frame)
        
        return frames
    
    def _detect_frame_in_text(self, segment: DebateSegment, frame_label: str, patterns: List[str]) -> Optional[Frame]:
        """
        Detect a specific frame in text.
        
        Args:
            segment: Debate segment
            frame_label: Frame label
            patterns: Patterns to match
            
        Returns:
            Frame if detected, None otherwise
        """
        text_lower = segment.text.lower()
        confidence = 0.0
        evidence_text = ""
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                confidence += len(matches) * 0.2
                # Use the first match as evidence
                if not evidence_text:
                    evidence_text = matches[0]
        
        if confidence > 0.2:  # Threshold for frame detection
            return Frame(
                frame_label=frame_label,
                confidence=min(1.0, confidence),
                evidence_text=evidence_text,
                source_segment=segment
            )
        
        return None
    
    def _detect_frame_in_claim(self, claim: Claim, frame_label: str, patterns: List[str]) -> Optional[Frame]:
        """
        Detect a specific frame in a claim.
        
        Args:
            claim: Claim to analyze
            frame_label: Frame label
            patterns: Patterns to match
            
        Returns:
            Frame if detected, None otherwise
        """
        text_lower = claim.text.lower()
        confidence = 0.0
        evidence_text = ""
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                confidence += len(matches) * 0.2
                # Use the first match as evidence
                if not evidence_text:
                    evidence_text = matches[0]
        
        if confidence > 0.15:  # Lower threshold for claims
            return Frame(
                frame_label=frame_label,
                confidence=min(1.0, confidence * claim.confidence),  # Weight by claim confidence
                evidence_text=evidence_text,
                source_segment=claim.source_segment
            )
        
        return None
    
    def get_frame_distribution(self, frames: List[Frame]) -> Dict[str, int]:
        """
        Get distribution of frames.
        
        Args:
            frames: List of frames
            
        Returns:
            Dictionary mapping frame labels to counts
        """
        distribution = {}
        
        for frame in frames:
            if frame.frame_label not in distribution:
                distribution[frame.frame_label] = 0
            distribution[frame.frame_label] += 1
        
        return distribution
    
    def get_dominant_frames(self, frames: List[Frame], top_k: int = 3) -> List[Frame]:
        """
        Get the most dominant frames.
        
        Args:
            frames: List of frames
            top_k: Number of top frames to return
            
        Returns:
            List of dominant frames
        """
        # Sort by confidence and return top k
        sorted_frames = sorted(frames, key=lambda x: x.confidence, reverse=True)
        return sorted_frames[:top_k]
    
    def validate_frame(self, frame: Frame) -> bool:
        """
        Validate a detected frame.
        
        Args:
            frame: Frame to validate
            
        Returns:
            True if valid, False otherwise
        """
        valid_frames = list(self.frame_patterns.keys())
        
        if frame.frame_label not in valid_frames:
            return False
        
        if frame.confidence < 0.1 or frame.confidence > 1.0:
            return False
        
        if not frame.evidence_text:
            return False
        
        return True
    
    def get_frame_relationships(self, frames: List[Frame]) -> Dict[str, List[str]]:
        """
        Get relationships between frames.
        
        Args:
            frames: List of frames
            
        Returns:
            Dictionary mapping frames to related frames
        """
        relationships = {
            'economic_growth': ['innovation', 'fiscal_responsibility'],
            'public_safety': ['national_security', 'consumer_protection'],
            'consumer_protection': ['public_safety', 'social_justice'],
            'innovation': ['economic_growth', 'education'],
            'national_security': ['public_safety', 'cybersecurity'],
            'climate_risk': ['health_care', 'social_justice'],
            'health_care': ['social_justice', 'education'],
            'education': ['innovation', 'social_justice'],
            'social_justice': ['health_care', 'consumer_protection'],
            'fiscal_responsibility': ['economic_growth', 'public_safety']
        }
        
        return relationships























