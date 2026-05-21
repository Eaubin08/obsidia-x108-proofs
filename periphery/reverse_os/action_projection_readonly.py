"""
Action Projection (Read-Only) — projects what action WOULD be taken, never takes it.
Advisory context only. All outputs are projection candidates.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_FORBIDDEN_TOKENS = {"ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT"}


@dataclass
class ActionProjection:
    projection_id: str
    projected_action: str
    projection_reason: str
    advisory_only: bool = True
    real_action_taken: bool = False
    can_emit_act: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "projection_id": self.projection_id,
            "projected_action": self.projected_action,
            "projection_reason": self.projection_reason,
            "advisory_only": self.advisory_only,
            "real_action_taken": self.real_action_taken,
            "can_emit_act": self.can_emit_act,
        }


def project_action_readonly(projection_id: str, intent: str, context: str) -> ActionProjection:
    forbidden = [t for t in _FORBIDDEN_TOKENS if t in intent.upper() or t in context.upper()]
    if forbidden:
        return ActionProjection(
            projection_id=projection_id,
            projected_action="PROJECTION_WITHHELD",
            projection_reason=f"FORBIDDEN_SOVEREIGN_TOKEN_IN_INPUT:{','.join(forbidden)}",
            advisory_only=True,
            real_action_taken=False,
            can_emit_act=False,
        )
    return ActionProjection(
        projection_id=projection_id,
        projected_action=f"PROJECTED:{intent[:50]}",
        projection_reason="REVERSE_OS_PROJECTION_ADVISORY_ONLY",
        advisory_only=True,
        real_action_taken=False,
        can_emit_act=False,
    )
