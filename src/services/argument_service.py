"""
Argument Service.

This module provides business logic for argument mining and analysis.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from ..policy_argument_mining import (
    PolicyIngestion, PolicyPreprocessor,
    ClaimDetector, StanceDetector, ArgumentRoleLabeler,
    FrameMiner, EntityLinker, ArgumentGraph, ArgumentScorer,
    PolicyArgumentIntegrator
)

logger = logging.getLogger(__name__)


class ArgumentService:
    """Service for argument mining and analysis."""
    
    def __init__(self):
        self.ingestion = PolicyIngestion()
        self.preprocessor = PolicyPreprocessor()
        # self.segmenter = PolicySegmenter()  # TODO: Implement PolicySegmenter
        self.claim_detector = ClaimDetector()
        self.stance_detector = StanceDetector()
        self.role_labeler = ArgumentRoleLabeler()
        self.frame_miner = FrameMiner()
        self.entity_linker = EntityLinker()
        self.scorer = ArgumentScorer()
        self.integrator = PolicyArgumentIntegrator()
    
    def analyze_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a policy document for arguments and insights.
        
        Args:
            document_data: Document information including text and metadata
            
        Returns:
            Complete argument analysis
        """
        try:
            # Extract document information
            content = document_data.get('content', '')
            source = document_data.get('source', '')
            document_type = document_data.get('document_type', 'text')
            
            # Preprocess content
            preprocessed_content = self.preprocessor.preprocess_segment(content)
            
            # Segment content
            segments = self.segmenter.segment_text(preprocessed_content)
            
            # Detect claims
            claims = self.claim_detector.detect_claims(segments)
            
            # Detect stances
            stances = self.stance_detector.detect_stances_from_claims(claims)
            
            # Label argument roles
            roles = self.role_labeler.label_claim_roles(claims)
            
            # Detect frames
            frames = self.frame_miner.detect_frames_from_claims(claims)
            
            # Extract entities
            entities = self.entity_linker.extract_entities_from_claims(claims)
            
            # Score arguments
            scored_claims = []
            for claim in claims:
                score = self.scorer.score_claim(claim)
                scored_claims.append({
                    "claim": claim.claim_text,
                    "evidence": claim.evidence_text,
                    "claim_type": claim.claim_type,
                    "score": score.__dict__
                })
            
            # Build argument graph
            graph = self._build_argument_graph(claims, stances, entities, frames)
            
            # Generate insights
            insights = self._generate_insights(claims, stances, frames, entities)
            
            return {
                "document_id": document_data.get('id', ''),
                "source": source,
                "document_type": document_type,
                "analysis_timestamp": datetime.now().isoformat(),
                "summary": {
                    "num_claims": len(claims),
                    "num_stances": len(stances),
                    "num_frames": len(frames),
                    "num_entities": len(entities),
                    "num_segments": len(segments)
                },
                "claims": scored_claims,
                "stances": [stance.__dict__ for stance in stances],
                "frames": [frame.__dict__ for frame in frames],
                "entities": [entity.__dict__ for entity in entities],
                "argument_graph": graph,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            raise
    
    def _build_argument_graph(self, claims: List, stances: List, 
                            entities: List, frames: List) -> Dict[str, Any]:
        """Build argument graph from analysis results."""
        try:
            # Create graph structure
            nodes = []
            edges = []
            
            # Add claim nodes
            for i, claim in enumerate(claims):
                nodes.append({
                    "id": f"claim_{i}",
                    "type": "claim",
                    "text": claim.claim_text,
                    "claim_type": claim.claim_type,
                    "evidence": claim.evidence_text
                })
            
            # Add stance nodes
            for i, stance in enumerate(stances):
                nodes.append({
                    "id": f"stance_{i}",
                    "type": "stance",
                    "stance_label": stance.stance_label,
                    "stance_target": stance.stance_target,
                    "confidence": stance.confidence
                })
            
            # Add entity nodes
            for i, entity in enumerate(entities):
                nodes.append({
                    "id": f"entity_{i}",
                    "type": "entity",
                    "text": entity.text,
                    "entity_type": entity.entity_type,
                    "confidence": entity.confidence
                })
            
            # Add frame nodes
            for i, frame in enumerate(frames):
                nodes.append({
                    "id": f"frame_{i}",
                    "type": "frame",
                    "frame_label": frame.frame_label,
                    "salience": frame.salience,
                    "description": frame.description
                })
            
            # Add edges (simplified relationships)
            # Claims to stances
            for i, stance in enumerate(stances):
                if i < len(claims):
                    edges.append({
                        "from": f"claim_{i}",
                        "to": f"stance_{i}",
                        "relation": "supports" if stance.stance_label == "support" else "opposes"
                    })
            
            # Entities to claims
            for i, entity in enumerate(entities):
                if i < len(claims):
                    edges.append({
                        "from": f"entity_{i}",
                        "to": f"claim_{i}",
                        "relation": "mentions"
                    })
            
            # Frames to claims
            for i, frame in enumerate(frames):
                if i < len(claims):
                    edges.append({
                        "from": f"frame_{i}",
                        "to": f"claim_{i}",
                        "relation": "frames"
                    })
            
            return {
                "nodes": nodes,
                "edges": edges,
                "statistics": {
                    "total_nodes": len(nodes),
                    "total_edges": len(edges),
                    "node_types": {
                        "claim": len([n for n in nodes if n["type"] == "claim"]),
                        "stance": len([n for n in nodes if n["type"] == "stance"]),
                        "entity": len([n for n in nodes if n["type"] == "entity"]),
                        "frame": len([n for n in nodes if n["type"] == "frame"])
                    }
                }
            }
            
        except Exception as e:
            logger.warning(f"Error building argument graph: {e}")
            return {
                "nodes": [],
                "edges": [],
                "statistics": {
                    "total_nodes": 0,
                    "total_edges": 0,
                    "node_types": {}
                }
            }
    
    def _generate_insights(self, claims: List, stances: List, 
                         frames: List, entities: List) -> Dict[str, Any]:
        """Generate insights from argument analysis."""
        try:
            insights = {
                "key_themes": [],
                "stakeholder_sentiment": {},
                "argument_strength": {},
                "policy_implications": [],
                "risk_indicators": {}
            }
            
            # Extract key themes from frames
            frame_labels = [frame.frame_label for frame in frames]
            insights["key_themes"] = list(set(frame_labels))
            
            # Analyze stakeholder sentiment
            stance_distribution = {}
            for stance in stances:
                label = stance.stance_label
                if label not in stance_distribution:
                    stance_distribution[label] = 0
                stance_distribution[label] += 1
            
            insights["stakeholder_sentiment"] = stance_distribution
            
            # Analyze argument strength
            claim_types = [claim.claim_type for claim in claims]
            type_distribution = {}
            for claim_type in claim_types:
                if claim_type not in type_distribution:
                    type_distribution[claim_type] = 0
                type_distribution[claim_type] += 1
            
            insights["argument_strength"] = {
                "claim_type_distribution": type_distribution,
                "total_claims": len(claims),
                "average_evidence_length": sum(len(claim.evidence_text) for claim in claims) / len(claims) if claims else 0
            }
            
            # Generate policy implications
            implications = []
            if len(stances) > 0:
                support_count = stance_distribution.get("support", 0)
                oppose_count = stance_distribution.get("oppose", 0)
                
                if support_count > oppose_count:
                    implications.append("Policy appears to have broad support")
                elif oppose_count > support_count:
                    implications.append("Policy faces significant opposition")
                else:
                    implications.append("Policy has mixed stakeholder sentiment")
            
            if "economic_growth" in frame_labels:
                implications.append("Economic considerations are prominent")
            
            if "consumer_protection" in frame_labels:
                implications.append("Consumer protection concerns are raised")
            
            insights["policy_implications"] = implications
            
            # Identify risk indicators
            risk_indicators = {}
            
            # High opposition indicates implementation risk
            if stance_distribution.get("oppose", 0) > stance_distribution.get("support", 0):
                risk_indicators["implementation_risk"] = "high"
            
            # Multiple frames suggest complex policy
            if len(frame_labels) > 3:
                risk_indicators["complexity_risk"] = "high"
            
            # Lack of evidence suggests weak arguments
            weak_evidence_count = sum(1 for claim in claims if len(claim.evidence_text) < 50)
            if weak_evidence_count > len(claims) * 0.5:
                risk_indicators["evidence_quality_risk"] = "high"
            
            insights["risk_indicators"] = risk_indicators
            
            return insights
            
        except Exception as e:
            logger.warning(f"Error generating insights: {e}")
            return {
                "key_themes": [],
                "stakeholder_sentiment": {},
                "argument_strength": {},
                "policy_implications": [],
                "risk_indicators": {}
            }
    
    def compare_documents(self, document_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple document analyses.
        
        Args:
            document_analyses: List of document analysis results
            
        Returns:
            Comparison results
        """
        try:
            if len(document_analyses) < 2:
                raise ValueError("Need at least 2 documents to compare")
            
            comparison = {
                "num_documents": len(document_analyses),
                "comparison_timestamp": datetime.now().isoformat(),
                "summary_comparison": {},
                "theme_comparison": {},
                "sentiment_comparison": {},
                "risk_comparison": {}
            }
            
            # Compare summaries
            total_claims = sum(analysis["summary"]["num_claims"] for analysis in document_analyses)
            total_stances = sum(analysis["summary"]["num_stances"] for analysis in document_analyses)
            
            comparison["summary_comparison"] = {
                "total_claims": total_claims,
                "total_stances": total_stances,
                "average_claims_per_document": total_claims / len(document_analyses),
                "average_stances_per_document": total_stances / len(document_analyses)
            }
            
            # Compare themes
            all_themes = set()
            for analysis in document_analyses:
                themes = analysis.get("insights", {}).get("key_themes", [])
                all_themes.update(themes)
            
            theme_frequency = {}
            for theme in all_themes:
                theme_frequency[theme] = sum(
                    1 for analysis in document_analyses 
                    if theme in analysis.get("insights", {}).get("key_themes", [])
                )
            
            comparison["theme_comparison"] = {
                "all_themes": list(all_themes),
                "theme_frequency": theme_frequency,
                "most_common_themes": sorted(theme_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
            }
            
            # Compare sentiment
            overall_sentiment = {"support": 0, "oppose": 0, "neutral": 0}
            for analysis in document_analyses:
                sentiment = analysis.get("insights", {}).get("stakeholder_sentiment", {})
                for stance, count in sentiment.items():
                    if stance in overall_sentiment:
                        overall_sentiment[stance] += count
            
            comparison["sentiment_comparison"] = {
                "overall_sentiment": overall_sentiment,
                "sentiment_distribution": {
                    stance: count / sum(overall_sentiment.values()) if sum(overall_sentiment.values()) > 0 else 0
                    for stance, count in overall_sentiment.items()
                }
            }
            
            # Compare risk indicators
            risk_summary = {}
            for analysis in document_analyses:
                risk_indicators = analysis.get("insights", {}).get("risk_indicators", {})
                for risk_type, risk_level in risk_indicators.items():
                    if risk_type not in risk_summary:
                        risk_summary[risk_type] = {"high": 0, "medium": 0, "low": 0}
                    risk_summary[risk_type][risk_level] += 1
            
            comparison["risk_comparison"] = {
                "risk_summary": risk_summary,
                "overall_risk_assessment": self._calculate_overall_risk_assessment(risk_summary)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing documents: {e}")
            raise
    
    def _calculate_overall_risk_assessment(self, risk_summary: Dict[str, Any]) -> str:
        """Calculate overall risk assessment from risk summary."""
        try:
            total_high_risks = 0
            total_risks = 0
            
            for risk_type, risk_counts in risk_summary.items():
                total_high_risks += risk_counts.get("high", 0)
                total_risks += sum(risk_counts.values())
            
            if total_risks == 0:
                return "low"
            
            high_risk_ratio = total_high_risks / total_risks
            
            if high_risk_ratio > 0.5:
                return "high"
            elif high_risk_ratio > 0.2:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            logger.warning(f"Error calculating overall risk assessment: {e}")
            return "unknown"
    
    def get_argument_statistics(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about argument analyses.
        
        Args:
            analyses: List of argument analyses
            
        Returns:
            Statistics summary
        """
        try:
            if not analyses:
                return {
                    "total_analyses": 0,
                    "total_claims": 0,
                    "total_stances": 0,
                    "total_frames": 0,
                    "total_entities": 0
                }
            
            total_claims = sum(analysis["summary"]["num_claims"] for analysis in analyses)
            total_stances = sum(analysis["summary"]["num_stances"] for analysis in analyses)
            total_frames = sum(analysis["summary"]["num_frames"] for analysis in analyses)
            total_entities = sum(analysis["summary"]["num_entities"] for analysis in analyses)
            
            # Calculate averages
            num_analyses = len(analyses)
            
            statistics = {
                "total_analyses": num_analyses,
                "total_claims": total_claims,
                "total_stances": total_stances,
                "total_frames": total_frames,
                "total_entities": total_entities,
                "averages": {
                    "claims_per_analysis": total_claims / num_analyses,
                    "stances_per_analysis": total_stances / num_analyses,
                    "frames_per_analysis": total_frames / num_analyses,
                    "entities_per_analysis": total_entities / num_analyses
                },
                "distributions": {
                    "stance_distribution": self._calculate_stance_distribution(analyses),
                    "frame_distribution": self._calculate_frame_distribution(analyses),
                    "claim_type_distribution": self._calculate_claim_type_distribution(analyses)
                }
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting argument statistics: {e}")
            raise
    
    def _calculate_stance_distribution(self, analyses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate stance distribution across analyses."""
        stance_counts = {"support": 0, "oppose": 0, "neutral": 0}
        
        for analysis in analyses:
            sentiment = analysis.get("insights", {}).get("stakeholder_sentiment", {})
            for stance, count in sentiment.items():
                if stance in stance_counts:
                    stance_counts[stance] += count
        
        return stance_counts
    
    def _calculate_frame_distribution(self, analyses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate frame distribution across analyses."""
        frame_counts = {}
        
        for analysis in analyses:
            themes = analysis.get("insights", {}).get("key_themes", [])
            for theme in themes:
                if theme not in frame_counts:
                    frame_counts[theme] = 0
                frame_counts[theme] += 1
        
        return frame_counts
    
    def _calculate_claim_type_distribution(self, analyses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate claim type distribution across analyses."""
        claim_type_counts = {}
        
        for analysis in analyses:
            argument_strength = analysis.get("insights", {}).get("argument_strength", {})
            type_distribution = argument_strength.get("claim_type_distribution", {})
            
            for claim_type, count in type_distribution.items():
                if claim_type not in claim_type_counts:
                    claim_type_counts[claim_type] = 0
                claim_type_counts[claim_type] += count
        
        return claim_type_counts
