from __future__ import annotations

from ..agents.agent_01_sop_extractor import extract_sop
from ..agents.agent_02_risk_analyzer import analyze_risk
from ..agents.agent_03_compliance_mapper import map_compliance
from ..agents.agent_04_evidence_builder import build_evidence
from ..models import WorkflowGraph
from ..skills.skill_map_workflow_graph import map_workflow_graph

PRIMITIVE_SPEC = {
    "primitive_id": "WORKFLOW_GRAPH_READONLY_V4",
    "role": "Build a graph candidate from SOP text without runtime execution.",
    "kernel_binding": False,
}


def build_workflow_graph_readonly(sop_text: str, title: str = "Untitled workflow") -> WorkflowGraph:
    """Primitive 1 — WORKFLOW_GRAPH_READONLY."""
    a1 = extract_sop(sop_text, title=title)
    a2 = analyze_risk(a1.payload)
    a3 = map_compliance(a2.payload)
    a4 = build_evidence(a3.payload)
    return map_workflow_graph(
        title=title,
        source_excerpt=sop_text[:2000],
        extraction_payload=a1.payload,
        risk_payload=a2.payload,
        compliance_payload=a3.payload,
        evidence_payload=a4.payload,
    )
