from __future__ import annotations

from typing import Any, Dict, List

from ..models import WorkflowEdge, WorkflowGraph, WorkflowStep, stable_id
from ..utils import unique_keep_order

SKILL_SPEC = {
    "skill_id": "SKILL_MAP_WORKFLOW_GRAPH_READONLY",
    "contract": "agent payloads become graph nodes/edges; graph has no execution authority",
}


def map_workflow_graph(
    title: str,
    source_excerpt: str,
    extraction_payload: Dict[str, Any],
    risk_payload: Dict[str, Any],
    evidence_payload: Dict[str, Any],
    compliance_payload: Dict[str, Any] | None = None,
) -> WorkflowGraph:
    """Skill — map extracted SOP into a readonly workflow graph.

    The graph exposes procedural structure for review. It is not a scheduler, it
    does not call tools, and it cannot trigger side effects.
    """
    extracted_steps = extraction_payload.get("steps", [])
    risk_steps = {s.get("step_id"): s for s in risk_payload.get("risk_annotated_steps", [])}
    evidence_steps = {s.get("step_id"): s for s in evidence_payload.get("evidence_by_step", [])}
    compliance_steps = {}
    if compliance_payload:
        compliance_steps = {s.get("step_id"): s for s in compliance_payload.get("compliance_mapped_steps", [])}

    nodes: List[WorkflowStep] = []
    edges: List[WorkflowEdge] = []
    critical_steps: List[str] = []

    for idx, step in enumerate(extracted_steps):
        sid = step["step_id"]
        risk = risk_steps.get(sid, {})
        evidence = evidence_steps.get(sid, {})
        compliance = compliance_steps.get(sid, {})
        criticality = risk.get("criticality", "low")
        node = WorkflowStep(
            step_id=sid,
            title=step.get("title", sid),
            description=step.get("description", ""),
            actor=step.get("actor", "operator_or_agent"),
            sequence_index=step.get("index", idx + 1),
            source_line=step.get("source_line", step.get("description", "")),
            input_refs=step.get("input_refs", []),
            output_refs=step.get("output_refs", []),
            tools=unique_keep_order(step.get("tools", [])),
            conditions=unique_keep_order(step.get("conditions", [])),
            next_steps=step.get("next_steps", []),
            previous_steps=step.get("previous_steps", []),
            criticality=criticality,
            criticality_score=float(risk.get("criticality_score", 0.0)),
            risk_categories=unique_keep_order(risk.get("risk_categories", [])),
            irreversibility_signals=unique_keep_order(risk.get("irreversibility_signals", [])),
            control_families=unique_keep_order(compliance.get("control_families", [])),
            required_evidence=unique_keep_order(evidence.get("required_evidence", [])),
            evidence_status=evidence.get("evidence_status", "requirements_only_missing_until_supplied"),
            x108_review_required=bool(risk.get("x108_review_required") or evidence.get("x108_review_required")),
            candidate_only=True,
        )
        if criticality in {"high", "critical"} or node.x108_review_required:
            critical_steps.append(sid)
        nodes.append(node)

    for node in nodes:
        for target in node.next_steps:
            edges.append(WorkflowEdge(source=node.step_id, target=target, edge_kind="sequence", condition="ordered_next_step"))

    payload = {
        "title": title,
        "source_excerpt": source_excerpt,
        "node_ids": [n.step_id for n in nodes],
        "critical_steps": critical_steps,
    }
    workflow_id = stable_id("WFLOW_GRAPH", payload)
    return WorkflowGraph(
        workflow_id=workflow_id,
        title=title,
        source_kind="human_sop_text",
        source_excerpt=source_excerpt,
        nodes=nodes,
        edges=edges,
        critical_steps=critical_steps,
    )
