"""
Knowledge Graph Store — in-memory graph with Neo4j-compatible API.
Swappable with real Neo4j driver via the same interface.
"""

import logging
from typing import Optional, Any
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeNode:
    """A node in the knowledge graph."""
    id: str
    labels: list[str] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeEdge:
    """A directed relationship between two nodes."""
    id: str
    source_id: str
    target_id: str
    relationship: str
    properties: dict[str, Any] = field(default_factory=dict)


class KnowledgeGraph:
    """
    In-memory knowledge graph store.
    API mirrors Neo4j for easy migration: nodes, edges, queries.
    """

    def __init__(self):
        self._nodes: dict[str, KnowledgeNode] = {}
        self._edges: dict[str, KnowledgeEdge] = {}
        self._adj_out: dict[str, list[KnowledgeEdge]] = defaultdict(list)  # source → edges
        self._adj_in: dict[str, list[KnowledgeEdge]] = defaultdict(list)   # target → edges
        self._label_index: dict[str, list[str]] = defaultdict(list)        # label → node_ids

    # ── CRUD ──

    def add_node(self, node_id: str, labels: list[str], properties: dict = None) -> KnowledgeNode:
        node = KnowledgeNode(id=node_id, labels=labels, properties=properties or {})
        node.properties.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        self._nodes[node_id] = node
        for label in labels:
            self._label_index[label].append(node_id)
        return node

    def add_edge(self, edge_id: str, source_id: str, target_id: str,
                 relationship: str, properties: dict = None) -> KnowledgeEdge:
        if source_id not in self._nodes:
            raise ValueError(f"Source node '{source_id}' not found")
        if target_id not in self._nodes:
            self.add_node(target_id, ["Unknown"], {})
        edge = KnowledgeEdge(
            id=edge_id, source_id=source_id, target_id=target_id,
            relationship=relationship, properties=properties or {},
        )
        edge.properties.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        self._edges[edge_id] = edge
        self._adj_out[source_id].append(edge)
        self._adj_in[target_id].append(edge)
        return edge

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        return self._nodes.get(node_id)

    def get_edge(self, edge_id: str) -> Optional[KnowledgeEdge]:
        return self._edges.get(edge_id)

    def delete_node(self, node_id: str):
        if node_id in self._nodes:
            del self._nodes[node_id]
            self._adj_out.pop(node_id, None)
            self._adj_in.pop(node_id, None)
            for label_list in self._label_index.values():
                if node_id in label_list:
                    label_list.remove(node_id)

    # ── Queries ──

    def nodes_by_label(self, label: str) -> list[KnowledgeNode]:
        return [self._nodes[nid] for nid in self._label_index.get(label, []) if nid in self._nodes]

    def edges_by_relationship(self, rel: str) -> list[KnowledgeEdge]:
        return [e for e in self._edges.values() if e.relationship == rel]

    def neighbors(self, node_id: str, direction: str = "out") -> list[tuple[KnowledgeEdge, KnowledgeNode]]:
        """Get neighbors. direction: 'out', 'in', or 'both'."""
        results = []
        if direction in ("out", "both"):
            for edge in self._adj_out.get(node_id, []):
                target = self._nodes.get(edge.target_id)
                if target:
                    results.append((edge, target))
        if direction in ("in", "both"):
            for edge in self._adj_in.get(node_id, []):
                source = self._nodes.get(edge.source_id)
                if source:
                    results.append((edge, source))
        return results

    def trace_lineage(self, node_id: str, max_depth: int = 5) -> dict:
        """Trace upstream and downstream lineage from a node."""
        upstream = self._walk_graph(node_id, "in", max_depth)
        downstream = self._walk_graph(node_id, "out", max_depth)
        return {"node": self._node_dict(node_id), "upstream": upstream, "downstream": downstream}

    def impact_analysis(self, node_id: str) -> dict:
        """Find all assets affected if this node changes/fails."""
        affected = []
        visited = set()

        def walk(nid: str, depth: int):
            if depth > 10 or nid in visited:
                return
            visited.add(nid)
            for edge in self._adj_out.get(nid, []):
                target = self._nodes.get(edge.target_id)
                if target:
                    affected.append({
                        "node": self._node_dict(edge.target_id),
                        "relationship": edge.relationship,
                        "depth": depth,
                    })
                    walk(edge.target_id, depth + 1)

        walk(node_id, 1)
        return {"source": self._node_dict(node_id), "affected_assets": affected}

    def compliance_mapping(self, column_name: str) -> dict:
        """Map a column through its regulatory context."""
        column_node = None
        for node in self._nodes.values():
            if "Column" in node.labels and node.properties.get("name", "").lower() == column_name.lower():
                column_node = node
                break

        if not column_node:
            return {"error": f"Column '{column_name}' not found"}

        result = {"column": self._node_dict(column_node.id), "regulations": [], "controls": []}

        # Walk outward to find regulations and controls
        for edge, target in self.neighbors(column_node.id, "out"):
            if "Policy" in target.labels:
                result["regulations"].append(self._node_dict(target.id))
            if "Control" in target.labels:
                result["controls"].append(self._node_dict(target.id))

        return result

    def risk_heatmap(self) -> list[dict]:
        """Get all Risk nodes sorted by score."""
        risks = self.nodes_by_label("Risk")
        return sorted(
            [self._node_dict(r.id) for r in risks],
            key=lambda r: r["properties"].get("score", 0),
            reverse=True,
        )

    # ── Aggregate info ──

    def summary(self) -> dict:
        return {
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "labels": {label: len(ids) for label, ids in self._label_index.items()},
            "relationships": list(set(e.relationship for e in self._edges.values())),
        }

    # ── Helpers ──

    def _node_dict(self, node_id: str) -> Optional[dict]:
        node = self._nodes.get(node_id)
        if not node:
            return None
        return {"id": node.id, "labels": node.labels, "properties": node.properties}

    def _walk_graph(self, start_id: str, direction: str, max_depth: int) -> list[dict]:
        results = []
        visited = {start_id}

        def walk(nid: str, depth: int):
            if depth > max_depth:
                return
            edges = self._adj_in.get(nid, []) if direction == "in" else self._adj_out.get(nid, [])
            for edge in edges:
                neighbor_id = edge.source_id if direction == "in" else edge.target_id
                if neighbor_id in visited:
                    continue
                visited.add(neighbor_id)
                neighbor = self._nodes.get(neighbor_id)
                if neighbor:
                    results.append({
                        "node": self._node_dict(neighbor_id),
                        "relationship": edge.relationship,
                        "depth": depth,
                    })
                    walk(neighbor_id, depth + 1)

        walk(start_id, 1)
        return results


# Singleton
knowledge_graph = KnowledgeGraph()
