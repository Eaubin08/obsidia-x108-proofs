from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import Any

_VALID_STATUSES = {"READY", "PENDING", "STALE", "REJECTED", "QUARANTINED"}


@dataclass
class ContextPacket:
    packet_id: str
    action_id: str
    status: str
    content_hash: str
    signals: list[str]
    can_decide: bool = False

    def assert_cannot_decide(self) -> None:
        if self.can_decide:
            raise AssertionError("CONTEXT_PACKET_CANNOT_DECIDE")

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "action_id": self.action_id,
            "status": self.status,
            "content_hash": self.content_hash,
            "signals": self.signals,
            "can_decide": self.can_decide,
        }


def build_context_packet(action_id: str, signals: list[str], status: str = "READY") -> ContextPacket:
    if status not in _VALID_STATUSES:
        raise ValueError(f"INVALID_STATUS:{status}")
    content_hash = hashlib.sha256(
        json.dumps({"action_id": action_id, "signals": signals}, sort_keys=True).encode()
    ).hexdigest()
    pkt = ContextPacket(
        packet_id=uuid.uuid4().hex,
        action_id=action_id,
        status=status,
        content_hash=content_hash,
        signals=signals,
        can_decide=False,
    )
    pkt.assert_cannot_decide()
    return pkt
