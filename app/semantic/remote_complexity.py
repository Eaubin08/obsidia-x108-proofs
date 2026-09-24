"""Bounded remote-complexity profile — used only to adjust the completion
budget for direct_answer prompts genuinely covering multiple sub-questions.

Does not touch comparison/structured_summary/code_file profiles. Derived
from the prompt text only, never from task_id.
"""
from __future__ import annotations

import re
from enum import Enum

_MULTI_PART_RE = re.compile(
    r"\band\s+what\b|\band\s+which\b|\band\s+who\b|\band\s+how\b|"
    r"\?\s*\w[^?]*\?", re.IGNORECASE)


class RemoteComplexityProfile(str, Enum):
    SIMPLE_CLOSED = "SIMPLE_CLOSED"
    MULTI_PART_DIRECT = "MULTI_PART_DIRECT"
    STRUCTURED = "STRUCTURED"
    CODE = "CODE"
    LONG_FORM = "LONG_FORM"


def classify_remote_complexity(prompt: str, answer_kind: str) -> RemoteComplexityProfile:
    if answer_kind == "code_file":
        return RemoteComplexityProfile.CODE
    if answer_kind in ("comparison", "structured_summary"):
        return RemoteComplexityProfile.STRUCTURED
    if answer_kind == "direct_answer" and _MULTI_PART_RE.search(prompt):
        return RemoteComplexityProfile.MULTI_PART_DIRECT
    if answer_kind == "direct_answer":
        return RemoteComplexityProfile.SIMPLE_CLOSED
    return RemoteComplexityProfile.LONG_FORM


# Bounded budget bumps — only applied to MULTI_PART_DIRECT, and only up to
# a hard ceiling. Never applied blanket to every direct_answer prompt.
MULTI_PART_DIRECT_BUDGET_CEILING = 320


def adaptive_completion_budget(base_budget: int, profile: RemoteComplexityProfile) -> tuple[int, str]:
    """Return (budget, reason). Only MULTI_PART_DIRECT is ever raised, and
    only up to MULTI_PART_DIRECT_BUDGET_CEILING."""
    if profile == RemoteComplexityProfile.MULTI_PART_DIRECT and base_budget < MULTI_PART_DIRECT_BUDGET_CEILING:
        return MULTI_PART_DIRECT_BUDGET_CEILING, "multi_part_direct_bounded_increase"
    return base_budget, "unchanged"
