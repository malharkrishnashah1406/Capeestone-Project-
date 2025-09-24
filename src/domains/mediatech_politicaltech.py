"""
MediaTech/PoliticalTech Startups Domain.

This domain analyzes media technology and political technology startups.
"""

from typing import Dict, List, Any
from .base import BaseDomain, Event, Shock


class MediaTechPoliticalTechDomain(BaseDomain):
    """Domain for analyzing media technology and political technology startups."""
    
    @property
    def key(self) -> str:
        return "mediatech_politicaltech"
    
    @property
    def name(self) -> str:
        return "MediaTech/PoliticalTech"
    
    @property
    def description(self) -> str:
        return "Analysis of media technology and political technology startups."
    
    def feature_spec(self) -> Dict[str, str]:
        return {
            "content_moderation_scale": "float - Content moderation scale (0-1)",
            "political_sensitivity": "float - Political sensitivity score (0-1)",
            "user_engagement_metrics": "dict - User engagement metrics",
            "content_volume": "int - Daily content volume",
            "moderation_accuracy": "float - Content moderation accuracy (0-1)",
            "political_bias_score": "float - Political bias score (-1 to 1)",
            "regulatory_compliance": "float - Regulatory compliance score (0-1)",
            "audience_diversity": "float - Audience diversity score (0-1)",
            "content_virality": "float - Content virality score (0-1)",
            "platform_trust_score": "float - Platform trust score (0-1)"
        }
    
    def extract_features(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract MediaTech/PoliticalTech specific features from input data."""
        features = {}
        
        features["content_moderation_scale"] = inputs.get("content_moderation_scale", 0.5)
        features["political_sensitivity"] = inputs.get("political_sensitivity", 0.6)
        features["user_engagement_metrics"] = inputs.get("user_engagement_metrics", {})
        features["content_volume"] = inputs.get("content_volume", 1000)
        features["moderation_accuracy"] = inputs.get("moderation_accuracy", 0.8)
        features["political_bias_score"] = inputs.get("political_bias_score", 0.0)
        features["regulatory_compliance"] = inputs.get("regulatory_compliance", 0.7)
        features["audience_diversity"] = inputs.get("audience_diversity", 0.6)
        features["content_virality"] = inputs.get("content_virality", 0.4)
        features["platform_trust_score"] = inputs.get("platform_trust_score", 0.7)
        
        return features
    
    def risk_factors(self) -> List[str]:
        return [
            "content_regulation",
            "political_censorship",
            "misinformation_spread",
            "user_privacy_violations",
            "platform_bias_allegations",
            "regulatory_crackdown",
            "audience_polarization",
            "content_virality_abuse"
        ]
    
    def map_events_to_shocks(self, events: List[Event]) -> List[Shock]:
        """Map events to MediaTech/PoliticalTech specific shocks."""
        shocks = []
        
        for event in events:
            if event.category in ["regulation", "content_policy"]:
                shocks.append(Shock(
                    type="content_regulation",
                    jurisdiction=event.jurisdiction,
                    intensity=min(0.9, abs(event.sentiment) * 0.9),
                    duration_days=180,
                    start_date=event.date,
                    confidence=event.confidence,
                    source_refs=[event.title]
                ))
        
        return shocks
    
    def simulate_response(self, features: Dict[str, Any], shocks: List[Shock]) -> Dict[str, float]:
        """Simulate MediaTech/PoliticalTech response to shocks."""
        content_risk = 0.3
        regulatory_risk = 0.2
        user_trust = features.get("platform_trust_score", 0.7)
        
        for shock in shocks:
            if shock.type == "content_regulation":
                content_risk += shock.intensity * 0.4
                regulatory_risk += shock.intensity * 0.3
                user_trust -= shock.intensity * 0.1
        
        return {
            "content_risk": min(1.0, content_risk),
            "regulatory_risk": min(1.0, regulatory_risk),
            "user_trust": max(0.0, min(1.0, user_trust)),
            "platform_stability": 0.6,
            "content_quality": 0.7
        }
    
    def reporting_metrics(self) -> List[str]:
        return [
            "content_risk",
            "regulatory_risk",
            "user_trust",
            "platform_stability",
            "content_quality"
        ]