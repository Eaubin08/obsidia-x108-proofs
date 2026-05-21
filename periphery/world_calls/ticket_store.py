from __future__ import annotations

import json
import os
from typing import Any

from .sovereign_ticket import SovereignTicket

_DEFAULT_STORE = os.path.join(
    os.path.dirname(__file__), "..", "..", "audit", "sovereign_tickets.jsonl"
)


def store_ticket(ticket: SovereignTicket, store_path: str | None = None) -> None:
    path = store_path or _DEFAULT_STORE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(ticket.to_dict(), ensure_ascii=False) + "\n")


def load_tickets(store_path: str | None = None) -> list[dict[str, Any]]:
    path = store_path or _DEFAULT_STORE
    if not os.path.exists(path):
        return []
    entries = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries
