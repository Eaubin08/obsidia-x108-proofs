"""E11 COGNITION SHADOW MEMORY V0: an already-computed native memory retrieval snapshot -> B6, beside SENS -> B7.

Read-only composition of certified functions (D1 retrieval snapshot V1 only, D2 B7 on SENS entries only).
It never retrieves, generates, proposes, promotes, persists, acts or decides (decision authority: KX108_ONLY).
Invalid snapshots fail closed; errors from the certified layers propagate unchanged.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.cognition.b7.detector import detect_unresolved
from app.harness.state_explicit.context_assembly import assemble_context
from app.harness.state_explicit.contracts import BOUNDARY
from app.harness.state_explicit.memory_adapter import native_memory_state_entries
from app.harness.state_explicit.registry import WorkingStateRegistry
from app.harness.state_explicit.sens_adapter import sens_state_entries

SCHEMA = "COGNITION_SHADOW_MEMORY_V0"
SNAPSHOT_SCHEMA = "OBSIDIA_NATIVE_MEMORY_RETRIEVAL_V1"
BOUNDARY_KEYS = ("readonly", "decision_authority", "memory_write", "emits_act", "kernel_mutation")
SNAPSHOT_REF_KEYS = ("schema_version", "status", "query", "selected_items_count")
# a Brody response envelope carries these; a retrieval snapshot never does
RESPONSE_ENVELOPE_KEYS = ("retrieval_status", "local_response_engine_used", "attempted_queries", "query_results_count")
AUTHORITY_FLAGS = ("memory_write", "emits_act", "kernel_mutation")


def _validate_snapshot(snapshot: Any) -> None:
    if not isinstance(snapshot, Mapping):
        raise TypeError("memory_snapshot must be a Mapping")
    if snapshot.get("schema_version") != SNAPSHOT_SCHEMA:
        raise ValueError(f"memory_snapshot schema_version must be {SNAPSHOT_SCHEMA}")
    envelope = [k for k in RESPONSE_ENVELOPE_KEYS if k in snapshot]
    if envelope:
        raise ValueError(f"memory response envelope rejected (keys: {envelope})")
    status = snapshot.get("status")
    if not isinstance(status, str) or not status:
        raise ValueError("memory_snapshot status must be a non-empty string")
    if not isinstance(snapshot.get("selected_items"), list):
        raise ValueError("memory_snapshot selected_items must be a list")
    active = [k for k in AUTHORITY_FLAGS if snapshot.get(k)]
    if active:
        raise ValueError(f"memory_snapshot carries forbidden authority flags: {active}")


def run_cognition_shadow_with_memory(text: str, memory_snapshot: Mapping) -> dict[str, Any]:
    _validate_snapshot(memory_snapshot)
    entries = sens_state_entries(text)
    registry = WorkingStateRegistry()
    for entry in entries:
        registry.register(entry)
    memory_entries = native_memory_state_entries(memory_snapshot)
    packet = assemble_context(text, registry, memory_entries=memory_entries)
    requests = [request for entry in entries for request in detect_unresolved(entry)]
    return {
        "schema": SCHEMA,
        "input_text": text,
        "memory_snapshot_ref": {key: memory_snapshot.get(key) for key in SNAPSHOT_REF_KEYS},
        "state_entries": [entry.to_dict() for entry in entries],
        "memory_entries": [entry.to_dict() for entry in memory_entries],
        "context_packet": packet.to_dict(),
        "resolution_requests": [request.to_dict() for request in requests],
        "boundary": {key: BOUNDARY[key] for key in BOUNDARY_KEYS},
    }
