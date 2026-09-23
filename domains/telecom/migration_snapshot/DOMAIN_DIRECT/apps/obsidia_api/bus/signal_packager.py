"""
Bus signal packager — F56.

Transforms an external signal into a read-only observation packet.
Never decides. Never acts. Never stores. Never mutates.

Enforcement:
  - All text fields sanitized via sanitize_user_facing_text() (F47.2)
  - accepted_as_observation=True always
  - interpreted_as_command=False always
  - routed_to_decision=False always
  - emitted_act=False always
  - mutation_performed=False always
  - storage_performed=False always
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from apps.obsidia_api.bus.signal_model import SignalInput
from apps.obsidia_api.safe_response import sanitize_user_facing_text

_PAYLOAD_MAX_CHARS = 4096
_CONTEXT_MAX_CHARS = 1024


def _to_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return str(value)


def _clip_and_sanitize(text: str, max_chars: int) -> tuple[str, bool, bool]:
    """Return (sanitized, truncated, forbidden_tokens_found)."""
    truncated = len(text) > max_chars
    clipped = text[:max_chars] if truncated else text
    sanitized = sanitize_user_facing_text(clipped)
    return sanitized, truncated, sanitized != clipped


def build_signal_observation_packet(signal: SignalInput) -> dict[str, Any]:
    """
    Build a read-only observation packet from an external signal.

    Returns a dict suitable for build_output_envelope().
    All string inputs sanitized. No state written. No decision made.
    """
    signal_id = signal.signal_id or str(uuid.uuid4())
    server_ts = datetime.now(timezone.utc).isoformat()
    signal_ts = signal.signal_timestamp or server_ts

    # Sanitize all text fields
    payload_raw = _to_str(signal.signal_payload)
    payload_sanitized, payload_truncated, payload_forbidden = _clip_and_sanitize(
        payload_raw, _PAYLOAD_MAX_CHARS
    )

    origin_sanitized = sanitize_user_facing_text(signal.signal_origin or "")

    context_raw = signal.operator_context or ""
    context_sanitized, context_truncated, context_forbidden = _clip_and_sanitize(
        context_raw, _CONTEXT_MAX_CHARS
    )

    source_sanitized = sanitize_user_facing_text(signal.source_layer or "unknown")
    intent_sanitized = sanitize_user_facing_text(signal.declared_intent or "")

    forbidden_tokens_found = payload_forbidden or context_forbidden
    any_truncated = payload_truncated or context_truncated

    classified_type = signal.signal_type.value
    risk_hint_val = signal.risk_hint.value if signal.risk_hint else "unknown"

    return {
        "status": "OK",
        # Additional sovereignty invariants not in _CORE_BOUNDARY
        "allowed_to_decide": False,
        "advisory_only": True,
        "x108_mutation": False,
        "brody_decision": False,
        # Observation packet
        "signal_observation_packet": {
            "signal_id": signal_id,
            "signal_type": classified_type,
            "signal_origin": origin_sanitized,
            "signal_timestamp": signal_ts,
            "classified_signal_type": classified_type,
            "accepted_as_observation": True,
            "interpreted_as_command": False,
            "routed_to_decision": False,
            "emitted_act": False,
            "mutation_performed": False,
            "storage_performed": False,
            "signal_content_readonly": payload_sanitized,
            "forbidden_tokens_found": forbidden_tokens_found,
            "sanitized": True,
            "truncated": any_truncated,
            "risk_hint": risk_hint_val,
            "source_layer": source_sanitized,
            "correlation_id": signal.correlation_id,
        },
    }
