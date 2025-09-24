"""
Argument Graph Module.

This module builds and manages argument graphs from policy debates,
connecting arguments, stances, and entities.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from .ingestion import DebateSegment
from .claim_detection import Claim
from .stance_detection import Stance
from .argument_role_labeling import ArgumentRole
from .frame_mining import Frame
from .entity_linking import Entity
import networkx as nx
import logging

logger = logging.getLogger(__name__)


@dataclass
class ArgumentNode:
    """Represents a node in the argument graph."""
    node_id: str
    node_type: str  # claim, stance, entity, frame
    content: Any  # Claim, Stance, Entity, or Frame object
    confidence: float
    source_segment: DebateSegment


@dataclass
class ArgumentEdge:
    """Represents an edge in the argument graph."""
    from_node_id: str
    to_node_id: str
    relation: str  # supports, attacks, rebuts, undercuts, mentions, frames
    confidence: float
    evidence: str


class ArgumentGraph:
    """Builds and manages argument graphs from policy debates."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, ArgumentNode] = {}
        self.edges: List[ArgumentEdge] = []
        self.node_counter = 0
    
    def add_claim(self, claim: Claim) -> str:
        """
        Add a claim to the graph.
        
        Args:
            claim: Claim to add
            
        Returns:
            Node ID of the added claim
        """
        node_id = f"claim_{self.node_counter}"
        self.node_counter += 1
        
        node = ArgumentNode(
            node_id=node_id,
            node_type="claim",
            content=claim,
            confidence=claim.confidence,
            source_segment=claim.source_segment
        )
        
        self.nodes[node_id] = node
        self.graph.add_node(node_id, **node.__dict__)
        
        return node_id
    
    def add_stance(self, stance: Stance) -> str:
        """
        Add a stance to the graph.
        
        Args:
            stance: Stance to add
            
        Returns:
            Node ID of the added stance
        """
        node_id = f"stance_{self.node_counter}"
        self.node_counter += 1
        
        node = ArgumentNode(
            node_id=node_id,
            node_type="stance",
            content=stance,
            confidence=stance.confidence,
            source_segment=stance.source_segment
        )
        
        self.nodes[node_id] = node
        self.graph.add_node(node_id, **node.__dict__)
        
        return node_id
    
    def add_entity(self, entity: Entity) -> str:
        """
        Add an entity to the graph.
        
        Args:
            entity: Entity to add
            
        Returns:
            Node ID of the added entity
        """
        node_id = f"entity_{self.node_counter}"
        self.node_counter += 1
        
        node = ArgumentNode(
            node_id=node_id,
            node_type="entity",
            content=entity,
            confidence=entity.confidence,
            source_segment=entity.source_segment
        )
        
        self.nodes[node_id] = node
        self.graph.add_node(node_id, **node.__dict__)
        
        return node_id
    
    def add_frame(self, frame: Frame) -> str:
        """
        Add a frame to the graph.
        
        Args:
            frame: Frame to add
            
        Returns:
            Node ID of the added frame
        """
        node_id = f"frame_{self.node_counter}"
        self.node_counter += 1
        
        node = ArgumentNode(
            node_id=node_id,
            node_type="frame",
            content=frame,
            confidence=frame.confidence,
            source_segment=frame.source_segment
        )
        
        self.nodes[node_id] = node
        self.graph.add_node(node_id, **node.__dict__)
        
        return node_id
    
    def add_edge(self, from_node_id: str, to_node_id: str, relation: str, confidence: float = 0.5, evidence: str = "") -> None:
        """
        Add an edge to the graph.
        
        Args:
            from_node_id: Source node ID
            to_node_id: Target node ID
            relation: Type of relation
            confidence: Confidence in the relation
            evidence: Evidence for the relation
        """
        if from_node_id not in self.nodes or to_node_id not in self.nodes:
            logger.warning(f"Attempting to add edge between non-existent nodes: {from_node_id} -> {to_node_id}")
            return
        
        edge = ArgumentEdge(
            from_node_id=from_node_id,
            to_node_id=to_node_id,
            relation=relation,
            confidence=confidence,
            evidence=evidence
        )
        
        self.edges.append(edge)
        self.graph.add_edge(from_node_id, to_node_id, **edge.__dict__)
    
    def build_graph_from_segments(self, segments: List[DebateSegment], claims: List[Claim], 
                                 stances: List[Stance], entities: List[Entity], frames: List[Frame]) -> None:
        """
        Build argument graph from all components.
        
        Args:
            segments: List of debate segments
            claims: List of claims
            stances: List of stances
            entities: List of entities
            frames: List of frames
        """
        # Add all nodes
        claim_nodes = {}
        stance_nodes = {}
        entity_nodes = {}
        frame_nodes = {}
        
        for claim in claims:
            node_id = self.add_claim(claim)
            claim_nodes[claim] = node_id
        
        for stance in stances:
            node_id = self.add_stance(stance)
            stance_nodes[stance] = node_id
        
        for entity in entities:
            node_id = self.add_entity(entity)
            entity_nodes[entity] = node_id
        
        for frame in frames:
            node_id = self.add_frame(frame)
            frame_nodes[frame] = node_id
        
        # Add edges based on relationships
        self._add_claim_stance_edges(claim_nodes, stance_nodes)
        self._add_entity_mention_edges(claim_nodes, entity_nodes)
        self._add_frame_edges(claim_nodes, frame_nodes)
        self._add_argument_edges(claim_nodes)
    
    def _add_claim_stance_edges(self, claim_nodes: Dict[Claim, str], stance_nodes: Dict[Stance, str]) -> None:
        """Add edges between claims and stances."""
        for claim, claim_id in claim_nodes.items():
            for stance, stance_id in stance_nodes.items():
                # Check if stance is about the same target as claim
                if stance.stance_target.lower() in claim.text.lower():
                    relation = "supports" if stance.stance_label == "support" else "attacks"
                    self.add_edge(claim_id, stance_id, relation, stance.confidence, stance.evidence_text)
    
    def _add_entity_mention_edges(self, claim_nodes: Dict[Claim, str], entity_nodes: Dict[Entity, str]) -> None:
        """Add edges between claims and entities they mention."""
        for claim, claim_id in claim_nodes.items():
            for entity, entity_id in entity_nodes.items():
                if entity.name.lower() in claim.text.lower():
                    self.add_edge(claim_id, entity_id, "mentions", entity.confidence, entity.source_text)
    
    def _add_frame_edges(self, claim_nodes: Dict[Claim, str], frame_nodes: Dict[Frame, str]) -> None:
        """Add edges between claims and frames."""
        for claim, claim_id in claim_nodes.items():
            for frame, frame_id in frame_nodes.items():
                if frame.evidence_text.lower() in claim.text.lower():
                    self.add_edge(claim_id, frame_id, "frames", frame.confidence, frame.evidence_text)
    
    def _add_argument_edges(self, claim_nodes: Dict[Claim, str]) -> None:
        """Add edges between related claims."""
        claims = list(claim_nodes.keys())
        
        for i, claim1 in enumerate(claims):
            for j, claim2 in enumerate(claims[i+1:], i+1):
                # Check for semantic similarity (simple keyword overlap)
                similarity = self._calculate_similarity(claim1.text, claim2.text)
                if similarity > 0.3:
                    relation = "supports" if similarity > 0.6 else "related"
                    self.add_edge(claim_nodes[claim1], claim_nodes[claim2], relation, similarity, "semantic similarity")
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple similarity between two texts."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the argument graph.
        
        Returns:
            Dictionary with graph statistics
        """
        stats = {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'node_types': {},
            'edge_types': {},
            'connected_components': nx.number_strongly_connected_components(self.graph),
            'density': nx.density(self.graph),
            'average_clustering': nx.average_clustering(self.graph.to_undirected()) if self.graph.nodes() else 0
        }
        
        # Count node types
        for node in self.nodes.values():
            if node.node_type not in stats['node_types']:
                stats['node_types'][node.node_type] = 0
            stats['node_types'][node.node_type] += 1
        
        # Count edge types
        for edge in self.edges:
            if edge.relation not in stats['edge_types']:
                stats['edge_types'][edge.relation] = 0
            stats['edge_types'][edge.relation] += 1
        
        return stats
    
    def get_subgraph(self, node_ids: List[str]) -> 'ArgumentGraph':
        """
        Get a subgraph containing only specified nodes.
        
        Args:
            node_ids: List of node IDs to include
            
        Returns:
            New ArgumentGraph with only specified nodes
        """
        subgraph = ArgumentGraph()
        
        # Add nodes
        for node_id in node_ids:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                subgraph.nodes[node_id] = node
                subgraph.graph.add_node(node_id, **node.__dict__)
        
        # Add edges
        for edge in self.edges:
            if edge.from_node_id in node_ids and edge.to_node_id in node_ids:
                subgraph.edges.append(edge)
                subgraph.graph.add_edge(edge.from_node_id, edge.to_node_id, **edge.__dict__)
        
        return subgraph
    
    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export graph to dictionary format.
        
        Returns:
            Dictionary representation of the graph
        """
        return {
            'nodes': {node_id: {
                'node_type': node.node_type,
                'confidence': node.confidence,
                'content': str(node.content)
            } for node_id, node in self.nodes.items()},
            'edges': [{
                'from_node': edge.from_node_id,
                'to_node': edge.to_node_id,
                'relation': edge.relation,
                'confidence': edge.confidence,
                'evidence': edge.evidence
            } for edge in self.edges],
            'statistics': self.get_graph_statistics()
        }
    
    def get_central_nodes(self, top_k: int = 5) -> List[str]:
        """
        Get the most central nodes in the graph.
        
        Args:
            top_k: Number of top nodes to return
            
        Returns:
            List of node IDs ordered by centrality
        """
        if not self.graph.nodes():
            return []
        
        # Calculate betweenness centrality
        centrality = nx.betweenness_centrality(self.graph)
        
        # Sort by centrality and return top k
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return [node_id for node_id, _ in sorted_nodes[:top_k]]




