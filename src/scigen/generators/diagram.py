"""Diagram generation using Graphviz."""

import random
from pathlib import Path
from typing import List, Tuple, Optional, Set

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

from scigen.core.grammar import GrammarEngine
from scigen.models.rules import RuleSet


class DiagramGenerator:
    """Generates system diagrams using Graphviz.
    
    Creates directed and undirected graphs representing system
    architectures, network topologies, etc.
    """
    
    def __init__(
        self,
        sysname: str,
        seed: Optional[int] = None,
        rules_file: Optional[Path] = None
    ):
        """Initialize diagram generator.
        
        Args:
            sysname: Name of the system being diagrammed.
            seed: Random seed.
            rules_file: Optional grammar rules file for node/edge labels.
        """
        if not NETWORKX_AVAILABLE:
            raise RuntimeError("networkx is required for diagram generation")
        
        self.sysname = sysname
        self.seed = seed or random.randint(0, 0xFFFFFFFF)
        random.seed(self.seed)
        
        # Load grammar if provided
        self.engine = None
        if rules_file and rules_file.exists():
            ruleset = RuleSet()
            self.engine = GrammarEngine(ruleset, debug_level=0)
            self.engine.load_rules(rules_file)
    
    def generate_directed_graph(
        self,
        num_nodes: Optional[int] = None,
        node_label_type: str = "generic"
    ) -> nx.DiGraph:
        """Generate a directed graph.
        
        Args:
            num_nodes: Number of nodes (if None, randomly chosen).
            node_label_type: Type of node labels to generate.
            
        Returns:
            NetworkX DiGraph.
        """
        if num_nodes is None:
            num_nodes = random.randint(5, 15)
        
        G = nx.DiGraph()
        
        # Add nodes with labels
        for i in range(num_nodes):
            label = self._generate_node_label(i, node_label_type)
            G.add_node(i, label=label)
        
        # Add edges to create a connected graph
        # Ensure each node has at least one connection
        edges_added = set()
        
        # Create a spanning structure
        for i in range(1, num_nodes):
            source = random.randint(0, i-1)
            if (source, i) not in edges_added:
                edge_label = self._generate_edge_label()
                G.add_edge(source, i, label=edge_label)
                edges_added.add((source, i))
        
        # Add additional random edges
        num_extra_edges = random.randint(num_nodes // 3, num_nodes)
        for _ in range(num_extra_edges):
            source = random.randint(0, num_nodes - 1)
            target = random.randint(0, num_nodes - 1)
            if source != target and (source, target) not in edges_added:
                edge_label = self._generate_edge_label()
                G.add_edge(source, target, label=edge_label)
                edges_added.add((source, target))
        
        return G
    
    def generate_undirected_graph(
        self,
        num_nodes: Optional[int] = None,
        node_label_type: str = "generic"
    ) -> nx.Graph:
        """Generate an undirected graph.
        
        Args:
            num_nodes: Number of nodes (if None, randomly chosen).
            node_label_type: Type of node labels to generate.
            
        Returns:
            NetworkX Graph.
        """
        if num_nodes is None:
            num_nodes = random.randint(5, 15)
        
        G = nx.Graph()
        
        # Add nodes
        for i in range(num_nodes):
            label = self._generate_node_label(i, node_label_type)
            G.add_node(i, label=label)
        
        # Add edges
        edges_added = set()
        
        # Create connected graph
        for i in range(1, num_nodes):
            source = random.randint(0, i-1)
            edge_key = tuple(sorted([source, i]))
            if edge_key not in edges_added:
                edge_label = self._generate_edge_label()
                G.add_edge(source, i, label=edge_label)
                edges_added.add(edge_key)
        
        # Add extra edges
        num_extra_edges = random.randint(num_nodes // 3, num_nodes)
        for _ in range(num_extra_edges):
            source = random.randint(0, num_nodes - 1)
            target = random.randint(0, num_nodes - 1)
            edge_key = tuple(sorted([source, target]))
            if source != target and edge_key not in edges_added:
                edge_label = self._generate_edge_label()
                G.add_edge(source, target, label=edge_label)
                edges_added.add(edge_key)
        
        return G
    
    def _generate_node_label(self, node_id: int, label_type: str) -> str:
        """Generate a label for a node.
        
        Args:
            node_id: Node identifier.
            label_type: Type of label (generic, ip, hostname, etc.).
            
        Returns:
            Node label.
        """
        if self.engine:
            try:
                rule_name = f"NODE_LABEL_{label_type.upper()}"
                return self.engine.expand(rule_name)
            except:
                pass
        
        # Fallback label generation
        if label_type == "ip":
            return f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"
        elif label_type == "hostname":
            return f"node-{node_id}"
        elif label_type == "letter":
            return chr(65 + node_id % 26)  # A, B, C, ...
        else:
            return f"N{node_id}"
    
    def _generate_edge_label(self) -> str:
        """Generate a label for an edge.
        
        Returns:
            Edge label.
        """
        if self.engine:
            try:
                return self.engine.expand("EDGE_LABEL")
            except:
                pass
        
        # Empty label by default
        return ""
    
    def to_dot(self, graph: nx.Graph, layout: str = "dot") -> str:
        """Convert graph to Graphviz DOT format.
        
        Args:
            graph: NetworkX graph.
            layout: Graphviz layout algorithm.
            
        Returns:
            DOT format string.
        """
        is_directed = isinstance(graph, nx.DiGraph)
        graph_type = "digraph" if is_directed else "graph"
        edge_op = "->" if is_directed else "--"
        
        lines = [f"{graph_type} {self.sysname} {{"]
        lines.append(f"    layout={layout};")
        lines.append("    node [shape=box];")
        lines.append("")
        
        # Add nodes
        for node, data in graph.nodes(data=True):
            label = data.get('label', str(node))
            lines.append(f'    {node} [label="{label}"];')
        
        lines.append("")
        
        # Add edges
        for source, target, data in graph.edges(data=True):
            edge_label = data.get('label', '')
            if edge_label:
                lines.append(f'    {source} {edge_op} {target} [label="{edge_label}"];')
            else:
                lines.append(f'    {source} {edge_op} {target};')
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def save_dot(self, graph: nx.Graph, output_path: Path, layout: str = "dot") -> None:
        """Save graph as DOT file.
        
        Args:
            graph: NetworkX graph.
            output_path: Output file path.
            layout: Graphviz layout algorithm.
        """
        dot_content = self.to_dot(graph, layout)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(dot_content)
