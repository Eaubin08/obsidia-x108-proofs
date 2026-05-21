from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class OS3ReplayManifest:
    manifest_id: str
    os3_ticket_id: str
    action_id: str
    original_input_hash: str
    original_output_hash: str
    original_trace_hash: str
    original_merkle_root: str
    replay_status: str = "NOT_RUN"
    replay_hash: str = ""
    replay_compare_result: str = "PENDING"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "os3_ticket_id": self.os3_ticket_id,
            "action_id": self.action_id,
            "original_input_hash": self.original_input_hash,
            "original_output_hash": self.original_output_hash,
            "original_trace_hash": self.original_trace_hash,
            "original_merkle_root": self.original_merkle_root,
            "replay_status": self.replay_status,
            "replay_hash": self.replay_hash,
            "replay_compare_result": self.replay_compare_result,
            "notes": self.notes,
        }


def build_replay_manifest(ticket: Any) -> OS3ReplayManifest:
    import uuid
    return OS3ReplayManifest(
        manifest_id=uuid.uuid4().hex,
        os3_ticket_id=ticket.ticket_id,
        action_id=ticket.action_id,
        original_input_hash=ticket.input_hash,
        original_output_hash=ticket.output_hash,
        original_trace_hash=ticket.trace_hash,
        original_merkle_root=ticket.merkle_root,
    )
