"""
Trust Path — chain of custody from input to decision.
Verifies that each step in the governance path is traceable.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TrustPathNode:
    step: str
    agent_id: str
    hash_ref: str
    trusted: bool


@dataclass
class TrustPath:
    action_id: str
    nodes: list[TrustPathNode]
    is_complete: bool
    broken_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "is_complete": self.is_complete,
            "broken_at": self.broken_at,
            "node_count": len(self.nodes),
            "nodes": [
                {"step": n.step, "agent_id": n.agent_id, "trusted": n.trusted}
                for n in self.nodes
            ],
        }


def build_trust_path(action_id: str, ticket: Any, pog: Any) -> TrustPath:
    nodes = []

    nodes.append(TrustPathNode(
        step="OS3_INPUT",
        agent_id="os3_ticket",
        hash_ref=getattr(ticket, "input_hash", ""),
        trusted=bool(getattr(ticket, "input_hash", "")),
    ))
    nodes.append(TrustPathNode(
        step="OS3_TRACE",
        agent_id="os3_ticket",
        hash_ref=getattr(ticket, "trace_hash", ""),
        trusted=bool(getattr(ticket, "trace_hash", "")),
    ))
    nodes.append(TrustPathNode(
        step="LYAPUNOV",
        agent_id="math_core",
        hash_ref="",
        trusted=getattr(pog, "lyapunov_stable", False),
    ))
    nodes.append(TrustPathNode(
        step="POG",
        agent_id="proof_of_governance",
        hash_ref="",
        trusted=getattr(pog, "pog_valid", False),
    ))

    broken_at = ""
    for n in nodes:
        if not n.trusted:
            broken_at = n.step
            break

    return TrustPath(
        action_id=action_id,
        nodes=nodes,
        is_complete=(broken_at == ""),
        broken_at=broken_at,
    )
