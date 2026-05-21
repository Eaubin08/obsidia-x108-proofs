"""
Context Packet Exporter — serializes a context packet for audit/handoff.
Export is always read-only, dry-run, advisory only.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExportedContextPacket:
    packet_id: str
    export_hash: str
    payload: dict[str, Any]
    dry_run_only: bool = True
    readonly: bool = True
    decision_authority: str = "KX108_ONLY"

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "export_hash": self.export_hash,
            "payload": self.payload,
            "dry_run_only": self.dry_run_only,
            "readonly": self.readonly,
            "decision_authority": self.decision_authority,
        }


def export_context_packet(packet: dict[str, Any]) -> ExportedContextPacket:
    packet_id = packet.get("packet_id", "unknown")
    serialized = json.dumps(packet, sort_keys=True, default=str)
    export_hash = hashlib.sha256(serialized.encode()).hexdigest()

    return ExportedContextPacket(
        packet_id=packet_id,
        export_hash=export_hash,
        payload=packet,
        dry_run_only=True,
        readonly=True,
        decision_authority="KX108_ONLY",
    )
