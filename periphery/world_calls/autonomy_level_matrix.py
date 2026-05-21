from __future__ import annotations

from enum import IntEnum

from .action_risk_classifier import ActionRiskClass
from .world_call_classifier import WorldCallClass


class AutonomyLevel(IntEnum):
    LEVEL_0_READ_ONLY_ANSWER = 0
    LEVEL_1_ADVISORY_SUGGESTION = 1
    LEVEL_2_PLAN_GENERATION = 2
    LEVEL_3_TOOL_CALL_READ_ONLY = 3
    LEVEL_4_REVERSIBLE_MUTATION_WITH_APPROVAL = 4
    LEVEL_5_IRREVERSIBLE_ACTION_WITH_X108_GATE = 5


def compute_autonomy_level(arc: ActionRiskClass, wcc: WorldCallClass) -> AutonomyLevel:
    if arc == ActionRiskClass.ACTION_FORBIDDEN or wcc == WorldCallClass.FORBIDDEN_WORLD_CALL:
        return AutonomyLevel.LEVEL_5_IRREVERSIBLE_ACTION_WITH_X108_GATE

    if arc == ActionRiskClass.ACTION_IRREVERSIBLE or wcc == WorldCallClass.IRREVERSIBLE_WORLD_CALL:
        return AutonomyLevel.LEVEL_5_IRREVERSIBLE_ACTION_WITH_X108_GATE

    if arc in (ActionRiskClass.ACTION_FINANCIAL, ActionRiskClass.ACTION_COMPLIANCE_BOUND):
        return AutonomyLevel.LEVEL_4_REVERSIBLE_MUTATION_WITH_APPROVAL

    if wcc == WorldCallClass.REVERSIBLE_WORLD_CALL or arc == ActionRiskClass.ACTION_CODE_MUTATION:
        return AutonomyLevel.LEVEL_4_REVERSIBLE_MUTATION_WITH_APPROVAL

    if wcc == WorldCallClass.READ_ONLY_WORLD_CALL or arc == ActionRiskClass.ACTION_EXTERNAL_API:
        return AutonomyLevel.LEVEL_3_TOOL_CALL_READ_ONLY

    if arc == ActionRiskClass.ACTION_PLAN:
        return AutonomyLevel.LEVEL_2_PLAN_GENERATION

    if arc == ActionRiskClass.ACTION_ADVISORY:
        return AutonomyLevel.LEVEL_1_ADVISORY_SUGGESTION

    return AutonomyLevel.LEVEL_0_READ_ONLY_ANSWER
