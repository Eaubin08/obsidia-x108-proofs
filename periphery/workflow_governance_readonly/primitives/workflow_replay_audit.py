from __future__ import annotations

from typing import Any, Dict

from ..models import ContextPacket
from ..skills.skill_replay_audit_trace import build_replay_audit_trace

PRIMITIVE_SPEC = {
    "primitive_id": "WORKFLOW_REPLAY_AUDIT_READONLY_V4",
    "role": "Rebuild structural trace and invariant checks without side effects.",
    "execution_replay": False,
}


def build_workflow_replay_audit_readonly(packet: ContextPacket) -> Dict[str, Any]:
    """Primitive 6 — WORKFLOW_REPLAY_AUDIT."""
    report = build_replay_audit_trace(packet)
    report["primitive_spec"] = PRIMITIVE_SPEC
    return report


def build_workflow_replay_audit_from_result(result: Dict[str, Any]) -> Dict[str, Any]:
    packet = result.get("context_packet", {})
    graph = packet.get("workflow_graph", {})
    ir = packet.get("obsidia_ir", {})
    critical = ir.get("critical_action_candidates", [])
    invariant_checks = {
        "packet_boundary_present": isinstance(packet.get("boundary"), dict),
        "graph_boundary_present": isinstance(graph.get("boundary"), dict),
        "ir_authority_is_kx108": ir.get("authority") == "KX108_ONLY",
        "envelope_runtime_binding_false": result.get("x108_readonly_ingress_envelope", {}).get("x108_runtime_binding") is False,
        "critical_candidates_candidate_only": all(c.get("candidate_only") is True for c in critical),
    }
    return {
        "report_id": f"REPLAY_AUDIT_{packet.get('packet_id')}",
        "packet_id": packet.get("packet_id"),
        "workflow_id": packet.get("source_workflow_id"),
        "node_count": len(graph.get("nodes", [])),
        "edge_count": len(graph.get("edges", [])),
        "critical_candidate_count": len(critical),
        "trace_chain": packet.get("trace_chain", []),
        "invariant_checks": invariant_checks,
        "structural_replay_only": True,
        "side_effects_replayed": False,
        "candidate_only": True,
        "primitive_spec": PRIMITIVE_SPEC,
        "boundary": packet.get("boundary", {}),
    }
