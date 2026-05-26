"""
Graphiti Context Adapter — adapts Graphiti context for ContextPacket consumption.
Read-only. Contextualizes but does not decide.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .graphiti_readonly_bridge import GraphitiContextResult


@dataclass
class GraphitiContextPacket:
    adapter_id: str
    source_query_id: str
    adapted_items: list[dict]
    context_signal_only: bool = True
    allowed_to_decide: bool = False
    graphiti_write: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapter_id": self.adapter_id,
            "source_query_id": self.source_query_id,
            "adapted_items": self.adapted_items,
            "context_signal_only": self.context_signal_only,
            "allowed_to_decide": self.allowed_to_decide,
            "graphiti_write": self.graphiti_write,
        }


def adapt_graphiti_context(adapter_id: str, result: GraphitiContextResult) -> GraphitiContextPacket:
    return GraphitiContextPacket(
        adapter_id=adapter_id,
        source_query_id=result.query_id,
        adapted_items=result.context_items,
        context_signal_only=True,
        allowed_to_decide=False,
        graphiti_write=False,
    )
