"""
F32 — Brody Full Runtime Integration Readonly Packet.

Assembles all 7 readonly surfaces (F23A6.2 → F30) into a single certified
readonly packet. Each surface is wrapped in try/except: if a surface cannot
be built it returns status="MISSING_SURFACE_READONLY_DEGRADED" instead of
raising, so the packet always completes.

BOUNDARY (enforced on every output):
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

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


PACKET_ID = "F32_BRODY_FULL_RUNTIME_INTEGRATION_READONLY_PACKET"
VERSION = "F32_V1"
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

_SURFACE_NAMES = (
    "sigma_dispatcher",
    "tree_signal_packet",
    "monitoring_adapters",
    "operator_view_packet",
    "brody_runtime_context",
    "workflow_governance_readonly",
    "neo4j_guide_bridge",
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _degraded(surface: str, reason: str) -> dict[str, Any]:
    return {
        "status": "MISSING_SURFACE_READONLY_DEGRADED",
        "surface": surface,
        "reason": reason,
        **BOUNDARY,
    }


def _packet_sha256(ready: int, total: int, integration_status: str) -> str:
    payload = json.dumps(
        {"packet_id": PACKET_ID, "surfaces_ready": ready,
         "surfaces_total": total, "integration_status": integration_status},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest().upper()


# ── Surface builders (lazy imports — no circular dependency at module level) ──

def _build_sigma_dispatcher(
    domain: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    try:
        from sigma.evaluate import evaluate_sigma_domain  # noqa: PLC0415
        result = evaluate_sigma_domain(domain, payload)
        return {"status": "READY", "domain": domain, "result": result, **BOUNDARY}
    except Exception as exc:
        return _degraded("sigma_dispatcher", str(exc))


def _build_tree_signal(
    signal_id: str,
    activations: list[float],
    theta: float,
    domain_sigma_envelope: dict[str, Any],
) -> dict[str, Any]:
    try:
        from periphery.cognitive_trees.tree_signal_packet import build_tree_signal_packet  # noqa: PLC0415
        pkt = build_tree_signal_packet(
            signal_id,
            activations,
            theta=theta,
            domain_sigma_envelope=domain_sigma_envelope,
        )
        return {"status": "READY", "result": pkt.to_dict(), **BOUNDARY}
    except Exception as exc:
        return _degraded("tree_signal_packet", str(exc))


def _build_monitoring_adapters(
    sigma_payload: dict[str, Any],
) -> dict[str, Any]:
    try:
        from periphery.adapters.bank_adapter import build_bank_action, build_bank_state  # noqa: PLC0415
        from periphery.adapters.gps_adapter import build_gps_action, build_gps_state  # noqa: PLC0415
        from periphery.adapters.trading_adapter import (  # noqa: PLC0415
            build_trading_action,
            build_trading_state,
        )
        from periphery.control_plane import run_control_plane  # noqa: PLC0415
        from sigma.evaluate import evaluate_sigma_domain  # noqa: PLC0415

        adapters: dict[str, Any] = {}
        for dom, state_fn, action_fn in (
            ("bank", build_bank_state, build_bank_action),
            ("gps_defense_aviation", build_gps_state, build_gps_action),
            ("trading", build_trading_state, build_trading_action),
        ):
            try:
                state = state_fn(sigma_payload)
                action = action_fn(sigma_payload)
                ctrl = run_control_plane(action)
                ctrl.assert_non_sovereign()
                state_dict = dict(getattr(state, "__dict__", {}))
                dse = evaluate_sigma_domain(dom, state_dict)
                adapters[dom] = {
                    "status": "READY",
                    "control_packet_non_sovereign": True,
                    "domain_sigma_attached": True,
                    "domain_sigma_gate": dse.get("x108_gate", "HOLD"),
                    "decision_authority": "KX108_ONLY",
                }
            except Exception as inner:
                adapters[dom] = {
                    "status": "DEGRADED",
                    "reason": str(inner),
                    "decision_authority": "KX108_ONLY",
                }

        ready_adapters = sum(1 for v in adapters.values() if v.get("status") == "READY")
        return {
            "status": "READY",
            "adapters": adapters,
            "adapters_ready": ready_adapters,
            "adapters_total": len(adapters),
            **BOUNDARY,
        }
    except Exception as exc:
        return _degraded("monitoring_adapters", str(exc))


def _build_operator_view(
    domain_sigma_envelope: dict[str, Any],
    tree_signal_packet_dict: dict[str, Any],
) -> dict[str, Any]:
    try:
        from apps.obsidia_api.brody_operator_view_packet import build_operator_view_packet  # noqa: PLC0415
        result = build_operator_view_packet(
            domain_sigma_envelope=domain_sigma_envelope,
            tree_signal_packet=tree_signal_packet_dict,
        )
        return {"status": "READY", "result": result, **BOUNDARY}
    except Exception as exc:
        return _degraded("operator_view_packet", str(exc))


def _build_runtime_context(
    domain_sigma_envelope: dict[str, Any],
    tree_signal_packet_dict: dict[str, Any],
    operator_view_packet: dict[str, Any],
) -> dict[str, Any]:
    try:
        from apps.obsidia_api.brody_runtime_context_adapter import build_runtime_context  # noqa: PLC0415
        ctx = build_runtime_context(
            domain_sigma_envelope_snapshot=domain_sigma_envelope,
            tree_signal_packet_snapshot=tree_signal_packet_dict,
            brody_full_context=operator_view_packet,
        )
        return {"status": "READY", "result": ctx, **BOUNDARY}
    except Exception as exc:
        return _degraded("brody_runtime_context", str(exc))


def _build_workflow_governance(
    sop_text: str,
    title: str,
    session_id: str,
    request_type: str,
) -> dict[str, Any]:
    try:
        from periphery.workflow_governance_readonly.integration.brody_workflow_governance_snapshot_adapter import (  # noqa: PLC0415,E501
            build_brody_workflow_governance_snapshot,
        )
        snapshot = build_brody_workflow_governance_snapshot(
            sop_text=sop_text,
            title=title,
            session_id=session_id,
            request_type=request_type,
        )
        return {"status": "READY", "result": snapshot, **BOUNDARY}
    except Exception as exc:
        return _degraded("workflow_governance_readonly", str(exc))


def _build_neo4j_guide_bridge() -> dict[str, Any]:
    try:
        from periphery.brody_memory_readonly.neo4j_brody_guide_bridge_readonly.brody_neo4j_guide_bridge_readonly_v1 import (  # noqa: PLC0415,E501
            BOUNDARY as NEO4J_BOUNDARY,
            MANUAL_NEO4J_WRITE_CONFIRMATION,
            MANUAL_NEO4J_WRITE_ENV,
        )
        return {
            "status": "READY",
            "guard_mode": "DOUBLE_GUARD_MANUAL_ONLY",
            "write_surface": "GUARDED_NOT_AUTO_ACCESSIBLE",
            "requires_env": NEO4J_WRITE_ENV if (NEO4J_WRITE_ENV := MANUAL_NEO4J_WRITE_ENV) else "",
            "requires_token": MANUAL_NEO4J_WRITE_CONFIRMATION,
            "runtime_auto_accessible": False,
            "neo4j_boundary": {
                k: v for k, v in NEO4J_BOUNDARY.items()
            },
            **BOUNDARY,
        }
    except Exception as exc:
        return _degraded("neo4j_guide_bridge", str(exc))


# ── Main builder ──────────────────────────────────────────────────────────────

def build_f32_full_runtime_integration_packet(
    *,
    domain: str = "bank",
    sigma_payload: dict[str, Any] | None = None,
    sop_text: str = (
        "1. Read readonly request\n"
        "2. Validate contract boundary\n"
        "3. Prepare readonly advisory response"
    ),
    title: str = "F32 integration readonly",
    session_id: str = "f32-integration",
    signal_id: str = "f32-tree-signal",
    activations: list[float] | None = None,
    theta: float = 0.15,
    request_type: str = "STRUCTURAL_PREPARATION",
) -> dict[str, Any]:
    """
    Assemble all 7 readonly runtime surfaces into a single certified packet.

    Each surface is tried independently; a failure degrades that surface to
    status="MISSING_SURFACE_READONLY_DEGRADED" without aborting the packet.

    Returns a dict with:
        packet_id, version, integration_status, surfaces_ready/missing/total,
        packet_sha256, surfaces{7}, and the full BOUNDARY block.
    """
    sp = sigma_payload or {}
    acts: list[float] = activations if activations is not None else [0.0] * 34

    # 1 — sigma dispatcher (F23A6.2)
    sigma = _build_sigma_dispatcher(domain, sp)
    dse = sigma["result"] if sigma["status"] == "READY" else {}

    # 2 — tree signal packet (F27)
    tree = _build_tree_signal(signal_id, acts, theta, dse)
    tsp_dict = tree["result"] if tree["status"] == "READY" else {}

    # 3 — monitoring adapters bank/gps/trading (F23A4.6)
    monitoring = _build_monitoring_adapters(sp)

    # 4 — operator view packet (F28.2)
    operator_view = _build_operator_view(dse, tsp_dict)
    ovp_result = operator_view["result"] if operator_view["status"] == "READY" else {}

    # 5 — brody runtime context (F26/F28)
    runtime_ctx = _build_runtime_context(dse, tsp_dict, ovp_result)

    # 6 — workflow governance readonly (F30.4)
    workflow = _build_workflow_governance(sop_text, title, session_id, request_type)

    # 7 — neo4j guide bridge guard inspection (F29)
    neo4j = _build_neo4j_guide_bridge()

    surfaces: dict[str, Any] = {
        "sigma_dispatcher": sigma,
        "tree_signal_packet": tree,
        "monitoring_adapters": monitoring,
        "operator_view_packet": operator_view,
        "brody_runtime_context": runtime_ctx,
        "workflow_governance_readonly": workflow,
        "neo4j_guide_bridge": neo4j,
    }

    ready = sum(1 for s in surfaces.values() if s.get("status") == "READY")
    missing = sum(1 for s in surfaces.values() if s.get("status") == "MISSING_SURFACE_READONLY_DEGRADED")
    total = len(surfaces)

    integration_status = (
        "READY_READONLY" if missing == 0
        else f"PARTIAL_READONLY_{ready}_OF_{total}"
    )

    return {
        "packet_id": PACKET_ID,
        "version": VERSION,
        "created_at": _ts(),
        "mode": "READONLY",
        "proof_status": PROOF_STATUS,
        "integration_status": integration_status,
        "surfaces_ready": ready,
        "surfaces_missing": missing,
        "surfaces_total": total,
        "packet_sha256": _packet_sha256(ready, total, integration_status),
        "surfaces": surfaces,
        **BOUNDARY,
    }
