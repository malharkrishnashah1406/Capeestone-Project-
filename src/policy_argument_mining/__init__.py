"""
Policy Argument Mining Module.

This module provides tools for analyzing political discourse, policy debates,
and official statements to extract arguments, stances, and policy implications.
"""

from .ingestion import PolicyIngestion
from .preprocessing import PolicyPreprocessor
from .claim_detection import ClaimDetector
from .stance_detection import StanceDetector
from .argument_role_labeling import ArgumentRoleLabeler
from .frame_mining import FrameMiner
from .entity_linking import EntityLinker
from .graph import ArgumentGraph
from .scoring import ArgumentScorer
from .integration import PolicyArgumentIntegrator

# Backward-compatible alias for segmenter expected by UI
class PolicySegmenter(PolicyPreprocessor):
    """Segments policy text into meaningful units for argument analysis."""
    
    def segment_text(self, text):
        """Segment the input text into meaningful units.
        
        Args:
            text (str): The input text to segment.
            
        Returns:
            list: A list of dictionaries, each containing a 'text' key with the segment text
                  and a 'type' key indicating the type of segment.
        """
        if not text or not isinstance(text, str):
            return []
            
        # Use spaCy's sentence segmentation
        doc = self.nlp(text)
        
        # Create segments from sentences
        segments = []
        for sent in doc.sents:
            segment_text = sent.text.strip()
            if len(segment_text) > 1:  # Ignore very short segments
                segments.append({
                    'text': segment_text,
                    'type': 'sentence'
                })
        
        # If no segments were found (shouldn't happen with proper text), return the full text
        if not segments and text.strip():
            return [{'text': text.strip(), 'type': 'paragraph'}]
            
        return segments

__all__ = [
    'PolicyIngestion',
    'PolicyPreprocessor',
    'PolicySegmenter',
    'ClaimDetector',
    'StanceDetector',
    'ArgumentRoleLabeler',
    'FrameMiner',
    'EntityLinker',
    'ArgumentGraph',
    'ArgumentScorer',
    'PolicyArgumentIntegrator',
]
