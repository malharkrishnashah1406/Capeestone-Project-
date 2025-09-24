"""
Research Package.

This package contains advanced research functionalities for startup performance
prediction and risk assessment, including hybrid modeling, causal inference,
graph networks, and multimodal data fusion.
"""

from .hybrid_models import HybridModelEngine, SurvivalData, ModelComparison
from .causal_inference import CausalInferenceEngine, CausalEffect, CounterfactualScenario
from .graph_networks import (
    TemporalKnowledgeGraph, ShockPropagationEngine, 
    GraphNode, GraphEdge, ShockPropagation
)
from .multimodal_fusion import (
    MultimodalDataFusion, DataSource, 
    EmbeddingResult, FusionResult
)

__all__ = [
    # Hybrid Models
    'HybridModelEngine',
    'SurvivalData', 
    'ModelComparison',
    
    # Causal Inference
    'CausalInferenceEngine',
    'CausalEffect',
    'CounterfactualScenario',
    
    # Graph Networks
    'TemporalKnowledgeGraph',
    'ShockPropagationEngine',
    'GraphNode',
    'GraphEdge',
    'ShockPropagation',
    
    # Multimodal Fusion
    'MultimodalDataFusion',
    'DataSource',
    'EmbeddingResult',
    'FusionResult'
]

__version__ = "1.0.0"
__author__ = "Startup Performance Prediction System"
__description__ = "Advanced research functionalities for startup risk assessment"








