"""
WorldActionBus — append-only local journal of world action intentions.
No real egress. Dry-run only. No API calls.
"""
from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

_DEFAULT_BUS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "audit", "world_action_bus.jsonl"
)


@dataclass
class WorldActionEvent:
    event_id: str
    action_id: str
    sovereign_ticket_id: str
    world_call_class: str
    action_risk_class: str
    autonomy_level: int
    intent: str
    domain: str
    dry_run_only: bool
    blocked: bool
    block_reason: str
    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def publish_event(
    action_id: str,
    sovereign_ticket_id: str,
    world_call_class: str,
    action_risk_class: str,
    autonomy_level: int,
    intent: str,
    domain: str,
    blocked: bool = True,
    block_reason: str = "",
    bus_path: str | None = None,
) -> WorldActionEvent:
    path = bus_path or _DEFAULT_BUS_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)

    event = WorldActionEvent(
        event_id=uuid.uuid4().hex,
        action_id=action_id,
        sovereign_ticket_id=sovereign_ticket_id,
        world_call_class=world_call_class,
        action_risk_class=action_risk_class,
        autonomy_level=autonomy_level,
        intent=intent,
        domain=domain,
        dry_run_only=True,
        blocked=blocked,
        block_reason=block_reason,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")

    return event
