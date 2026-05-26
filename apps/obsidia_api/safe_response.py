"""
Safe response wrapper — ensures every API response carries sovereignty invariants.
"""
from __future__ import annotations
import re
from datetime import datetime, timezone
from typing import Any

# Only mask when Brody appears to be actively EMITTING a sovereign verdict/action.
# Conceptual mentions ("Brody ne peut pas autoriser ACT") are allowed through.
_EMISSION_RE = re.compile(
    r"(?:"
    r"j['']?[eé]mets?\s+(?:un\s+)?"
    r"|j['']?autorise\s+(?:un\s+)?"
    r"|je\s+d[eé]clenche\s+(?:un\s+)?"
    r"|brody\s+[eé]met\s+"
    r"|brody\s+autorise\s+"
    r"|brody\s+d[eé]clenche\s+"
    r")"
    r"(ACT|HOLD|BLOCK|ALLOW|VERDICT|DECIDE)\b",
    re.IGNORECASE,
)


def strip_forbidden_tokens(text: str) -> str:
    """Mask only sovereign-emission patterns — not conceptual mentions.
    'Brody ne peut pas autoriser ACT' passes through unchanged.
    'j'émets ACT' becomes 'j'émets A***'.
    """
    def _mask(m: re.Match) -> str:
        token = m.group(1)
        return m.group(0)[: -len(token)] + token[0] + "***"
    return _EMISSION_RE.sub(_mask, text)


def safe_backend_response(
    data: dict[str, Any] | None = None,
    source: str = "REAL_BACKEND",
) -> dict[str, Any]:
    """Wrap any API response with sovereignty invariants."""
    base: dict[str, Any] = {
        "readonly": True,
        "advisory_only": True,
        "emits_act": False,
        "emits_verdict": False,
        "decision_authority": "KX108_ONLY",
        "memory_write": False,
        "kernel_mutation": False,
        "real_action": False,
        "source": source,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if data:
        base.update(data)
    # Sanitize any response_text field
    if "response" in base and isinstance(base["response"], str):
        base["response"] = strip_forbidden_tokens(base["response"])
    if "response_text" in base and isinstance(base["response_text"], str):
        base["response_text"] = strip_forbidden_tokens(base["response_text"])
    return base
