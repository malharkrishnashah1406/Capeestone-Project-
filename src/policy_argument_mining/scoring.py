"""
Argument Scoring Module.

This module computes salience, credibility, and uncertainty scores
for arguments in policy debates.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .ingestion import DebateSegment
from .claim_detection import Claim
from .stance_detection import Stance
from .argument_role_labeling import ArgumentRole
from .frame_mining import Frame
from .entity_linking import Entity
from .graph import ArgumentGraph
import logging

logger = logging.getLogger(__name__)


@dataclass
class ArgumentScores:
    """Represents scores for an argument."""
    salience: float  # Frequency and centrality
    credibility: float  # Source quality and evidence
    uncertainty: float  # Conflict and disagreement
    overall_score: float  # Combined score


class ArgumentScorer:
    """Computes various scores for arguments in policy debates."""
    
    def __init__(self):
        self.source_quality_weights = {
            'expert': 1.0,
            'official': 0.9,
            'academic': 0.8,
            'media': 0.6,
            'social': 0.4,
            'unknown': 0.3
        }
        
        self.evidence_indicators = [
            'study', 'research', 'data', 'evidence', 'analysis',
            'report', 'survey', 'statistics', 'findings', 'results'
        ]
        
        self.uncertainty_indicators = [
            'maybe', 'perhaps', 'possibly', 'uncertain', 'unclear',
            'debate', 'controversy', 'dispute', 'disagreement', 'conflict'
        ]
    
    def score_claim(self, claim: Claim, graph: Optional[ArgumentGraph] = None) -> ArgumentScores:
        """
        Score a claim.
        
        Args:
            claim: Claim to score
            graph: Optional argument graph for centrality calculation
            
        Returns:
            ArgumentScores for the claim
        """
        salience = self._calculate_salience(claim, graph)
        credibility = self._calculate_credibility(claim)
        uncertainty = self._calculate_uncertainty(claim)
        
        # Overall score is weighted combination
        overall_score = (0.4 * salience + 0.4 * credibility + 0.2 * (1 - uncertainty))
        
        return ArgumentScores(
            salience=salience,
            credibility=credibility,
            uncertainty=uncertainty,
            overall_score=overall_score
        )
    
    def score_stance(self, stance: Stance, graph: Optional[ArgumentGraph] = None) -> ArgumentScores:
        """
        Score a stance.
        
        Args:
            stance: Stance to score
            graph: Optional argument graph for centrality calculation
            
        Returns:
            ArgumentScores for the stance
        """
        salience = self._calculate_stance_salience(stance, graph)
        credibility = self._calculate_stance_credibility(stance)
        uncertainty = self._calculate_stance_uncertainty(stance)
        
        overall_score = (0.4 * salience + 0.4 * credibility + 0.2 * (1 - uncertainty))
        
        return ArgumentScores(
            salience=salience,
            credibility=credibility,
            uncertainty=uncertainty,
            overall_score=overall_score
        )
    
    def score_entity(self, entity: Entity) -> ArgumentScores:
        """
        Score an entity.
        
        Args:
            entity: Entity to score
            
        Returns:
            ArgumentScores for the entity
        """
        salience = self._calculate_entity_salience(entity)
        credibility = self._calculate_entity_credibility(entity)
        uncertainty = self._calculate_entity_uncertainty(entity)
        
        overall_score = (0.3 * salience + 0.5 * credibility + 0.2 * (1 - uncertainty))
        
        return ArgumentScores(
            salience=salience,
            credibility=credibility,
            uncertainty=uncertainty,
            overall_score=overall_score
        )
    
    def _calculate_salience(self, claim: Claim, graph: Optional[ArgumentGraph] = None) -> float:
        """
        Calculate salience score for a claim.
        
        Args:
            claim: Claim to score
            graph: Optional argument graph
            
        Returns:
            Salience score between 0 and 1
        """
        # Base salience from claim confidence
        salience = claim.confidence
        
        # Boost salience if claim has evidence
        if claim.evidence_spans:
            salience += 0.2
        
        # Boost salience based on graph centrality if available
        if graph:
            # Find the claim node in the graph
            for node_id, node in graph.nodes.items():
                if (node.node_type == "claim" and 
                    hasattr(node.content, 'text') and 
                    node.content.text == claim.text):
                    # Get centrality score (simplified)
                    centrality = graph.graph.degree(node_id) / max(1, len(graph.nodes))
                    salience += centrality * 0.3
                    break
        
        return min(1.0, salience)
    
    def _calculate_credibility(self, claim: Claim) -> float:
        """
        Calculate credibility score for a claim.
        
        Args:
            claim: Claim to score
            
        Returns:
            Credibility score between 0 and 1
        """
        credibility = 0.5  # Base credibility
        
        # Boost credibility based on evidence indicators
        text_lower = claim.text.lower()
        evidence_count = sum(1 for indicator in self.evidence_indicators if indicator in text_lower)
        credibility += min(0.3, evidence_count * 0.1)
        
        # Boost credibility based on source quality
        source_quality = self._get_source_quality(claim.source_segment)
        credibility += source_quality * 0.2
        
        return min(1.0, credibility)
    
    def _calculate_uncertainty(self, claim: Claim) -> float:
        """
        Calculate uncertainty score for a claim.
        
        Args:
            claim: Claim to score
            
        Returns:
            Uncertainty score between 0 and 1
        """
        uncertainty = 0.3  # Base uncertainty
        
        # Increase uncertainty based on uncertainty indicators
        text_lower = claim.text.lower()
        uncertainty_count = sum(1 for indicator in self.uncertainty_indicators if indicator in text_lower)
        uncertainty += min(0.4, uncertainty_count * 0.1)
        
        # Decrease uncertainty based on claim confidence
        uncertainty -= claim.confidence * 0.2
        
        return max(0.0, min(1.0, uncertainty))
    
    def _calculate_stance_salience(self, stance: Stance, graph: Optional[ArgumentGraph] = None) -> float:
        """Calculate salience score for a stance."""
        salience = stance.confidence
        
        # Boost salience for strong stances
        if stance.stance_label in ['support', 'oppose']:
            salience += 0.2
        
        # Boost salience based on graph centrality if available
        if graph:
            for node_id, node in graph.nodes.items():
                if (node.node_type == "stance" and 
                    hasattr(node.content, 'stance_target') and 
                    node.content.stance_target == stance.stance_target):
                    centrality = graph.graph.degree(node_id) / max(1, len(graph.nodes))
                    salience += centrality * 0.3
                    break
        
        return min(1.0, salience)
    
    def _calculate_stance_credibility(self, stance: Stance) -> float:
        """Calculate credibility score for a stance."""
        credibility = 0.5
        
        # Boost credibility based on evidence text
        if len(stance.evidence_text) > 50:
            credibility += 0.2
        
        # Boost credibility based on source quality
        source_quality = self._get_source_quality(stance.source_segment)
        credibility += source_quality * 0.3
        
        return min(1.0, credibility)
    
    def _calculate_stance_uncertainty(self, stance: Stance) -> float:
        """Calculate uncertainty score for a stance."""
        uncertainty = 0.3
        
        # Increase uncertainty for neutral stances
        if stance.stance_label == 'neutral':
            uncertainty += 0.3
        
        # Decrease uncertainty based on stance confidence
        uncertainty -= stance.confidence * 0.2
        
        return max(0.0, min(1.0, uncertainty))
    
    def _calculate_entity_salience(self, entity: Entity) -> float:
        """Calculate salience score for an entity."""
        salience = entity.confidence
        
        # Boost salience for known entities
        if entity.external_id:
            salience += 0.3
        
        return min(1.0, salience)
    
    def _calculate_entity_credibility(self, entity: Entity) -> float:
        """Calculate credibility score for an entity."""
        credibility = 0.5
        
        # Boost credibility for linked entities
        if entity.external_id:
            credibility += 0.4
        
        # Boost credibility based on entity type
        if entity.entity_type in ['organization', 'jurisdiction']:
            credibility += 0.1
        
        return min(1.0, credibility)
    
    def _calculate_entity_uncertainty(self, entity: Entity) -> float:
        """Calculate uncertainty score for an entity."""
        uncertainty = 0.3
        
        # Decrease uncertainty for linked entities
        if entity.external_id:
            uncertainty -= 0.2
        
        # Decrease uncertainty based on entity confidence
        uncertainty -= entity.confidence * 0.2
        
        return max(0.0, min(1.0, uncertainty))
    
    def _get_source_quality(self, segment: DebateSegment) -> float:
        """
        Get source quality score for a segment.
        
        Args:
            segment: Debate segment
            
        Returns:
            Source quality score between 0 and 1
        """
        source_lower = segment.source.lower()
        
        # Check for known high-quality sources
        if any(quality_source in source_lower for quality_source in ['congress', 'senate', 'house', 'federal']):
            return self.source_quality_weights['official']
        elif any(academic_source in source_lower for academic_source in ['university', 'college', 'research']):
            return self.source_quality_weights['academic']
        elif any(media_source in source_lower for media_source in ['news', 'press', 'media']):
            return self.source_quality_weights['media']
        else:
            return self.source_quality_weights['unknown']
    
    def get_aggregate_scores(self, claims: List[Claim], stances: List[Stance], 
                           entities: List[Entity], graph: Optional[ArgumentGraph] = None) -> Dict[str, float]:
        """
        Get aggregate scores across all arguments.
        
        Args:
            claims: List of claims
            stances: List of stances
            entities: List of entities
            graph: Optional argument graph
            
        Returns:
            Dictionary with aggregate scores
        """
        claim_scores = [self.score_claim(claim, graph) for claim in claims]
        stance_scores = [self.score_stance(stance, graph) for stance in stances]
        entity_scores = [self.score_entity(entity) for entity in entities]
        
        all_scores = claim_scores + stance_scores + entity_scores
        
        if not all_scores:
            return {
                'avg_salience': 0.0,
                'avg_credibility': 0.0,
                'avg_uncertainty': 0.0,
                'avg_overall': 0.0
            }
        
        return {
            'avg_salience': sum(score.salience for score in all_scores) / len(all_scores),
            'avg_credibility': sum(score.credibility for score in all_scores) / len(all_scores),
            'avg_uncertainty': sum(score.uncertainty for score in all_scores) / len(all_scores),
            'avg_overall': sum(score.overall_score for score in all_scores) / len(all_scores)
        }
    
    def get_top_scored_arguments(self, claims: List[Claim], stances: List[Stance], 
                                entities: List[Entity], graph: Optional[ArgumentGraph] = None, 
                                top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Get top-scored arguments.
        
        Args:
            claims: List of claims
            stances: List of stances
            entities: List of entities
            graph: Optional argument graph
            top_k: Number of top arguments to return
            
        Returns:
            List of top-scored arguments with their scores
        """
        scored_arguments = []
        
        # Score claims
        for claim in claims:
            scores = self.score_claim(claim, graph)
            scored_arguments.append({
                'type': 'claim',
                'content': claim.text,
                'scores': scores,
                'source': claim.source_segment
            })
        
        # Score stances
        for stance in stances:
            scores = self.score_stance(stance, graph)
            scored_arguments.append({
                'type': 'stance',
                'content': f"{stance.stance_label} towards {stance.stance_target}",
                'scores': scores,
                'source': stance.source_segment
            })
        
        # Score entities
        for entity in entities:
            scores = self.score_entity(entity)
            scored_arguments.append({
                'type': 'entity',
                'content': entity.name,
                'scores': scores,
                'source': entity.source_segment
            })
        
        # Sort by overall score and return top k
        scored_arguments.sort(key=lambda x: x['scores'].overall_score, reverse=True)
        return scored_arguments[:top_k]























