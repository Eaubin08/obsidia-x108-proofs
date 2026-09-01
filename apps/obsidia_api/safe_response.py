"""
Safe response wrapper — ensures every API response carries sovereignty invariants.

F47.1 — Protected response envelope hardening:
    Sovereignty flags are re-applied AFTER data merge.

F47.2 — controlled_response.text sanitizer:
    sanitize_user_facing_text() applies word-boundary replacement.

F34 — Runtime Evidence Receipt:
    Every safe backend response receives a readonly runtime evidence receipt.
    The receipt is attestation-only:
        - no decision
        - no action
        - no memory write
        - KX108_ONLY authority
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from apps.obsidia_api.runtime_evidence_receipt import (
    build_runtime_evidence_receipt,
)


# Only mask when Brody appears to be actively EMITTING a sovereign verdict/action.
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


_ISOLATED_TOKEN_RE = re.compile(
    r"\b(ALLOW|HOLD|BLOCK|ACT|DECIDE|VERDICT)\b",
    re.IGNORECASE,
)


_SOVEREIGNTY_PROTECTED: dict[str, Any] = {
    "decision_authority": "KX108_ONLY",
    "allowed_to_decide": False,
    "allowed_to_act": False,
    "readonly": True,
    "advisory_only": True,
    "context_signal_only": True,
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "graphiti_write": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "neo4j_write": False,
    "brody_decision": False,
    "real_action": False,
}


def strip_forbidden_tokens(text: str) -> str:
    """
    Masque uniquement les émissions souveraines.
    Les mentions conceptuelles restent autorisées.
    """

    def _mask(m: re.Match) -> str:
        token = m.group(1)
        return m.group(0)[: -len(token)] + token[0] + "***"

    return _EMISSION_RE.sub(_mask, text)


def sanitize_user_facing_text(text: str) -> str:
    """
    Remplacement des tokens souverains isolés dans les champs exposés.
    """

    return _ISOLATED_TOKEN_RE.sub("[REDACTED]", text)


def safe_backend_response(
    data: dict[str, Any] | None = None,
    source: str = "REAL_BACKEND",
) -> dict[str, Any]:
    """
    Wrapper final API.

    Ordre :
        1. données module
        2. verrou souveraineté
        3. nettoyage exposition
        4. preuve runtime F34
    """

    merged: dict[str, Any] = dict(data) if data else {}

    # F47.1 — sovereignty wins
    merged.update(_SOVEREIGNTY_PROTECTED)

    merged["source"] = source
    merged["timestamp"] = datetime.now(timezone.utc).isoformat()


    # Suppression traces internes
    _INTERNAL_TRACE_KEYS: frozenset[str] = frozenset(
        {
            "internal_trace",
            "system_prompt",
            "raw_prompt",
        }
    )

    for _sk in _INTERNAL_TRACE_KEYS:
        merged.pop(_sk, None)


    # F47.2 — text sanitization
    for field in ("response", "response_text"):
        if field in merged and isinstance(merged[field], str):
            merged[field] = strip_forbidden_tokens(
                merged[field]
            )


    cr = merged.get("controlled_response")

    if isinstance(cr, dict) and isinstance(cr.get("text"), str):
        cr["text"] = sanitize_user_facing_text(
            cr["text"]
        )


    # ==========================================================
    # F34 — Runtime Evidence Receipt
    # ==========================================================
    try:
        merged["runtime_evidence_receipt"] = (
            build_runtime_evidence_receipt(
                source=source,
                envelope=merged,
            )
        )

    except Exception as exc:
        merged["runtime_evidence_receipt"] = {
            "status": "EVIDENCE_BUILD_FAILED",
            "reason": str(exc),
            "decision_authority": "KX108_ONLY",
            "readonly": True,
            "attestation_only": True,
            "emits_act": False,
        }


    return merged