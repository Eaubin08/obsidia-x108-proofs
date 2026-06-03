# runtime_wiring/engine_bridge/api_adapter_preview.py
# P10B — API preview builder. Prepares engine-compatible JSON payload.
# NO apps/obsidia_api import. NO periphery import. NO live HTTP call.
# NO route creation. KX108_ONLY. DRY_RUN_PREVIEW_ONLY.

from __future__ import annotations

from typing import Any, Dict, List

from runtime_wiring.engine_bridge.bridge_types import EngineBridgeOutput

# ── Preview boundary ──────────────────────────────────────────────────────────
_PREVIEW_BOUNDARY: Dict[str, Any] = {
    "status": "ENGINE_BRIDGE_PREVIEW_ONLY",
    "dry_run": True,
    "runtime_active": False,
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
    "kernel_mutation": False,
    "engine_mutation": False,
    "apps_mutation": False,
    "periphery_mutation": False,
    "decision_authority": "KX108_ONLY",
    "proof_claim": False,
    "world_action": False,
}

# Tokens that must never appear in a valid preview payload value
_FORBIDDEN_VALUE_TOKENS = frozenset({"ACT", "ACTIVATE", "KERNEL_WRITE", "WORLD_ACTION"})


def validate_api_preview_payload(payload: Dict[str, Any]) -> bool:
    """Validate the preview payload against boundary rules.

    Raises ValueError (FAIL_CLOSED) on any violation.
    Returns True when all checks pass.
    """
    # Decision authority
    da = payload.get("decision_authority")
    if da != "KX108_ONLY":
        raise ValueError(f"FAIL_CLOSED: decision_authority must be KX108_ONLY, got {da!r}")

    # Hard-false flags
    for flag in ("emits_act", "runtime_active", "engine_mutation", "apps_mutation",
                 "periphery_mutation", "memory_write", "kernel_mutation", "proof_claim",
                 "world_action"):
        val = payload.get(flag)
        if val is not False:
            raise ValueError(f"FAIL_CLOSED: {flag} must be False, got {val!r}")

    # Decisions must be ALLOW_CONTEXT_ONLY and HOLD (never ACT)
    ctx = payload.get("context_only_decision")
    if ctx != "ALLOW_CONTEXT_ONLY":
        raise ValueError(f"FAIL_CLOSED: context_only_decision must be ALLOW_CONTEXT_ONLY, got {ctx!r}")
    crit = payload.get("critical_action_decision")
    if crit != "HOLD":
        raise ValueError(f"FAIL_CLOSED: critical_action_decision must be HOLD, got {crit!r}")

    # Scan for forbidden tokens in string values
    import json as _json
    payload_str = _json.dumps(payload, default=str)
    for tok in _FORBIDDEN_VALUE_TOKENS:
        # Only flag as a standalone decision value, not inside compound words
        if f'"{tok}"' in payload_str:
            raise ValueError(f"FAIL_CLOSED: forbidden token {tok!r} found in payload")

    return True


def build_api_preview_payload(
    bridge_output: EngineBridgeOutput,
    context_only_result: Dict[str, Any],
    critical_action_result: Dict[str, Any],
    engine_packets_preview: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build the engine-compatible API preview payload.

    This is the payload that WOULD be returned by a future /api/runtime-wiring/preview
    endpoint — if and when the human decision is made to expose it.
    It does NOT create the endpoint. It does NOT call apps/obsidia_api.
    """
    payload: Dict[str, Any] = {
        # Boundary block (mirrors apps/obsidia_api/contracts.py SovereignBase)
        **_PREVIEW_BOUNDARY,
        # Registry summary
        "source_registry_entries": bridge_output.registry_entries_count,
        "families_sampled": bridge_output.input_family_count,
        "context_packets_count": bridge_output.context_packets_count,
        # Decisions
        "context_only_decision": bridge_output.context_only_decision,
        "critical_action_decision": bridge_output.critical_action_decision,
        # Routing provenance
        "decision_ticket_context_only": context_only_result.get("decision_ticket_id"),
        "decision_ticket_critical": critical_action_result.get("decision_ticket_id"),
        "envelope_critical": critical_action_result.get("envelope_id"),
        "evidence_context_only": context_only_result.get("evidence_id"),
        "evidence_critical": critical_action_result.get("evidence_id"),
        "verification_status": context_only_result.get("verification_status", "NOT_VERIFIED_DRY_RUN"),
        # Engine ContextPacket previews (schema-mapped, no periphery import)
        "engine_context_packets_preview": engine_packets_preview,
        # Safety block (mirrors apps/obsidia_api/routes/x108.py _BOUNDARY)
        "safety": bridge_output.safety.to_dict(),
        # Notes
        "notes": bridge_output.notes,
        # Source
        "source": "ENGINE_BRIDGE_PREVIEW",
        "pipeline": "P10B_ENGINE_BRIDGE_READONLY_ADAPTER",
    }

    validate_api_preview_payload(payload)
    return payload


def build_safe_response_preview(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Wrap a validated preview payload in a safe-response envelope.

    Mirrors the structure of apps/obsidia_api/safe_response.safe_backend_response()
    WITHOUT importing it.
    """
    validate_api_preview_payload(payload)
    return {
        "ok": True,
        "source": payload.get("source", "ENGINE_BRIDGE_PREVIEW"),
        "data": payload,
        "boundary": {
            "readonly": True,
            "emits_act": False,
            "decision_authority": "KX108_ONLY",
            "engine_mutation": False,
            "apps_mutation": False,
            "periphery_mutation": False,
        },
    }
