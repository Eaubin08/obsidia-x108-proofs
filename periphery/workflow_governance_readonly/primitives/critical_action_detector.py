from __future__ import annotations

from typing import Any, Dict, List

from ..models import WorkflowGraph
from ..skills.skill_detect_critical_actions import detect_critical_actions

PRIMITIVE_SPEC = {
    "primitive_id": "CRITICAL_ACTION_DETECTOR_READONLY_V4",
    "role": "Detect irreversible/sensitive candidates for external X108 evaluation.",
    "candidate_only": True,
}


def detect_critical_action_candidates_readonly(graph: WorkflowGraph) -> List[Dict[str, Any]]:
    """Primitive 4 — CRITICAL_ACTION_DETECTOR."""
    candidates = detect_critical_actions(graph)
    for candidate in candidates:
        candidate["detector_primitive"] = PRIMITIVE_SPEC["primitive_id"]
    return candidates
