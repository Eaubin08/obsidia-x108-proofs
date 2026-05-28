from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from ..models import AgentSignal, ContextPacket, ObsidiaIR, WorkflowGraph, stable_id

SKILL_SPEC = {
    "skill_id": "SKILL_EXPORT_CONTEXT_PACKET_READONLY",
    "contract": "packet bundles signals/graph/IR/proof requirements; it is not an execution request",
}


def export_context_packet(graph: WorkflowGraph, ir: ObsidiaIR, signals: List[AgentSignal]) -> ContextPacket:
    """Export a context packet for downstream readonly X108 ingress."""
    evidence_requirements = sorted(set(ir.required_evidence))
    critical = list(ir.critical_action_candidates)
    trace_chain = [
        "SOP_TEXT",
        "AGENT_01_SOP_EXTRACTOR_READONLY",
        "AGENT_02_RISK_ANALYZER_READONLY",
        "AGENT_03_COMPLIANCE_MAPPER_READONLY",
        "AGENT_04_EVIDENCE_BUILDER_READONLY",
        "AGENT_05_CONTRADICTION_REPLAYER_READONLY",
        "AGENT_06_READONLY_AGGREGATOR",
        "WORKFLOW_GRAPH_READONLY",
        "OBSIDIA_IR",
        "OBSIDIA_IR_CANDIDATE",
        "CONTEXT_PACKET_READONLY",
    ]
    payload = {
        "workflow_id": graph.workflow_id,
        "ir_id": ir.ir_id,
        "signal_ids": [s.agent_id for s in signals],
        "critical_count": len(critical),
    }
    packet_id = stable_id("WFLOW_PACKET", payload)
    return ContextPacket(
        packet_id=packet_id,
        source_workflow_id=graph.workflow_id,
        source_ir_id=ir.ir_id,
        packet_kind="workflow_governance_context_packet",
        signals=[asdict(s) for s in signals],
        workflow_graph=asdict(graph),
        obsidia_ir=asdict(ir),
        evidence_requirements=evidence_requirements,
        critical_action_summary={
            "critical_candidate_count": len(critical),
            "critical_step_ids": [c.get("step_id") for c in critical],
            "x108_gate_required_candidates": [c.get("step_id") for c in critical if c.get("x108_gate_required")],
            "candidate_only": True,
        },
        trace_chain=trace_chain,
        replay_pointer=f"REPLAY_POINTER::{packet_id}",
    )
