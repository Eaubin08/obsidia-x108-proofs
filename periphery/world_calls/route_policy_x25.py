"""
Route Policy X25 — Transpac/Minitel-inspired routing governance.
Every action routed through a governed path. No direct internet egress.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .world_call_classifier import WorldCallClass
from .autonomy_level_matrix import AutonomyLevel


@dataclass
class X25RouteDecision:
    action_id: str
    route: str
    gate_required: bool
    human_checkpoint: bool
    dry_run_only: bool = True
    reason: str = ""


def route_x25(
    action_id: str,
    world_call_class: WorldCallClass,
    autonomy_level: AutonomyLevel,
) -> X25RouteDecision:
    if world_call_class == WorldCallClass.FORBIDDEN_WORLD_CALL:
        return X25RouteDecision(
            action_id=action_id,
            route="ROUTE_FORBIDDEN",
            gate_required=True,
            human_checkpoint=True,
            reason="FORBIDDEN_WORLD_CALL",
        )

    if autonomy_level >= AutonomyLevel.LEVEL_5_IRREVERSIBLE_ACTION_WITH_X108_GATE:
        return X25RouteDecision(
            action_id=action_id,
            route="ROUTE_X108_GATE",
            gate_required=True,
            human_checkpoint=True,
            reason="IRREVERSIBLE_REQUIRES_X108_AND_HUMAN",
        )

    if autonomy_level == AutonomyLevel.LEVEL_4_REVERSIBLE_MUTATION_WITH_APPROVAL:
        return X25RouteDecision(
            action_id=action_id,
            route="ROUTE_APPROVAL_GATE",
            gate_required=True,
            human_checkpoint=True,
            reason="REVERSIBLE_MUTATION_REQUIRES_APPROVAL",
        )

    return X25RouteDecision(
        action_id=action_id,
        route="ROUTE_DRY_RUN",
        gate_required=False,
        human_checkpoint=False,
        reason="LOW_RISK_DRY_RUN_PASS",
    )
