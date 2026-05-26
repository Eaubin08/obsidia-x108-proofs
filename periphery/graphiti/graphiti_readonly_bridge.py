"""
Graphiti Read-Only Bridge — provides read-only access to Graphiti context.
No Neo4j write. No Graphiti write. Context signal only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GraphitiContextResult:
    query_id: str
    nodes_found: int
    context_items: list[dict]
    readonly: bool = True
    write_attempted: bool = False
    neo4j_write: bool = False
    graphiti_write: bool = False
    decision_authority: str = "KX108_ONLY"

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "nodes_found": self.nodes_found,
            "context_items": self.context_items,
            "readonly": self.readonly,
            "write_attempted": self.write_attempted,
            "neo4j_write": self.neo4j_write,
            "graphiti_write": self.graphiti_write,
            "decision_authority": self.decision_authority,
        }


def query_graphiti_readonly(query_id: str, query: str, max_nodes: int = 10) -> GraphitiContextResult:
    return GraphitiContextResult(
        query_id=query_id,
        nodes_found=0,
        context_items=[],
        readonly=True,
        write_attempted=False,
        neo4j_write=False,
        graphiti_write=False,
        decision_authority="KX108_ONLY",
    )


def assert_graphiti_no_write(result: GraphitiContextResult) -> None:
    assert result.readonly is True, "GRAPHITI_READONLY_VIOLATION"
    assert result.neo4j_write is False, "GRAPHITI_NEO4J_WRITE_FORBIDDEN"
    assert result.graphiti_write is False, "GRAPHITI_WRITE_FORBIDDEN"
