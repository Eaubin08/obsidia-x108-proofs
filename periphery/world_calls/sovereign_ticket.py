from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any


@dataclass
class SovereignTicket:
    ticket_id: str
    action_id: str
    os3_ticket_id: str
    scope: str
    issued_at: str
    expires_at: str
    x108_gate: str
    autonomy_level: int
    dry_run_only: bool = True
    world_call_class: str = "NO_WORLD_CALL"
    hash: str = ""

    def is_expired(self) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        return now > self.expires_at

    def is_valid_scope(self, required_scope: str) -> bool:
        return self.scope == required_scope or self.scope == "*"

    def assert_not_expired(self) -> None:
        if self.is_expired():
            raise AssertionError(f"SOVEREIGN_TICKET_EXPIRED:{self.ticket_id}")

    def assert_scope(self, required_scope: str) -> None:
        if not self.is_valid_scope(required_scope):
            raise AssertionError(f"SOVEREIGN_TICKET_INVALID_SCOPE:{self.scope}!={required_scope}")

    def assert_dry_run(self) -> None:
        if not self.dry_run_only:
            raise AssertionError("SOVEREIGN_TICKET_NOT_DRY_RUN")

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticket_id": self.ticket_id,
            "action_id": self.action_id,
            "os3_ticket_id": self.os3_ticket_id,
            "scope": self.scope,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "x108_gate": self.x108_gate,
            "autonomy_level": self.autonomy_level,
            "dry_run_only": self.dry_run_only,
            "world_call_class": self.world_call_class,
            "hash": self.hash,
        }


def issue_sovereign_ticket(
    action_id: str,
    os3_ticket_id: str,
    x108_gate: str,
    scope: str,
    autonomy_level: int,
    world_call_class: str,
    ttl_seconds: int = 300,
) -> SovereignTicket:
    now = datetime.now(timezone.utc)
    issued_at = now.isoformat()
    expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
    ticket_id = uuid.uuid4().hex

    payload = {
        "ticket_id": ticket_id,
        "action_id": action_id,
        "os3_ticket_id": os3_ticket_id,
        "scope": scope,
        "issued_at": issued_at,
        "x108_gate": x108_gate,
    }
    h = hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()

    return SovereignTicket(
        ticket_id=ticket_id,
        action_id=action_id,
        os3_ticket_id=os3_ticket_id,
        scope=scope,
        issued_at=issued_at,
        expires_at=expires_at,
        x108_gate=x108_gate,
        autonomy_level=autonomy_level,
        dry_run_only=True,
        world_call_class=world_call_class,
        hash=h,
    )


def require_ticket_or_block(ticket: SovereignTicket | None) -> None:
    if ticket is None:
        raise AssertionError("NO_SOVEREIGN_TICKET_NO_WORLD_CALL")
    ticket.assert_not_expired()
    ticket.assert_dry_run()
