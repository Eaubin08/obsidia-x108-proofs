from __future__ import annotations

from enum import StrEnum
from typing import Any


class WorldCallClass(StrEnum):
    NO_WORLD_CALL = "NO_WORLD_CALL"
    READ_ONLY_WORLD_CALL = "READ_ONLY_WORLD_CALL"
    REVERSIBLE_WORLD_CALL = "REVERSIBLE_WORLD_CALL"
    IRREVERSIBLE_WORLD_CALL = "IRREVERSIBLE_WORLD_CALL"
    CRITICAL_WORLD_CALL = "CRITICAL_WORLD_CALL"
    FORBIDDEN_WORLD_CALL = "FORBIDDEN_WORLD_CALL"


_FORBIDDEN_DOMAINS = {"payment", "trade_execution", "email", "posting", "api_mutation_real"}
_CRITICAL_DOMAINS = {"compliance", "legal", "healthcare", "critical_infrastructure"}
_IRREVERSIBLE_KEYWORDS = {"delete", "drop", "destroy", "irreversible", "publish"}
_REVERSIBLE_KEYWORDS = {"update", "patch", "modify", "create"}
_READ_ONLY_KEYWORDS = {"read", "query", "fetch", "inspect", "search", "list"}


def classify_world_call(action_type: str, domain: str, irreversible: bool) -> WorldCallClass:
    action_lower = action_type.lower()
    domain_lower = domain.lower()

    if domain_lower in _FORBIDDEN_DOMAINS:
        return WorldCallClass.FORBIDDEN_WORLD_CALL

    if domain_lower in _CRITICAL_DOMAINS:
        return WorldCallClass.CRITICAL_WORLD_CALL

    if irreversible or any(k in action_lower for k in _IRREVERSIBLE_KEYWORDS):
        return WorldCallClass.IRREVERSIBLE_WORLD_CALL

    if any(k in action_lower for k in _REVERSIBLE_KEYWORDS):
        return WorldCallClass.REVERSIBLE_WORLD_CALL

    if any(k in action_lower for k in _READ_ONLY_KEYWORDS) or action_lower in ("query", "read"):
        return WorldCallClass.READ_ONLY_WORLD_CALL

    return WorldCallClass.NO_WORLD_CALL


def is_blocked(wcc: WorldCallClass) -> bool:
    return wcc in (WorldCallClass.FORBIDDEN_WORLD_CALL, WorldCallClass.CRITICAL_WORLD_CALL)
