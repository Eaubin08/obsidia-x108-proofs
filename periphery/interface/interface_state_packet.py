"""
Interface State Packet — captures current interface state for display.
Read-only view. Never mutates state.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class InterfaceStatePacket:
    packet_id: str
    session_id: str
    phase: str
    memory_status: str
    brody_status: str
    graphiti_status: str
    context_ready: bool
    readonly: bool = True
    can_emit_act: bool = False
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "session_id": self.session_id,
            "phase": self.phase,
            "memory_status": self.memory_status,
            "brody_status": self.brody_status,
            "graphiti_status": self.graphiti_status,
            "context_ready": self.context_ready,
            "readonly": self.readonly,
            "can_emit_act": self.can_emit_act,
            "timestamp": self.timestamp,
        }


def build_interface_state_packet(
    session_id: str,
    phase: str = "ACTIVE",
    memory_status: str = "CANDIDATE_ONLY",
    brody_status: str = "READONLY",
    graphiti_status: str = "READONLY",
) -> InterfaceStatePacket:
    return InterfaceStatePacket(
        packet_id=uuid.uuid4().hex,
        session_id=session_id,
        phase=phase,
        memory_status=memory_status,
        brody_status=brody_status,
        graphiti_status=graphiti_status,
        context_ready=True,
        readonly=True,
        can_emit_act=False,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
