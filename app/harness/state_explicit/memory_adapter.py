"""B6 Native Memory -> working state: converts an already-built readonly retrieval snapshot.

Input is the envelope of apps/obsidia_api/brody_obsidia_native_memory
.build_native_memory_retrieval_snapshot (retrieval policy unchanged, MEMZUM decides upstream).
No retrieval, no write, no Graphiti / Neo4j fallback. Items are references, not truth.
"""
from __future__ import annotations

from typing import Any, Mapping

from app.harness.state_explicit.contracts import StateEntry, StateStatus, Visibility, error_entry

_SOURCE = "apps.obsidia_api.brody_obsidia_native_memory"
_NO_ENTRY_STATUSES = {"MEMORY_NOT_REQUIRED"}


def native_memory_state_entries(snapshot: Mapping[str, Any]) -> tuple[StateEntry, ...]:
    status = str(snapshot.get("status") or "")
    items = list(snapshot.get("selected_items") or [])
    if status in _NO_ENTRY_STATUSES and not items:
        return ()
    if not items:
        # an unavailable / empty retrieval is explicit unknown state, never a silent absence
        return (StateEntry(state_id="native_memory:status", state_type="NATIVE_MEMORY_STATUS",
                           source_ref=_SOURCE, payload={"status": status or "UNKNOWN"},
                           provenance=(_SOURCE,), uncertainty=(f"native_memory_status:{status or 'UNKNOWN'}",),
                           status=StateStatus.UNKNOWN, tags=("native_memory", "unknown"),
                           summary=f"native memory: {status or 'UNKNOWN'}"),)
    out: list[StateEntry] = []
    for rank, item in enumerate(items, start=1):
        item_id = item.get("id")
        if not item_id:
            out.append(error_entry(f"native_memory:item_{rank}:invalid", _SOURCE, ValueError("missing id"),
                                   state_type="NATIVE_MEMORY_ITEM_ERROR"))
            continue
        payload = {k: item.get(k) for k in ("id", "title", "path", "tags", "score", "excerpt") if k in item}
        payload.update(readonly=True, memory_write=False)
        out.append(StateEntry(state_id=f"native_memory:{item_id}", state_type="NATIVE_MEMORY_ITEM",
                              source_ref=str(item.get("source_ref") or f"{_SOURCE}:{item_id}"), payload=payload,
                              provenance=(_SOURCE,), status=StateStatus.KNOWN, visibility=Visibility.LONG,
                              tags=("native_memory", *(str(t).lower() for t in (item.get("tags") or []))),
                              summary=str(item.get("title") or item_id)))
    return tuple(out)
