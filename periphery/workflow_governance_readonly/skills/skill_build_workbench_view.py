from __future__ import annotations

from typing import Any, Dict

from ..constants import DECISION_AUTHORITY, READONLY_FLAGS

SKILL_SPEC = {
    "skill_id": "SKILL_BUILD_WORKBENCH_VIEW_READONLY",
    "contract": "build static UI model only; no post/mutation endpoint implied",
}


def build_workbench_view_model(result: Dict[str, Any]) -> Dict[str, Any]:
    """Build a readonly UI model for SOP → graph → IR → packet → envelope."""
    graph = result.get("workflow_graph", {})
    ir = result.get("obsidia_ir", {})
    packet = result.get("context_packet", {})
    envelope = result.get("x108_readonly_ingress_envelope", {})
    nodes = graph.get("nodes", [])
    critical = ir.get("critical_action_candidates", [])
    return {
        "view_kind": "workflow_governance_workbench_readonly_v4",
        "title": graph.get("title"),
        "node_count": len(nodes),
        "edge_count": len(graph.get("edges", [])),
        "critical_candidate_count": len(critical),
        "packet_id": packet.get("packet_id"),
        "envelope_id": envelope.get("envelope_id"),
        "lanes": [
            {"id": "SOP", "label": "SOP source", "readonly": True},
            {"id": "AGENT_SWARM", "label": "6-agent readonly swarm", "readonly": True},
            {"id": "WORKFLOW_GRAPH", "label": "workflow graph candidate", "readonly": True},
            {"id": "OBSIDIA_IR", "label": "Obsidia IR candidate", "readonly": True},
            {"id": "CONTEXT_PACKET", "label": "context packet", "readonly": True},
            {"id": "X108_READONLY_ENVELOPE", "label": "X108 readonly ingress envelope", "readonly": True},
        ],
        "nodes": [
            {
                "step_id": n.get("step_id"),
                "title": n.get("title"),
                "criticality": n.get("criticality"),
                "x108_review_required": n.get("x108_review_required"),
                "required_evidence": n.get("required_evidence", []),
            }
            for n in nodes
        ],
        "critical_candidates": critical,
        "readonly_warnings": [
            "Workbench visualizes candidates only.",
            "No workflow, agent, skill, graph, packet, or envelope can decide.",
            "Any irreversible operation must pass outside this pack through X108.",
        ],
        "boundary": {"decision_authority": DECISION_AUTHORITY, **READONLY_FLAGS},
    }
