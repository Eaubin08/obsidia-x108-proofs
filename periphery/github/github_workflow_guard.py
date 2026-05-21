"""
GitHub Workflow Guard: issue -> plan -> branch -> patch -> tests -> PR -> audit -> human review.
No autonomous merge. Human approval required before any merge.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_WORKFLOW_STEPS = [
    "ISSUE", "PLAN", "BRANCH", "PATCH", "TESTS", "PR", "AUDIT_ARTIFACT", "HUMAN_REVIEW"
]


@dataclass
class WorkflowGuardDecision:
    action: str
    blocked: bool
    reason: str
    requires_human: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "blocked": self.blocked,
            "reason": self.reason,
            "requires_human": self.requires_human,
        }


def guard_workflow_action(action: str) -> WorkflowGuardDecision:
    action_upper = action.upper()

    if action_upper in ("AUTO_MERGE", "FORCE_MERGE", "BYPASS_REVIEW"):
        return WorkflowGuardDecision(
            action=action,
            blocked=True,
            reason="NO_AUTONOMOUS_MERGE_POLICY",
            requires_human=True,
        )

    if action_upper == "MERGE":
        return WorkflowGuardDecision(
            action=action,
            blocked=True,
            reason="MERGE_REQUIRES_HUMAN_APPROVAL",
            requires_human=True,
        )

    if action_upper in ("CREATE_PR", "PUSH_BRANCH", "ADD_COMMENT"):
        return WorkflowGuardDecision(
            action=action,
            blocked=False,
            reason="PR_CREATION_ALLOWED_PRE_REVIEW",
            requires_human=True,
        )

    return WorkflowGuardDecision(
        action=action,
        blocked=False,
        reason="WORKFLOW_ACTION_PERMITTED",
        requires_human=False,
    )
