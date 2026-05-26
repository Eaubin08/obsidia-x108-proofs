"""
Interface Event Log — append-only log of interface events.
Read-only view of events. No state mutation.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DEFAULT_LOG_PATH = Path("_local_audits") / "interface_event_log.jsonl"


@dataclass
class InterfaceEvent:
    event_id: str
    session_id: str
    event_type: str
    details: dict
    timestamp: str
    readonly: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "event_type": self.event_type,
            "details": self.details,
            "timestamp": self.timestamp,
            "readonly": self.readonly,
        }


def log_interface_event(
    session_id: str,
    event_type: str,
    details: dict | None = None,
    log_path: Path | None = None,
) -> InterfaceEvent:
    evt = InterfaceEvent(
        event_id=uuid.uuid4().hex,
        session_id=session_id,
        event_type=event_type,
        details=details or {},
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    path = log_path or _DEFAULT_LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(evt.to_dict()) + "\n")
    return evt
