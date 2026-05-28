from __future__ import annotations

from typing import Any, Dict

SKILL_SPEC = {
    "skill_id": "SKILL_GENERATE_REPORT_READONLY",
    "contract": "generate operator-readable report from swarm result; documentation only",
}


def generate_workflow_governance_report(result: Dict[str, Any]) -> str:
    """Generate a readable markdown report from a swarm result."""
    graph = result.get("workflow_graph", {})
    ir = result.get("obsidia_ir", {})
    packet = result.get("context_packet", {})
    envelope = result.get("x108_readonly_ingress_envelope", {})
    critical = ir.get("critical_action_candidates", [])
    evidence = packet.get("evidence_requirements", [])
    lines = [
        "# Workflow Governance Report V4",
        "",
        f"workflow_id: {graph.get('workflow_id')}",
        f"ir_id: {ir.get('ir_id')}",
        f"packet_id: {packet.get('packet_id')}",
        f"envelope_id: {envelope.get('envelope_id')}",
        "",
        "## Boundary",
        "",
        "DECISION_AUTHORITY=KX108_ONLY",
        "allowed_to_decide=false",
        "kernel_mutation=false",
        "x108_mutation=false",
        "workflow_decision=false",
        "x108_runtime_binding=false",
        "kernel_binding=false",
        "",
        "## Graph",
        "",
        f"nodes: {len(graph.get('nodes', []))}",
        f"edges: {len(graph.get('edges', []))}",
        f"critical_steps: {len(graph.get('critical_steps', []))}",
        "",
        "## Critical action candidates",
        "",
    ]
    if critical:
        for c in critical:
            lines.append(f"- {c.get('step_id')} | {c.get('criticality')} | candidate_only={c.get('candidate_only')} | x108_gate_required={c.get('x108_gate_required')}")
    else:
        lines.append("- none detected")
    lines.extend(["", "## Evidence requirements", ""])
    if evidence:
        lines.extend(f"- {item}" for item in evidence)
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Status",
        "",
        "This report is a readonly governance artifact. It is not a runtime authorization, not a workflow execution, and not a kernel patch.",
    ])
    return "\n".join(lines) + "\n"
