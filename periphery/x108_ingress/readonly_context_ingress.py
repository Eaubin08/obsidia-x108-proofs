from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class X108ContextIngress:
    action_id: str
    context_accepted: bool
    can_emit_act: bool = False
    can_write_memory: bool = False
    reason: str = ""

    def assert_readonly(self) -> None:
        if self.can_emit_act:
            raise AssertionError("X108_INGRESS_CANNOT_EMIT_ACT")
        if self.can_write_memory:
            raise AssertionError("X108_INGRESS_CANNOT_WRITE_MEMORY")

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "context_accepted": self.context_accepted,
            "can_emit_act": self.can_emit_act,
            "can_write_memory": self.can_write_memory,
            "reason": self.reason,
        }


def ingest_readonly_context(action_id: str, context_packet: Any) -> X108ContextIngress:
    status = getattr(context_packet, "status", "UNKNOWN")
    accepted = status in ("READY", "PENDING")

    ingress = X108ContextIngress(
        action_id=action_id,
        context_accepted=accepted,
        can_emit_act=False,
        can_write_memory=False,
        reason="READONLY_CONTEXT_INGRESS" if accepted else f"CONTEXT_STATUS_{status}",
    )
    ingress.assert_readonly()
    return ingress
