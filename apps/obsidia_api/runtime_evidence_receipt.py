"""
OBSIDIA Runtime Evidence Receipt V1

Surface d'attestation readonly du runtime API.
Ne décide pas.
N'exécute pas.
N'écrit aucune mémoire.
"""

from __future__ import annotations

from datetime import datetime, timezone
import uuid


def build_runtime_evidence_receipt(
    *,
    source: str = "BRODY_CHAT",
    trace_id: str | None = None,
    envelope: dict | None = None,
) -> dict:
    envelope = envelope or {}

    return {
        "receipt_id": f"rte-{uuid.uuid4().hex}",
        "trace_id": trace_id or f"trace-{uuid.uuid4().hex}",
        "source": source,
        "timestamp": datetime.now(timezone.utc).isoformat(),

        "decision_authority": "KX108_ONLY",

        "readonly": True,
        "attestation_only": True,

        "emits_act": False,
        "emits_verdict": False,
        "allowed_to_decide": False,
        "allowed_to_act": False,

        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "kernel_mutation": False,

        "runtime_path": "OBSIDIA_API",
        "envelope_verified": bool(envelope),
    }


def verify_runtime_evidence_receipt(receipt: dict) -> None:
    assert receipt["decision_authority"] == "KX108_ONLY"
    assert receipt["readonly"] is True
    assert receipt["attestation_only"] is True

    assert receipt["emits_act"] is False
    assert receipt["allowed_to_act"] is False
    assert receipt["allowed_to_decide"] is False

    assert receipt["memory_write"] is False
    assert receipt["graphiti_write"] is False
    assert receipt["neo4j_write"] is False
    assert receipt["kernel_mutation"] is False

    assert receipt.get("trace_id")