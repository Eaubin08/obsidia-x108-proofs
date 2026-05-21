from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import ActionCandidate, PeripheralSignalPacket
from .hackathon_failures import FailureCode

@dataclass
class ActionStep:
    step_id: str
    tool: str
    irreversible: bool = False
    async_step: bool = False
    requires_permission: bool = True
    changed_plan: bool = False
    payload: dict[str, Any] = field(default_factory=dict)

@dataclass
class ActionSequence:
    action_id: str
    steps: list[ActionStep]

def govern_action_sequence(action: ActionCandidate, sequence: ActionSequence) -> PeripheralSignalPacket:
    out = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    out.extra_metrics["sequence_step_count"] = len(sequence.steps)

    if len(sequence.steps) > 1:
        out.add_risk(FailureCode.MULTI_STEP_TEMPORAL_RISK.value)

    for step in sequence.steps:
        if step.async_step:
            out.add_unknown(FailureCode.ASYNC_RECHECK_REQUIRED.value)
            out.extra_metrics["x108_recheck_required_at_exec"] = True
            out.recommended_gate = "HOLD"
        if step.tool:
            out.add_risk(FailureCode.TOOL_CALL_RISK.value)
        if step.changed_plan:
            out.add_risk(FailureCode.PLAN_CHANGE_UNGOVERNED.value)
            out.recommended_gate = "HOLD"
        if step.irreversible and step.requires_permission and not action.payload.get("permission_ok", True):
            out.add_contradiction(FailureCode.PERMISSION_MISSING.value)
            out.recommended_gate = "BLOCK_CANDIDATE"

    return out
