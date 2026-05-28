from __future__ import annotations

from typing import Any, Dict

from ..constants import DECISION_AUTHORITY
from ..models import AgentSignal, ObsidiaIR, WorkflowGraph, stable_id
from .skill_detect_critical_actions import detect_critical_actions

SKILL_SPEC = {
    "skill_id": "SKILL_BUILD_OBSIDIA_IR_READONLY",
    "contract": "workflow graph becomes IR candidate; IR has no direct runtime semantics",
}


def build_obsidia_ir(graph: WorkflowGraph, aggregation_signal: AgentSignal) -> ObsidiaIR:
    """Reduce workflow graph into an Obsidia IR candidate.

    The IR is a structural representation for review. It deliberately separates
    OS0/OS1/OS3/OS4 projections and leaves sovereign decision authority outside.
    """
    critical_candidates = detect_critical_actions(graph)
    required_evidence = sorted({req for n in graph.nodes for req in n.required_evidence})

    ir_payload = {
        "workflow_id": graph.workflow_id,
        "title": graph.title,
        "critical_candidates": critical_candidates,
        "required_evidence": required_evidence,
    }
    ir_id = stable_id("OBSIDIA_IR", ir_payload)

    return ObsidiaIR(
        ir_id=ir_id,
        source_workflow_id=graph.workflow_id,
        ir_kind="workflow_governance_candidate_v4",
        intent={
            "title": graph.title,
            "source_kind": graph.source_kind,
            "purpose": "structure SOP into reviewable governance context",
            "execution_intent": False,
            "decision_authority": DECISION_AUTHORITY,
        },
        steps=[
            {
                "step_id": n.step_id,
                "description": n.description,
                "actor": n.actor,
                "criticality": n.criticality,
                "criticality_score": n.criticality_score,
                "risk_categories": n.risk_categories,
                "control_families": n.control_families,
                "required_evidence": n.required_evidence,
                "next_steps": n.next_steps,
                "candidate_only": True,
            }
            for n in graph.nodes
        ],
        critical_action_candidates=critical_candidates,
        required_evidence=required_evidence,
        os_projection={
            "OS0_IR": {
                "role": "deterministic representation candidate",
                "runtime_execution": False,
            },
            "OS1_STRUCTURE": {
                "node_count": len(graph.nodes),
                "edge_count": len(graph.edges),
                "critical_step_count": len(graph.critical_steps),
            },
            "OS2_ORCHESTRATION": {
                "agent_swarm_used": True,
                "agent_count": aggregation_signal.payload.get("agent_count"),
                "orchestration_is_readonly": True,
            },
            "OS3_AUDIT": {
                "trace_required": True,
                "replay_required": True,
                "evidence_requirements": required_evidence,
            },
            "OS4_INTERFACE": {
                "workbench_view_possible": True,
                "operator_packet_possible": True,
            },
        },
    )
