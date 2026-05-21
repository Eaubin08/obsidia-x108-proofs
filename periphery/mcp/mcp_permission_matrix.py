"""
MCP Permission Matrix. Tool access ≠ permission to act.
A tool being available does not imply authorization to use it for consequential actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_TOOL_RISK_MAP = {
    "read_file": "LOW",
    "write_file": "HIGH",
    "execute_command": "CRITICAL",
    "call_api": "HIGH",
    "send_email": "CRITICAL",
    "post_message": "HIGH",
    "database_query": "MEDIUM",
    "database_write": "HIGH",
}


@dataclass
class MCPToolAccess:
    tool_name: str
    risk_level: str
    access_granted: bool
    permission_required: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "risk_level": self.risk_level,
            "access_granted": self.access_granted,
            "permission_required": self.permission_required,
            "reason": self.reason,
        }


def evaluate_tool_access(tool_name: str, has_permission: bool) -> MCPToolAccess:
    risk = _TOOL_RISK_MAP.get(tool_name, "UNKNOWN")
    requires_perm = risk in ("HIGH", "CRITICAL", "UNKNOWN")

    if requires_perm and not has_permission:
        return MCPToolAccess(
            tool_name=tool_name,
            risk_level=risk,
            access_granted=False,
            permission_required=True,
            reason="TOOL_ACCESS_NOT_PERMISSION_DENIED",
        )

    return MCPToolAccess(
        tool_name=tool_name,
        risk_level=risk,
        access_granted=True,
        permission_required=requires_perm,
        reason="ACCESS_GRANTED_WITH_PERMISSION" if requires_perm else "LOW_RISK_ACCESS",
    )
