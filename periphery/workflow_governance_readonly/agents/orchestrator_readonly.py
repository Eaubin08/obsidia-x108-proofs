from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from .agent_01_sop_extractor import extract_sop
from .agent_02_risk_analyzer import analyze_risk
from .agent_03_compliance_mapper import map_compliance
from .agent_04_evidence_builder import build_evidence
from .agent_05_contradiction_replayer import replay_contradictions
from .agent_06_readonly_aggregator import aggregate_readonly
from ..boundary import validate_readonly_output
from ..models import Boundary
from ..skills.skill_map_workflow_graph import map_workflow_graph
from ..skills.skill_build_obsidia_ir import build_obsidia_ir
from ..skills.skill_export_context_packet import export_context_packet
from ..skills.skill_x108_ingress_envelope import build_x108_readonly_ingress_envelope


def run_readonly_swarm(sop_text: str, title: str = "Untitled workflow") -> Dict[str, Any]:
    """Run the full Agent 1..6 readonly workflow swarm.

    Pipeline:
    SOP → A1 extraction → A2 risk → A3 compliance → A4 evidence → A5 replay
    → A6 aggregation → workflow graph → Obsidia IR → context packet → X108
    readonly ingress envelope.
    """
    a1 = extract_sop(sop_text, title=title)
    a2 = analyze_risk(a1.payload)
    a3 = map_compliance(a2.payload)
    a4 = build_evidence(a3.payload)
    a5 = replay_contradictions(a1.payload, a2.payload, a4.payload, compliance_payload=a3.payload)
    a6 = aggregate_readonly([a1, a2, a3, a4, a5])

    graph = map_workflow_graph(
        title=title,
        source_excerpt=sop_text[:2000],
        extraction_payload=a1.payload,
        risk_payload=a2.payload,
        evidence_payload=a4.payload,
        compliance_payload=a3.payload,
    )
    ir = build_obsidia_ir(graph=graph, aggregation_signal=a6)
    packet = export_context_packet(graph=graph, ir=ir, signals=[a1, a2, a3, a4, a5, a6])
    envelope = build_x108_readonly_ingress_envelope(packet)

    result = {
        "pipeline_kind": "OBSIDIA_WORKFLOW_GOVERNANCE_READONLY_SWARM_V4",
        "boundary": Boundary().as_dict(),
        "signals": {
            "agent_01_sop_extractor": asdict(a1),
            "agent_02_risk_analyzer": asdict(a2),
            "agent_03_compliance_mapper": asdict(a3),
            "agent_04_evidence_builder": asdict(a4),
            "agent_05_contradiction_replayer": asdict(a5),
            "agent_06_readonly_aggregator": asdict(a6),
        },
        "workflow_graph": asdict(graph),
        "obsidia_ir": asdict(ir),
        "context_packet": asdict(packet),
        "x108_readonly_ingress_envelope": asdict(envelope),
    }
    validate_readonly_output(result, allow_descriptive_tokens=True)
    return result
