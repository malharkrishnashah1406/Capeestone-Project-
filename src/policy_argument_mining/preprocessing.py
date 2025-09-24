"""
Policy Document Preprocessing Module.

This module handles cleaning, normalization, and preprocessing of policy documents
and debate transcripts.
"""

import re
from typing import List, Dict, Any, Union
from .ingestion import DebateSegment
import logging

logger = logging.getLogger(__name__)


class PolicyPreprocessor:
    """Handles preprocessing of policy documents and debate segments."""
    
    def __init__(self):
        self.noise_patterns = [
            r'\[.*?\]',  # Remove bracketed text
            r'\(.*?\)',  # Remove parenthetical text
            r'[^\w\s\.\,\!\?\-]',  # Remove special characters except basic punctuation
        ]
        
        self.normalization_rules = {
            r'\s+': ' ',  # Multiple spaces to single space
            r'\.{2,}': '.',  # Multiple dots to single dot
            r'\!{2,}': '!',  # Multiple exclamation marks to single
            r'\?{2,}': '?',  # Multiple question marks to single
        }
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess raw text (clean + normalize)."""
        return self._normalize_text(self._clean_text(text or "")).strip()
    
    def preprocess_segment(self, segment: Union[DebateSegment, str]) -> DebateSegment:
        """
        Preprocess a debate segment or raw text.
        
        Args:
            segment: Debate segment OR raw text string
            
        Returns:
            Preprocessed DebateSegment
        """
        if isinstance(segment, str):
            raw_text = segment
            segment_obj = DebateSegment(
                speaker="",
                party="",
                start_ts=0.0,
                end_ts=0.0,
                text=raw_text,
                asr_confidence=1.0,
                turn_index=0
            )
        else:
            segment_obj = segment
        
        # Clean text
        cleaned_text = self._clean_text(segment_obj.text)
        
        # Normalize text
        normalized_text = self._normalize_text(cleaned_text)
        
        # Create new segment with cleaned text
        return DebateSegment(
            speaker=segment_obj.speaker,
            party=segment_obj.party,
            start_ts=segment_obj.start_ts,
            end_ts=segment_obj.end_ts,
            text=normalized_text,
            asr_confidence=segment_obj.asr_confidence,
            turn_index=segment_obj.turn_index
        )

    def preprocess_segments(self, segments: List[DebateSegment]) -> List[DebateSegment]:
        """
        Preprocess multiple debate segments.
        
        Args:
            segments: List of debate segments
            
        Returns:
            List of preprocessed segments
        """
        return [self.preprocess_segment(segment) for segment in segments]
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text by removing noise patterns.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        cleaned = text or ""
        
        # Remove noise patterns
        for pattern in self.noise_patterns:
            cleaned = re.sub(pattern, '', cleaned)
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip()
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text according to rules.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        normalized = text or ""
        
        # Apply normalization rules
        for pattern, replacement in self.normalization_rules.items():
            normalized = re.sub(pattern, replacement, normalized)
        
        return normalized.strip()
    
    def extract_quotes(self, text: str) -> List[str]:
        """
        Extract quoted text from segment.
        
        Args:
            text: Text to extract quotes from
            
        Returns:
            List of quoted strings
        """
        # Simple quote extraction (stub implementation)
        quotes = re.findall(r'"([^"]*)"', text or "")
        quotes.extend(re.findall(r"'([^']*)'", text or ""))
        return quotes
    
    def extract_speaker_tags(self, text: str) -> Dict[str, str]:
        """
        Extract speaker tags and metadata.
        
        Args:
            text: Text to extract tags from
            
        Returns:
            Dictionary of speaker tags
        """
        tags = {}
        
        # Extract party affiliations (stub implementation)
        party_patterns = [
            r'\(([^)]*Party[^)]*)\)',
            r'\[([^\]]*Party[^\]]*)\]',
        ]
        
        for pattern in party_patterns:
            matches = re.findall(pattern, text or "", re.IGNORECASE)
            if matches:
                tags['party'] = matches[0]
                break
        
        return tags
    
    def split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting (stub implementation)
        sentences = re.split(r'[.!?]+', text or "")
        return [s.strip() for s in sentences if s.strip()]
    
    def remove_noise(self, text: str) -> str:
        """
        Remove noise from text.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        return self._clean_text(text)




















