"""
Output Envelope V1 — Standardized API response wrapper.
==========================================================
Implements the output contract validated in /api/brody/chat:
  - Boundary flags (KX108_ONLY, no writes)
  - Compact/debug packetization
  - Evidence fields
  - Deep snapshot omission markers

Usage:
    from apps.obsidia_api.output_envelope import build_output_envelope
    return build_output_envelope(data, compact=compact, debug=debug, route="/bus/stats")

Principle: The engine produces. The envelope transports.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

# ── Core fields always present in the envelope ─────────────────────────────
_CORE_BOUNDARY: dict[str, Any] = {
    "decision_authority": "KX108_ONLY",
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "kernel_mutation": False,
    "readonly": True,
}

# ── Fields kept in compact mode ──────────────────────────────────────────
_COMPACT_KEEP = {
    "status", "route", "source",
    "decision_authority", "emits_act", "emits_verdict",
    "memory_write", "graphiti_write", "neo4j_write",
    "kernel_mutation", "readonly",
    "compact", "debug", "timestamp",
}


def build_output_envelope(
    data: dict[str, Any],
    *,
    compact: bool = False,
    debug: bool = False,
    source: str = "OBSIDIA_API",
    route: str = "",
) -> dict[str, Any]:
    """
    Wrap response data in a standardized output envelope.

    Parameters:
        data: The response payload from the route handler.
        compact: Return light payload (core fields only).
        debug: Return full payload with all internal data.
        source: Source identifier.
        route: Route identifier (e.g. "/bus/stats").

    Returns:
        Enveloped dict with boundary flags + packetization.
    """
    # ── Build base payload ───────────────────────────────────────────────
    payload: dict[str, Any] = {
        **_CORE_BOUNDARY,
        "source": source,
        "route": route,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "compact": compact,
        "debug": debug,
    }

    if debug:
        # Full payload: merge all original data
        payload.update(data)
        return payload

    if compact:
        # Light payload: keep only core fields + compact markers
        for k, v in data.items():
            if k in _COMPACT_KEEP:
                payload[k] = v
        payload["deep_snapshots_omitted"] = True
        payload["deep_snapshots_available"] = True
        payload["debug_payload_omitted"] = True
        payload["debug_payload_available"] = True
        payload["omitted_debug_fields"] = [
            k for k in data if k not in _COMPACT_KEEP
        ]
        return payload

    # Default: merge data + boundary, keep backward-compatible
    payload.update(data)
    return payload
