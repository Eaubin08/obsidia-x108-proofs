"""B6 WorkingStateRegistry: in-memory session working state (never durable memory).

Entries are addressable by state_id, registered once (a duplicate id fails closed: no
replacement, no in-place update), never persisted and never written anywhere.
"""
from __future__ import annotations

from typing import Any

from app.harness.state_explicit.contracts import BOUNDARY, StateEntry


class DuplicateStateError(ValueError):
    pass


class WorkingStateRegistry:
    def __init__(self) -> None:
        self._entries: dict[str, StateEntry] = {}

    def register(self, entry: StateEntry) -> StateEntry:
        if not isinstance(entry, StateEntry):
            raise TypeError("only StateEntry objects can be registered")
        if entry.state_id in self._entries:
            raise DuplicateStateError(f"state_id already registered: {entry.state_id}")
        self._entries[entry.state_id] = entry
        return entry

    def get(self, state_id: str) -> StateEntry:
        return self._entries[state_id]          # KeyError: unknown ids fail closed

    def list_entries(self) -> tuple[StateEntry, ...]:
        return tuple(self._entries.values())    # registration order

    def snapshot(self) -> dict[str, Any]:
        return {"entries": [e.to_dict() for e in self._entries.values()],
                "durable_memory": False, "boundary": dict(BOUNDARY)}
