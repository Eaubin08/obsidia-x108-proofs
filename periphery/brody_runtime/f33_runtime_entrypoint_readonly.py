"""
F33 — Brody Runtime Entrypoint Readonly.

Consumable adapter over the F32 full runtime integration packet.
Exposes `call_brody_runtime_entrypoint()` for direct call, API route,
and audit invocation. Adds entrypoint envelope (id, version, called_at,
entrypoint_status) over the F32 packet.

BOUNDARY (re-enforced — inherited from F32):
    decision_authority = KX108_ONLY
    allowed_to_decide  = False
    emits_act          = False
    emits_verdict      = False
    kernel_mutation    = False
    x108_mutation      = False
    neo4j_write        = False
    memory_write       = False
    graphiti_write     = False
    runtime_execute    = False

PATCH_RUNTIME = NO  |  COMMIT = NO  |  TAG = NO  |  PUSH = NO
proof_status  = RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


ENTRYPOINT_ID = "F33_BRODY_RUNTIME_ENTRYPOINT_READONLY"
VERSION = "F33_V1"
PROOF_STATUS = "RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN"

BOUNDARY: dict[str, Any] = {
    "decision_authority": "KX108_ONLY",
    "allowed_to_decide": False,
    "readonly": True,
    "advisory_only": True,
    "context_signal_only": True,
    "can_decide": False,
    "can_emit_act": False,
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "runtime_execute": False,
}


def call_brody_runtime_entrypoint(
    *,
    domain: str = "bank",
    sigma_payload: dict[str, Any] | None = None,
    sop_text: str = (
        "1. Read readonly request\n"
        "2. Validate contract boundary\n"
        "3. Prepare readonly advisory response"
    ),
    title: str = "F33 entrypoint readonly",
    session_id: str = "f33-entrypoint",
    signal_id: str = "f33-tree-signal",
    activations: list[float] | None = None,
    theta: float = 0.15,
    request_type: str = "STRUCTURAL_PREPARATION",
) -> dict[str, Any]:
    """
    Call the F32 runtime integration packet via the F33 consumable entrypoint.

    Returns a certified readonly entrypoint envelope wrapping the F32 packet:
        entrypoint_id, version, called_at, entrypoint_status,
        f32_packet (full 7-surface packet),
        surfaces_ready/missing/total, integration_status,
        proof_status, and the full BOUNDARY block.
    """
    from periphery.brody_runtime.f32_full_runtime_integration_readonly_packet import (  # noqa: PLC0415
        build_f32_full_runtime_integration_packet,
    )

    f32_packet = build_f32_full_runtime_integration_packet(
        domain=domain,
        sigma_payload=sigma_payload,
        sop_text=sop_text,
        title=title,
        session_id=session_id,
        signal_id=signal_id,
        activations=activations,
        theta=theta,
        request_type=request_type,
    )

    surfaces_ready = f32_packet.get("surfaces_ready", 0)
    surfaces_missing = f32_packet.get("surfaces_missing", 0)
    surfaces_total = f32_packet.get("surfaces_total", 0)
    integration_status = f32_packet.get("integration_status", "UNKNOWN")

    entrypoint_status = (
        "ENTRYPOINT_READY_READONLY"
        if integration_status == "READY_READONLY"
        else f"ENTRYPOINT_PARTIAL_{surfaces_ready}_OF_{surfaces_total}"
    )

    return {
        "entrypoint_id": ENTRYPOINT_ID,
        "version": VERSION,
        "called_at": datetime.now(timezone.utc).isoformat(),
        "proof_status": PROOF_STATUS,
        "entrypoint_status": entrypoint_status,
        "integration_status": integration_status,
        "surfaces_ready": surfaces_ready,
        "surfaces_missing": surfaces_missing,
        "surfaces_total": surfaces_total,
        "f32_packet": f32_packet,
        **BOUNDARY,
    }
