"""COGNITION SHADOW V0: read-only composition SENS -> B6 working state -> B6 ContextPacket -> B7 detection.

Composes only certified functions; it never proposes, resolves, promotes, persists, acts or decides
(decision authority: KX108_ONLY). Errors from the certified layers propagate unchanged.
"""
from __future__ import annotations

from typing import Any

from app.cognition.b7.detector import detect_unresolved
from app.harness.state_explicit.context_assembly import assemble_context
from app.harness.state_explicit.contracts import BOUNDARY
from app.harness.state_explicit.registry import WorkingStateRegistry
from app.harness.state_explicit.sens_adapter import sens_state_entries

SCHEMA = "COGNITION_SHADOW_V0"
BOUNDARY_KEYS = ("readonly", "decision_authority", "memory_write", "emits_act", "kernel_mutation")


def run_cognition_shadow(text: str) -> dict[str, Any]:
    entries = sens_state_entries(text)
    registry = WorkingStateRegistry()
    for entry in entries:
        registry.register(entry)
    packet = assemble_context(text, registry)
    requests = [request for entry in entries for request in detect_unresolved(entry)]
    return {
        "schema": SCHEMA,
        "input_text": text,
        "state_entries": [entry.to_dict() for entry in entries],
        "context_packet": packet.to_dict(),
        "resolution_requests": [request.to_dict() for request in requests],
        "boundary": {key: BOUNDARY[key] for key in BOUNDARY_KEYS},
    }
