from __future__ import annotations

from enum import StrEnum


class ActionRiskClass(StrEnum):
    ACTION_READ_ONLY = "ACTION_READ_ONLY"
    ACTION_ADVISORY = "ACTION_ADVISORY"
    ACTION_PLAN = "ACTION_PLAN"
    ACTION_EXTERNAL_API = "ACTION_EXTERNAL_API"
    ACTION_CODE_MUTATION = "ACTION_CODE_MUTATION"
    ACTION_FINANCIAL = "ACTION_FINANCIAL"
    ACTION_COMPLIANCE_BOUND = "ACTION_COMPLIANCE_BOUND"
    ACTION_SENSITIVE = "ACTION_SENSITIVE"
    ACTION_IRREVERSIBLE = "ACTION_IRREVERSIBLE"
    ACTION_FORBIDDEN = "ACTION_FORBIDDEN"


_FORBIDDEN_TYPES = {"payment", "trade", "broadcast", "deploy_production"}
_FINANCIAL_TYPES = {"transfer", "withdrawal", "order", "settlement"}
_COMPLIANCE_DOMAINS = {"healthcare", "legal", "compliance", "regulatory"}
_CODE_TYPES = {"code_mutation", "patch_apply", "deploy"}


def classify_action_risk(action_type: str, domain: str, irreversible: bool) -> ActionRiskClass:
    atype = action_type.lower()
    dom = domain.lower()

    if atype in _FORBIDDEN_TYPES:
        return ActionRiskClass.ACTION_FORBIDDEN

    if irreversible:
        return ActionRiskClass.ACTION_IRREVERSIBLE

    if atype in _FINANCIAL_TYPES:
        return ActionRiskClass.ACTION_FINANCIAL

    if dom in _COMPLIANCE_DOMAINS:
        return ActionRiskClass.ACTION_COMPLIANCE_BOUND

    if atype in _CODE_TYPES:
        return ActionRiskClass.ACTION_CODE_MUTATION

    if "api" in atype:
        return ActionRiskClass.ACTION_EXTERNAL_API

    if atype in ("plan", "propose", "suggest"):
        return ActionRiskClass.ACTION_PLAN

    if atype in ("advise", "recommend", "explain"):
        return ActionRiskClass.ACTION_ADVISORY

    return ActionRiskClass.ACTION_READ_ONLY


def requires_x108_gate(arc: ActionRiskClass) -> bool:
    return arc in (
        ActionRiskClass.ACTION_IRREVERSIBLE,
        ActionRiskClass.ACTION_FINANCIAL,
        ActionRiskClass.ACTION_COMPLIANCE_BOUND,
        ActionRiskClass.ACTION_FORBIDDEN,
    )


def requires_human_approval(arc: ActionRiskClass) -> bool:
    return arc in (
        ActionRiskClass.ACTION_FORBIDDEN,
        ActionRiskClass.ACTION_IRREVERSIBLE,
    )
