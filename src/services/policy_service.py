"""
Policy Service.

This module provides business logic for policy analysis and impact assessment.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import hashlib

from ..policy_argument_mining import PolicyArgumentIntegrator
from ..simulation.shocks import ShockGenerator
from ..utils.registry import get_domain

logger = logging.getLogger(__name__)


class PolicyService:
    """Service for policy analysis and impact assessment."""
    
    def __init__(self):
        self.argument_integrator = PolicyArgumentIntegrator()
        self.shock_generator = ShockGenerator()
    
    def analyze_policy_impact(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the impact of a policy on different domains.
        
        Args:
            policy_data: Policy information including text and metadata
            
        Returns:
            Policy impact analysis
        """
        try:
            # Extract policy text and metadata
            policy_text = policy_data.get('body_text', '')
            policy_title = policy_data.get('title', '')
            jurisdiction = policy_data.get('jurisdiction', '')
            policy_type = policy_data.get('policy_type', '')
            
            # Analyze policy arguments
            argument_analysis = self._analyze_policy_arguments(policy_text)
            
            # Identify affected domains
            affected_domains = self._identify_affected_domains(policy_text, argument_analysis)
            
            # Generate policy-specific shocks
            policy_shocks = self._generate_policy_shocks(policy_data, argument_analysis)
            
            # Assess impact on each domain
            domain_impacts = {}
            for domain_key in affected_domains:
                try:
                    domain_impact = self._assess_domain_impact(domain_key, policy_data, argument_analysis, policy_shocks)
                    domain_impacts[domain_key] = domain_impact
                except Exception as e:
                    logger.warning(f"Failed to assess impact for domain {domain_key}: {e}")
                    domain_impacts[domain_key] = {"error": str(e)}
            
            # Calculate overall impact metrics
            overall_impact = self._calculate_overall_impact(domain_impacts, argument_analysis)
            
            return {
                "policy_id": policy_data.get('id', ''),
                "policy_title": policy_title,
                "jurisdiction": jurisdiction,
                "policy_type": policy_type,
                "argument_analysis": argument_analysis,
                "affected_domains": affected_domains,
                "policy_shocks": policy_shocks,
                "domain_impacts": domain_impacts,
                "overall_impact": overall_impact,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing policy impact: {e}")
            raise
    
    def _analyze_policy_arguments(self, policy_text: str) -> Dict[str, Any]:
        """Analyze arguments in policy text."""
        try:
            # Use the policy argument integrator to analyze the text
            policy_signals = self.argument_integrator.analyze_policy_arguments(policy_text)
            
            # Convert to analysis format
            analysis = {
                "uncertainty_index": policy_signals.uncertainty_index,
                "consensus_level": policy_signals.consensus_level,
                "polarization_index": policy_signals.polarization_index,
                "urgency_score": policy_signals.urgency_score,
                "confidence": policy_signals.confidence,
                "key_themes": policy_signals.key_themes,
                "stakeholder_sentiment": policy_signals.stakeholder_sentiment
            }
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Error analyzing policy arguments: {e}")
            # Return default analysis
            return {
                "uncertainty_index": 0.5,
                "consensus_level": 0.5,
                "polarization_index": 0.5,
                "urgency_score": 0.5,
                "confidence": 0.5,
                "key_themes": [],
                "stakeholder_sentiment": "neutral"
            }
    
    def _identify_affected_domains(self, policy_text: str, argument_analysis: Dict[str, Any]) -> List[str]:
        """Identify domains that are likely to be affected by the policy."""
        # Define domain keywords for identification
        domain_keywords = {
            'venture_capital': ['fund', 'investment', 'portfolio', 'dry powder', 'exit', 'liquidity'],
            'accelerators': ['accelerator', 'incubator', 'startup', 'cohort', 'mentor'],
            'saas': ['software', 'subscription', 'arr', 'churn', 'cac', 'ltv'],
            'fintech': ['financial', 'banking', 'payment', 'regulatory', 'compliance', 'aml'],
            'healthtech_biotech': ['healthcare', 'medical', 'clinical', 'trial', 'fda', 'approval'],
            'greentech': ['climate', 'carbon', 'renewable', 'energy', 'sustainability', 'esg'],
            'regtech_policy': ['regulation', 'compliance', 'policy', 'legal', 'regulatory'],
            'cross_border': ['international', 'global', 'trade', 'tariff', 'sanction', 'currency'],
            'public_sector_funded': ['government', 'public', 'grant', 'procurement', 'budget'],
            'mediatech_politicaltech': ['media', 'content', 'platform', 'election', 'campaign', 'advertising']
        }
        
        policy_text_lower = policy_text.lower()
        affected_domains = []
        
        for domain_key, keywords in domain_keywords.items():
            # Check if any keywords are present in the policy text
            keyword_matches = sum(1 for keyword in keywords if keyword in policy_text_lower)
            
            # If multiple keywords match, consider the domain affected
            if keyword_matches >= 2:
                affected_domains.append(domain_key)
        
        # If no specific domains identified, return common domains
        if not affected_domains:
            affected_domains = ['venture_capital', 'fintech', 'regtech_policy']
        
        return affected_domains
    
    def _generate_policy_shocks(self, policy_data: Dict[str, Any], 
                              argument_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate policy-specific shocks based on analysis."""
        try:
            shocks = []
            
            # Determine shock intensity based on argument analysis
            urgency_score = argument_analysis.get('urgency_score', 0.5)
            uncertainty_index = argument_analysis.get('uncertainty_index', 0.5)
            
            # Base shock intensity on urgency and uncertainty
            base_intensity = (urgency_score + uncertainty_index) / 2
            
            # Generate regulatory change shock
            regulatory_shock = {
                "type": "regulatory_change",
                "jurisdiction": policy_data.get('jurisdiction', 'US'),
                "intensity": base_intensity,
                "duration_days": int(180 + base_intensity * 365),  # 6-18 months
                "confidence": 0.7 + base_intensity * 0.2,
                "description": f"Policy change: {policy_data.get('title', 'Unknown policy')}",
                "source_refs": [f"Policy: {policy_data.get('id', 'unknown')}"]
            }
            shocks.append(regulatory_shock)
            
            # Add market impact shock if high urgency
            if urgency_score > 0.7:
                market_shock = {
                    "type": "market_crash",
                    "jurisdiction": policy_data.get('jurisdiction', 'US'),
                    "intensity": urgency_score * 0.8,
                    "duration_days": int(30 + urgency_score * 60),
                    "confidence": 0.6 + urgency_score * 0.2,
                    "description": "Market reaction to policy change",
                    "source_refs": [f"Policy: {policy_data.get('id', 'unknown')}"]
                }
                shocks.append(market_shock)
            
            return shocks
            
        except Exception as e:
            logger.warning(f"Error generating policy shocks: {e}")
            # Return default shock
            return [{
                "type": "regulatory_change",
                "jurisdiction": policy_data.get('jurisdiction', 'US'),
                "intensity": 0.5,
                "duration_days": 365,
                "confidence": 0.7,
                "description": "Policy change",
                "source_refs": [f"Policy: {policy_data.get('id', 'unknown')}"]
            }]
    
    def _assess_domain_impact(self, domain_key: str, policy_data: Dict[str, Any], 
                            argument_analysis: Dict[str, Any], 
                            policy_shocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess the impact of a policy on a specific domain."""
        try:
            # Get domain information
            domain = get_domain(domain_key)
            
            # Create sample features for the domain
            sample_features = self._generate_sample_features(domain_key)
            
            # Convert shocks to domain-specific impact
            domain_impact = {
                "domain_key": domain_key,
                "domain_name": domain.name,
                "risk_level": self._calculate_risk_level(argument_analysis, policy_shocks),
                "impact_metrics": self._calculate_impact_metrics(domain_key, sample_features, policy_shocks),
                "compliance_requirements": self._identify_compliance_requirements(domain_key, policy_data),
                "implementation_timeline": self._estimate_implementation_timeline(domain_key, policy_data),
                "cost_estimates": self._estimate_costs(domain_key, policy_data),
                "recommendations": self._generate_recommendations(domain_key, argument_analysis)
            }
            
            return domain_impact
            
        except Exception as e:
            logger.error(f"Error assessing domain impact for {domain_key}: {e}")
            raise
    
    def _generate_sample_features(self, domain_key: str) -> Dict[str, Any]:
        """Generate sample features for a domain."""
        # This would typically come from actual domain data
        # For now, return sample features based on domain
        sample_features = {
            'venture_capital': {
                'dry_powder': 0.6,
                'fund_age_years': 3,
                'sector_exposure': {'tech': 0.4, 'fintech': 0.3, 'health': 0.3},
                'follow_on_rate': 0.7
            },
            'fintech': {
                'regulatory_burden_index': 0.7,
                'fraud_rate': 0.02,
                'kyc_cost_per_user': 15,
                'interchange_yield': 0.03
            },
            'saas': {
                'arr': 1000000,
                'ndr': 0.95,
                'gross_churn': 0.05,
                'cac': 500
            }
        }
        
        return sample_features.get(domain_key, {})
    
    def _calculate_risk_level(self, argument_analysis: Dict[str, Any], 
                            policy_shocks: List[Dict[str, Any]]) -> str:
        """Calculate overall risk level."""
        # Combine uncertainty, urgency, and shock intensity
        uncertainty = argument_analysis.get('uncertainty_index', 0.5)
        urgency = argument_analysis.get('urgency_score', 0.5)
        max_shock_intensity = max((shock.get('intensity', 0) for shock in policy_shocks), default=0.5)
        
        # Calculate risk score
        risk_score = (uncertainty + urgency + max_shock_intensity) / 3
        
        if risk_score > 0.7:
            return "high"
        elif risk_score > 0.4:
            return "medium"
        else:
            return "low"
    
    def _calculate_impact_metrics(self, domain_key: str, features: Dict[str, Any], 
                                policy_shocks: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate impact metrics for a domain."""
        # This would use the domain's simulation capabilities
        # For now, return estimated impacts based on shock intensity
        max_intensity = max((shock.get('intensity', 0) for shock in policy_shocks), default=0.5)
        
        impact_metrics = {
            "revenue_impact": -max_intensity * 0.15,  # 15% reduction at max intensity
            "cost_impact": max_intensity * 0.25,      # 25% increase at max intensity
            "timeline_impact": max_intensity * 0.3,   # 30% delay at max intensity
            "compliance_risk": max_intensity * 0.8,   # 80% compliance risk at max intensity
            "market_risk": max_intensity * 0.6        # 60% market risk at max intensity
        }
        
        return impact_metrics
    
    def _identify_compliance_requirements(self, domain_key: str, 
                                        policy_data: Dict[str, Any]) -> List[str]:
        """Identify compliance requirements for a domain."""
        # This would analyze the policy text for specific requirements
        # For now, return sample requirements
        requirements = [
            "Review and update compliance procedures",
            "Conduct impact assessment",
            "Update documentation and reporting",
            "Train staff on new requirements",
            "Implement monitoring and controls"
        ]
        
        # Add domain-specific requirements
        if domain_key == 'fintech':
            requirements.extend([
                "Update AML/KYC procedures",
                "Review transaction monitoring",
                "Assess capital adequacy requirements"
            ])
        elif domain_key == 'healthtech_biotech':
            requirements.extend([
                "Review clinical trial protocols",
                "Update regulatory submissions",
                "Assess approval timelines"
            ])
        
        return requirements
    
    def _estimate_implementation_timeline(self, domain_key: str, 
                                        policy_data: Dict[str, Any]) -> Dict[str, int]:
        """Estimate implementation timeline for a domain."""
        # Base timeline estimates
        base_timeline = {
            "assessment_phase": 30,      # days
            "planning_phase": 60,        # days
            "implementation_phase": 180,  # days
            "testing_phase": 45,         # days
            "deployment_phase": 30       # days
        }
        
        # Adjust based on domain complexity
        if domain_key in ['fintech', 'healthtech_biotech']:
            # More complex domains need more time
            for phase in base_timeline:
                base_timeline[phase] = int(base_timeline[phase] * 1.5)
        
        return base_timeline
    
    def _estimate_costs(self, domain_key: str, policy_data: Dict[str, Any]) -> Dict[str, float]:
        """Estimate implementation costs for a domain."""
        # Base cost estimates (in thousands of USD)
        base_costs = {
            "consulting_fees": 50,
            "technology_updates": 100,
            "staff_training": 25,
            "compliance_monitoring": 30,
            "legal_review": 40,
            "total_estimated": 245
        }
        
        # Adjust based on domain
        if domain_key == 'fintech':
            base_costs["total_estimated"] *= 1.5
        elif domain_key == 'healthtech_biotech':
            base_costs["total_estimated"] *= 2.0
        
        return base_costs
    
    def _generate_recommendations(self, domain_key: str, 
                                argument_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations for a domain."""
        recommendations = [
            "Monitor policy developments closely",
            "Engage with regulatory authorities",
            "Conduct thorough impact assessment",
            "Develop contingency plans"
        ]
        
        # Add recommendations based on analysis
        if argument_analysis.get('uncertainty_index', 0.5) > 0.7:
            recommendations.append("Prepare for multiple policy scenarios")
        
        if argument_analysis.get('urgency_score', 0.5) > 0.7:
            recommendations.append("Accelerate compliance preparations")
        
        if argument_analysis.get('polarization_index', 0.5) > 0.7:
            recommendations.append("Engage in policy advocacy and stakeholder outreach")
        
        return recommendations
    
    def _calculate_overall_impact(self, domain_impacts: Dict[str, Any], 
                                argument_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall impact across all affected domains."""
        try:
            # Aggregate impact metrics
            total_revenue_impact = 0
            total_cost_impact = 0
            high_risk_domains = 0
            total_estimated_cost = 0
            
            for domain_impact in domain_impacts.values():
                if isinstance(domain_impact, dict) and 'impact_metrics' in domain_impact:
                    metrics = domain_impact['impact_metrics']
                    total_revenue_impact += metrics.get('revenue_impact', 0)
                    total_cost_impact += metrics.get('cost_impact', 0)
                    
                    if domain_impact.get('risk_level') == 'high':
                        high_risk_domains += 1
                    
                    if 'cost_estimates' in domain_impact:
                        total_estimated_cost += domain_impact['cost_estimates'].get('total_estimated', 0)
            
            num_domains = len(domain_impacts)
            if num_domains > 0:
                avg_revenue_impact = total_revenue_impact / num_domains
                avg_cost_impact = total_cost_impact / num_domains
            else:
                avg_revenue_impact = 0
                avg_cost_impact = 0
            
            overall_impact = {
                "affected_domains_count": num_domains,
                "high_risk_domains_count": high_risk_domains,
                "average_revenue_impact": avg_revenue_impact,
                "average_cost_impact": avg_cost_impact,
                "total_estimated_implementation_cost": total_estimated_cost,
                "overall_risk_level": self._calculate_overall_risk_level(domain_impacts),
                "policy_confidence": argument_analysis.get('confidence', 0.5),
                "implementation_priority": self._calculate_implementation_priority(argument_analysis)
            }
            
            return overall_impact
            
        except Exception as e:
            logger.error(f"Error calculating overall impact: {e}")
            return {
                "affected_domains_count": 0,
                "high_risk_domains_count": 0,
                "average_revenue_impact": 0,
                "average_cost_impact": 0,
                "total_estimated_implementation_cost": 0,
                "overall_risk_level": "unknown",
                "policy_confidence": 0.5,
                "implementation_priority": "medium"
            }
    
    def _calculate_overall_risk_level(self, domain_impacts: Dict[str, Any]) -> str:
        """Calculate overall risk level across domains."""
        high_risk_count = sum(1 for impact in domain_impacts.values() 
                             if isinstance(impact, dict) and impact.get('risk_level') == 'high')
        total_count = len(domain_impacts)
        
        if total_count == 0:
            return "unknown"
        
        high_risk_ratio = high_risk_count / total_count
        
        if high_risk_ratio > 0.5:
            return "high"
        elif high_risk_ratio > 0.2:
            return "medium"
        else:
            return "low"
    
    def _calculate_implementation_priority(self, argument_analysis: Dict[str, Any]) -> str:
        """Calculate implementation priority based on analysis."""
        urgency = argument_analysis.get('urgency_score', 0.5)
        uncertainty = argument_analysis.get('uncertainty_index', 0.5)
        
        if urgency > 0.7 and uncertainty < 0.4:
            return "high"
        elif urgency > 0.5 or uncertainty < 0.6:
            return "medium"
        else:
            return "low"








