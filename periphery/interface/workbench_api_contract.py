"""
Workbench API Contract — defines the governance API surface.
All operations are advisory or read-only. No autonomous execution.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_ALLOWED_METHODS = {
    "inspect", "query", "context_read", "audit_read",
    "candidate_submit", "test_run", "report_generate",
}

_FORBIDDEN_METHODS = {
    "auto_execute", "force_merge", "bypass_review",
    "write_memory", "write_neo4j", "deploy_contract",
    "send_transaction", "mint_token",
}


@dataclass
class WorkbenchAPIResult:
    method: str
    allowed: bool
    reason: str
    dry_run_only: bool = True
    requires_human: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "allowed": self.allowed,
            "reason": self.reason,
            "dry_run_only": self.dry_run_only,
            "requires_human": self.requires_human,
        }


def evaluate_workbench_method(method: str) -> WorkbenchAPIResult:
    m = method.lower()
    if m in _FORBIDDEN_METHODS:
        return WorkbenchAPIResult(method=method, allowed=False,
                                  reason=f"WORKBENCH_METHOD_FORBIDDEN:{m}")
    if m in _ALLOWED_METHODS:
        return WorkbenchAPIResult(method=method, allowed=True,
                                  reason="WORKBENCH_METHOD_ALLOWED_ADVISORY",
                                  dry_run_only=True, requires_human=True)
    return WorkbenchAPIResult(method=method, allowed=False,
                              reason=f"WORKBENCH_METHOD_UNKNOWN:{m}")
