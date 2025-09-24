"""
Policy Argument Integration Module.

This module bridges the policy argument mining layer to the event detection
and financial impact analysis layers.
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
from .scoring import ArgumentScorer, ArgumentScores
from domains.base import Event, Shock
import logging

logger = logging.getLogger(__name__)


@dataclass
class PolicySignal:
    """Represents a policy signal derived from argument analysis."""
    signal_type: str  # uncertainty, consensus, polarization, urgency
    intensity: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    evidence: str
    source_arguments: List[str]  # IDs of source arguments


@dataclass
class PolicyImpact:
    """Represents the impact of policy arguments on financial predictions."""
    impact_direction: str  # positive, negative, neutral
    impact_magnitude: float  # 0.0 to 1.0
    impact_timeframe: str  # short_term, medium_term, long_term
    confidence: float  # 0.0 to 1.0
    policy_signals: List[PolicySignal]


class PolicyArgumentIntegrator:
    """Integrates policy argument analysis with event detection and financial impact."""
    
    def __init__(self):
        self.scorer = ArgumentScorer()
        
        # Policy signal thresholds
        self.uncertainty_threshold = 0.6
        self.consensus_threshold = 0.7
        self.polarization_threshold = 0.5
        self.urgency_threshold = 0.8
        
        # Impact mapping weights
        self.impact_weights = {
            'uncertainty': {'magnitude': 0.3, 'timeframe': 'short_term'},
            'consensus': {'magnitude': 0.5, 'timeframe': 'medium_term'},
            'polarization': {'magnitude': 0.4, 'timeframe': 'medium_term'},
            'urgency': {'magnitude': 0.7, 'timeframe': 'short_term'}
        }
    
    def analyze_policy_arguments(self, claims: List[Claim], stances: List[Stance], 
                               entities: List[Entity], frames: List[Frame], 
                               graph: Optional[ArgumentGraph] = None) -> List[PolicySignal]:
        """
        Analyze policy arguments and extract policy signals.
        
        Args:
            claims: List of claims
            stances: List of stances
            entities: List of entities
            frames: List of frames
            graph: Optional argument graph
            
        Returns:
            List of policy signals
        """
        signals = []
        
        # Analyze uncertainty
        uncertainty_signal = self._analyze_uncertainty(claims, stances, graph)
        if uncertainty_signal:
            signals.append(uncertainty_signal)
        
        # Analyze consensus
        consensus_signal = self._analyze_consensus(stances, graph)
        if consensus_signal:
            signals.append(consensus_signal)
        
        # Analyze polarization
        polarization_signal = self._analyze_polarization(stances, graph)
        if polarization_signal:
            signals.append(polarization_signal)
        
        # Analyze urgency
        urgency_signal = self._analyze_urgency(claims, frames, graph)
        if urgency_signal:
            signals.append(urgency_signal)
        
        return signals
    
    def convert_to_events(self, policy_signals: List[PolicySignal], 
                         jurisdiction: str = "US") -> List[Event]:
        """
        Convert policy signals to events for the event detection layer.
        
        Args:
            policy_signals: List of policy signals
            jurisdiction: Jurisdiction for the events
            
        Returns:
            List of events
        """
        events = []
        
        for signal in policy_signals:
            event = self._signal_to_event(signal, jurisdiction)
            if event:
                events.append(event)
        
        return events
    
    def enhance_impact_prediction(self, base_impact: Dict[str, Any], 
                                policy_signals: List[PolicySignal]) -> PolicyImpact:
        """
        Enhance impact prediction with policy argument signals.
        
        Args:
            base_impact: Base impact prediction
            policy_signals: List of policy signals
            
        Returns:
            Enhanced policy impact
        """
        # Start with base impact
        impact_direction = base_impact.get('direction', 'neutral')
        impact_magnitude = base_impact.get('magnitude', 0.0)
        impact_timeframe = base_impact.get('timeframe', 'medium_term')
        confidence = base_impact.get('confidence', 0.5)
        
        # Adjust based on policy signals
        for signal in policy_signals:
            adjustment = self._calculate_signal_adjustment(signal)
            
            # Adjust magnitude
            if signal.signal_type == 'urgency':
                impact_magnitude = min(1.0, impact_magnitude + adjustment['magnitude'])
            elif signal.signal_type == 'uncertainty':
                confidence = max(0.1, confidence - adjustment['confidence'])
            elif signal.signal_type == 'polarization':
                impact_magnitude = min(1.0, impact_magnitude + adjustment['magnitude'])
            
            # Adjust timeframe
            if signal.signal_type in ['urgency', 'uncertainty']:
                impact_timeframe = 'short_term'
        
        return PolicyImpact(
            impact_direction=impact_direction,
            impact_magnitude=impact_magnitude,
            impact_timeframe=impact_timeframe,
            confidence=confidence,
            policy_signals=policy_signals
        )
    
    def _analyze_uncertainty(self, claims: List[Claim], stances: List[Stance], 
                           graph: Optional[ArgumentGraph] = None) -> Optional[PolicySignal]:
        """Analyze uncertainty in policy arguments."""
        if not claims and not stances:
            return None
        
        # Calculate average uncertainty
        claim_scores = [self.scorer.score_claim(claim, graph) for claim in claims]
        stance_scores = [self.scorer.score_stance(stance, graph) for stance in stances]
        
        all_scores = claim_scores + stance_scores
        if not all_scores:
            return None
        
        avg_uncertainty = sum(score.uncertainty for score in all_scores) / len(all_scores)
        
        if avg_uncertainty > self.uncertainty_threshold:
            return PolicySignal(
                signal_type='uncertainty',
                intensity=avg_uncertainty,
                confidence=0.7,
                evidence=f"Average uncertainty score: {avg_uncertainty:.2f}",
                source_arguments=[f"claim_{i}" for i in range(len(claims))] + [f"stance_{i}" for i in range(len(stances))]
            )
        
        return None
    
    def _analyze_consensus(self, stances: List[Stance], 
                          graph: Optional[ArgumentGraph] = None) -> Optional[PolicySignal]:
        """Analyze consensus in policy stances."""
        if not stances:
            return None
        
        # Count stance types
        stance_counts = {'support': 0, 'oppose': 0, 'neutral': 0}
        for stance in stances:
            stance_counts[stance.stance_label] += 1
        
        total_stances = len(stances)
        if total_stances == 0:
            return None
        
        # Calculate consensus (dominance of one stance)
        max_count = max(stance_counts.values())
        consensus_ratio = max_count / total_stances
        
        if consensus_ratio > self.consensus_threshold:
            dominant_stance = max(stance_counts, key=stance_counts.get)
            return PolicySignal(
                signal_type='consensus',
                intensity=consensus_ratio,
                confidence=0.8,
                evidence=f"Consensus on {dominant_stance}: {consensus_ratio:.2f}",
                source_arguments=[f"stance_{i}" for i in range(len(stances))]
            )
        
        return None
    
    def _analyze_polarization(self, stances: List[Stance], 
                             graph: Optional[ArgumentGraph] = None) -> Optional[PolicySignal]:
        """Analyze polarization in policy stances."""
        if not stances:
            return None
        
        # Count support vs oppose
        support_count = sum(1 for stance in stances if stance.stance_label == 'support')
        oppose_count = sum(1 for stance in stances if stance.stance_label == 'oppose')
        
        total_controversial = support_count + oppose_count
        if total_controversial == 0:
            return None
        
        # Calculate polarization (balance between support and oppose)
        polarization = min(support_count, oppose_count) / total_controversial
        
        if polarization > self.polarization_threshold:
            return PolicySignal(
                signal_type='polarization',
                intensity=polarization,
                confidence=0.7,
                evidence=f"Polarization: {support_count} support vs {oppose_count} oppose",
                source_arguments=[f"stance_{i}" for i in range(len(stances))]
            )
        
        return None
    
    def _analyze_urgency(self, claims: List[Claim], frames: List[Frame], 
                        graph: Optional[ArgumentGraph] = None) -> Optional[PolicySignal]:
        """Analyze urgency in policy arguments."""
        urgency_indicators = [
            'urgent', 'immediate', 'crisis', 'emergency', 'critical',
            'now', 'asap', 'deadline', 'time-sensitive', 'pressing'
        ]
        
        urgency_count = 0
        total_text = ""
        
        # Check claims for urgency indicators
        for claim in claims:
            total_text += claim.text.lower() + " "
        
        # Check frames for urgency indicators
        for frame in frames:
            if frame.frame_label in ['public_safety', 'national_security', 'climate_risk']:
                urgency_count += 1
        
        # Count urgency words
        for indicator in urgency_indicators:
            urgency_count += total_text.count(indicator)
        
        urgency_intensity = min(1.0, urgency_count / max(1, len(claims)))
        
        if urgency_intensity > self.urgency_threshold:
            return PolicySignal(
                signal_type='urgency',
                intensity=urgency_intensity,
                confidence=0.6,
                evidence=f"Urgency indicators found: {urgency_count}",
                source_arguments=[f"claim_{i}" for i in range(len(claims))] + [f"frame_{i}" for i in range(len(frames))]
            )
        
        return None
    
    def _signal_to_event(self, signal: PolicySignal, jurisdiction: str) -> Optional[Event]:
        """Convert a policy signal to an event."""
        from datetime import datetime
        
        # Map signal types to event categories
        category_mapping = {
            'uncertainty': 'policy_uncertainty',
            'consensus': 'policy_consensus',
            'polarization': 'policy_polarization',
            'urgency': 'policy_urgency'
        }
        
        category = category_mapping.get(signal.signal_type, 'policy_change')
        
        # Determine sentiment based on signal type
        if signal.signal_type == 'consensus':
            sentiment = 0.3  # Slightly positive
        elif signal.signal_type == 'polarization':
            sentiment = -0.2  # Slightly negative
        elif signal.signal_type == 'uncertainty':
            sentiment = -0.1  # Slightly negative
        else:
            sentiment = 0.0  # Neutral
        
        return Event(
            category=category,
            title=f"Policy {signal.signal_type} detected",
            description=signal.evidence,
            date=datetime.now(),
            jurisdiction=jurisdiction,
            sentiment=sentiment,
            confidence=signal.confidence
        )
    
    def _calculate_signal_adjustment(self, signal: PolicySignal) -> Dict[str, float]:
        """Calculate adjustment factors for a policy signal."""
        weights = self.impact_weights.get(signal.signal_type, {'magnitude': 0.2, 'timeframe': 'medium_term'})
        
        return {
            'magnitude': signal.intensity * weights['magnitude'],
            'confidence': signal.intensity * 0.3,
            'timeframe': weights['timeframe']
        }
    
    def get_policy_summary(self, policy_signals: List[PolicySignal]) -> Dict[str, Any]:
        """
        Get a summary of policy signals.
        
        Args:
            policy_signals: List of policy signals
            
        Returns:
            Dictionary with policy summary
        """
        if not policy_signals:
            return {
                'total_signals': 0,
                'signal_types': {},
                'overall_intensity': 0.0,
                'key_insights': []
            }
        
        # Count signal types
        signal_types = {}
        for signal in policy_signals:
            if signal.signal_type not in signal_types:
                signal_types[signal.signal_type] = 0
            signal_types[signal.signal_type] += 1
        
        # Calculate overall intensity
        overall_intensity = sum(signal.intensity for signal in policy_signals) / len(policy_signals)
        
        # Generate key insights
        key_insights = []
        for signal in policy_signals:
            if signal.intensity > 0.7:
                key_insights.append(f"High {signal.signal_type}: {signal.evidence}")
        
        return {
            'total_signals': len(policy_signals),
            'signal_types': signal_types,
            'overall_intensity': overall_intensity,
            'key_insights': key_insights
        }


















