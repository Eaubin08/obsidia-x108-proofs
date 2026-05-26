"""
OnChain Audit Packet — immutable record of a blockchain governance decision.
Read-only. No real chain writes.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class OnChainAuditPacket:
    packet_id: str
    action_id: str
    chain_id: str
    action_class: str
    gate_result: str
    reason: str
    risk_flags: list[str]
    timestamp: str
    dry_run_only: bool = True
    real_chain_write: bool = False
    hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "action_id": self.action_id,
            "chain_id": self.chain_id,
            "action_class": self.action_class,
            "gate_result": self.gate_result,
            "reason": self.reason,
            "risk_flags": self.risk_flags,
            "timestamp": self.timestamp,
            "dry_run_only": self.dry_run_only,
            "real_chain_write": self.real_chain_write,
            "hash": self.hash,
        }


def build_onchain_audit_packet(
    action_id: str,
    chain_id: str,
    action_class: str,
    gate_result: str,
    reason: str,
    risk_flags: list[str] | None = None,
) -> OnChainAuditPacket:
    ts = datetime.now(timezone.utc).isoformat()
    packet_id = uuid.uuid4().hex
    payload = {
        "packet_id": packet_id,
        "action_id": action_id,
        "chain_id": chain_id,
        "action_class": action_class,
        "gate_result": gate_result,
        "timestamp": ts,
    }
    h = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return OnChainAuditPacket(
        packet_id=packet_id,
        action_id=action_id,
        chain_id=chain_id,
        action_class=action_class,
        gate_result=gate_result,
        reason=reason,
        risk_flags=risk_flags or [],
        timestamp=ts,
        dry_run_only=True,
        real_chain_write=False,
        hash=h,
    )
