from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class MemoryCandidatePacket:
    action_id: str
    os3_ticket_id: str
    memory_candidate_id: str
    status: str
    memory_write_allowed: bool
    reason: str
    evidence_refs: list[str]
    hash: str

    def assert_no_write(self) -> None:
        if self.memory_write_allowed:
            raise AssertionError("MEMORY_WRITE_FORBIDDEN_BRIDGE_READONLY")

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "os3_ticket_id": self.os3_ticket_id,
            "memory_candidate_id": self.memory_candidate_id,
            "status": self.status,
            "memory_write_allowed": self.memory_write_allowed,
            "reason": self.reason,
            "evidence_refs": self.evidence_refs,
            "hash": self.hash,
        }


def build_memory_candidate(
    ticket: Any,
    packet: Any,
    action_candidate: Any,
) -> MemoryCandidatePacket:
    m = packet.extra_metrics
    memory_status = m.get("memory_status", "STABLE")

    if memory_status == "UNSTABLE":
        status = "FROZEN"
        reason = "MEMORY_UNSTABLE_CANDIDATE_FROZEN"
    elif str(getattr(ticket, "x108_gate", "UNKNOWN")).upper() not in ("ALLOW",):
        status = "REJECTED"
        reason = f"X108_GATE_{ticket.x108_gate}_NOT_ALLOW"
    elif not (ticket.input_hash and ticket.output_hash and ticket.trace_hash):
        status = "REJECTED"
        reason = "OS3_TICKET_INVALID_HASHES"
    else:
        status = "CANDIDATE_ONLY"
        reason = "MEMORY_CANDIDATE_READONLY_PENDING_HUMAN_REVIEW"

    candidate_id = uuid.uuid4().hex
    evidence_refs = list(getattr(packet, "evidence_refs", [])) + [f"os3:{ticket.ticket_id}"]

    payload = {
        "action_id": action_candidate.action_id,
        "os3_ticket_id": ticket.ticket_id,
        "candidate_id": candidate_id,
        "status": status,
    }
    h = hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()

    result = MemoryCandidatePacket(
        action_id=action_candidate.action_id,
        os3_ticket_id=ticket.ticket_id,
        memory_candidate_id=candidate_id,
        status=status,
        memory_write_allowed=False,
        reason=reason,
        evidence_refs=evidence_refs,
        hash=h,
    )
    result.assert_no_write()
    return result
