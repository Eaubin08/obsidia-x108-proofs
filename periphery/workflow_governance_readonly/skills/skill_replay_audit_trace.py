from __future__ import annotations

from typing import Any, Dict

from ..models import ContextPacket, stable_id

SKILL_SPEC = {
    "skill_id": "SKILL_REPLAY_AUDIT_TRACE_READONLY",
    "contract": "structural replay only; no side effects are replayed or executed",
}


def build_replay_audit_trace(packet: ContextPacket) -> Dict[str, Any]:
    """Build a structural replay audit report from a context packet."""
    report_id = stable_id("REPLAY_AUDIT", {"packet_id": packet.packet_id, "trace": packet.trace_chain})
    graph = packet.workflow_graph
    ir = packet.obsidia_ir
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    critical = ir.get("critical_action_candidates", [])
    invariant_checks = {
        "packet_is_candidate_only": "context_packet_is_not_a_decision" in packet.packet_constraints,
        "graph_boundary_present": isinstance(graph.get("boundary"), dict),
        "ir_authority_is_kx108": ir.get("authority") == "KX108_ONLY",
        "critical_candidates_are_candidate_only": all(c.get("candidate_only") is True for c in critical),
        "side_effects_replayed": False,
        "runtime_execution_replayed": False,
    }
    return {
        "report_id": report_id,
        "source_packet_id": packet.packet_id,
        "replay_kind": "structure_only_readonly",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "critical_step_count": len(critical),
        "trace_chain": list(packet.trace_chain),
        "invariant_checks": invariant_checks,
        "replay_gaps": [k for k, ok in invariant_checks.items() if ok is not True and k not in {"side_effects_replayed", "runtime_execution_replayed"}],
        "side_effect_replay": False,
        "execution_replay": False,
        "candidate_only": True,
        "boundary": dict(packet.boundary),
    }
