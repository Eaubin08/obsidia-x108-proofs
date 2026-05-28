from __future__ import annotations

from typing import Any, Dict, List

from ..models import WorkflowGraph

SKILL_SPEC = {
    "skill_id": "SKILL_DETECT_CRITICAL_ACTIONS_READONLY",
    "contract": "critical actions are candidates only; X108 review requirement is not a verdict",
}


def detect_critical_actions(graph: WorkflowGraph) -> List[Dict[str, Any]]:
    """Detect critical candidates from graph nodes.

    Output intentionally uses `candidate_only=true`. It never says a step is
    permitted or forbidden; it says whether a later X108 review is structurally
    required.
    """
    candidates: List[Dict[str, Any]] = []
    for node in graph.nodes:
        if node.criticality in {"high", "critical"} or node.irreversibility_signals or node.x108_review_required:
            candidates.append({
                "step_id": node.step_id,
                "title": node.title,
                "description": node.description,
                "actor": node.actor,
                "criticality": node.criticality,
                "criticality_score": node.criticality_score,
                "risk_categories": list(node.risk_categories),
                "irreversibility_signals": list(node.irreversibility_signals),
                "control_families": list(node.control_families),
                "required_evidence": list(node.required_evidence),
                "x108_gate_required": True,
                "candidate_only": True,
                "review_note": "requires external X108 evaluation before irreversible execution",
            })
    return candidates
