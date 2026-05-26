from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

class ActionPhase(StrEnum):
    INPUT_CAPTURED = "INPUT_CAPTURED"
    ACTION_CANDIDATE_BUILT = "ACTION_CANDIDATE_BUILT"
    PERIPHERY_SCORED = "PERIPHERY_SCORED"
    SIGMA_ROUTED = "SIGMA_ROUTED"
    X108_EVALUATED = "X108_EVALUATED"
    OS3_TICKETED = "OS3_TICKETED"
    GENCOIN_EVALUATED = "GENCOIN_EVALUATED"
    WORLD_ACTION_DRY_RUN_READY = "WORLD_ACTION_DRY_RUN_READY"
    FEEDBACK_CAPTURED = "FEEDBACK_CAPTURED"
    MEMORY_CANDIDATE_BUILT = "MEMORY_CANDIDATE_BUILT"
    CLOSED = "CLOSED"

_ALLOWED_NEXT: dict[ActionPhase, set[ActionPhase]] = {
    ActionPhase.INPUT_CAPTURED: {ActionPhase.ACTION_CANDIDATE_BUILT},
    ActionPhase.ACTION_CANDIDATE_BUILT: {ActionPhase.PERIPHERY_SCORED},
    ActionPhase.PERIPHERY_SCORED: {ActionPhase.SIGMA_ROUTED},
    ActionPhase.SIGMA_ROUTED: {ActionPhase.X108_EVALUATED},
    ActionPhase.X108_EVALUATED: {ActionPhase.OS3_TICKETED},
    ActionPhase.OS3_TICKETED: {ActionPhase.GENCOIN_EVALUATED},
    ActionPhase.GENCOIN_EVALUATED: {ActionPhase.WORLD_ACTION_DRY_RUN_READY},
    ActionPhase.WORLD_ACTION_DRY_RUN_READY: {ActionPhase.FEEDBACK_CAPTURED},
    ActionPhase.FEEDBACK_CAPTURED: {ActionPhase.MEMORY_CANDIDATE_BUILT},
    ActionPhase.MEMORY_CANDIDATE_BUILT: {ActionPhase.CLOSED},
    ActionPhase.CLOSED: set(),
}

@dataclass
class ActionLifecycleTrace:
    action_id: str
    phases: list[ActionPhase] = field(default_factory=lambda: [ActionPhase.INPUT_CAPTURED])
    notes: list[str] = field(default_factory=list)

    @property
    def current(self) -> ActionPhase:
        return self.phases[-1]

    def advance(self, next_phase: ActionPhase, note: str = "") -> None:
        allowed = _ALLOWED_NEXT.get(self.current, set())
        if next_phase not in allowed:
            raise ValueError(f"INVALID_ACTION_PHASE_TRANSITION:{self.current}->{next_phase}")
        self.phases.append(next_phase)
        if note:
            self.notes.append(note)

    def to_dict(self) -> dict[str, Any]:
        return {"action_id": self.action_id, "phases": [p.value for p in self.phases], "notes": self.notes}
