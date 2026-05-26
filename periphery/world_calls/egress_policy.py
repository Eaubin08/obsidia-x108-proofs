from __future__ import annotations

from .world_call_classifier import WorldCallClass
from .action_risk_classifier import ActionRiskClass
from .autonomy_level_matrix import AutonomyLevel


def evaluate_egress_policy(
    wcc: WorldCallClass,
    arc: ActionRiskClass,
    autonomy_level: AutonomyLevel,
    x108_gate: str,
) -> tuple[str, str]:
    if x108_gate.upper() not in ("ALLOW",):
        return "BLOCK", f"X108_GATE_{x108_gate}_REQUIRES_ALLOW"

    if wcc == WorldCallClass.FORBIDDEN_WORLD_CALL:
        return "BLOCK", "FORBIDDEN_WORLD_CALL"

    if arc == ActionRiskClass.ACTION_FORBIDDEN:
        return "BLOCK", "FORBIDDEN_ACTION_RISK"

    if autonomy_level == AutonomyLevel.LEVEL_5_IRREVERSIBLE_ACTION_WITH_X108_GATE:
        return "DRY_RUN", "V4_IRREVERSIBLE_DRY_RUN_HUMAN_REQUIRED"

    if autonomy_level == AutonomyLevel.LEVEL_4_REVERSIBLE_MUTATION_WITH_APPROVAL:
        return "DRY_RUN", "V4_REVERSIBLE_DRY_RUN_APPROVAL_REQUIRED"

    return "DRY_RUN", "V4_ALL_EGRESS_DRY_RUN"
