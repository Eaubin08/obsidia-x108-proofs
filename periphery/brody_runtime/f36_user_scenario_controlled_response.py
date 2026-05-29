"""
F36 — User Scenario: Brody Workbench Controlled Response.

End-to-end user scenario that calls the F33 runtime entrypoint, builds a
workbench surface summary from the F32 packet, and returns a controlled
readonly response for the user. Proves Brody can consult runtime/workbench
surfaces without deciding.

Flow:
    user_input
    → F33 runtime entrypoint (7 surfaces)
    → workbench summary (from F32 packet)
    → controlled_response (text, no forbidden tokens)
    → scenario envelope

BOUNDARY (enforced everywhere):
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

Forbidden response tokens: ALLOW · HOLD · BLOCK · ACT · DECIDE · VERDICT
Allowed:  autorité réservée · contexte disponible · surfaces consultées
          réponse informative · aucune exécution · aucune mutation

PATCH_RUNTIME = NO  |  COMMIT = NO  |  TAG = NO  |  PUSH = NO
proof_status  = RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


SCENARIO_ID = "F36_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE"
VERSION = "F36_V1"
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

FORBIDDEN_RESPONSE_TOKENS = ("ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT")

_DEFAULT_USER_INPUT = "Je veux analyser une transaction bancaire avant paiement."
_DEFAULT_SIGMA_PAYLOAD: dict[str, Any] = {
    "balance": 10_000.0,
    "transactions": [{"amount": 100.0, "type": "debit", "recipient": "readonly-scenario-target"}],
    "request_type": "STRUCTURAL_PREPARATION",
}


def _build_controlled_response_text(
    user_input: str,
    domain: str,
    surface_names: list[str],
    surfaces_ready: int,
) -> str:
    from apps.obsidia_api.safe_response import sanitize_user_facing_text  # noqa: PLC0415
    safe_input = sanitize_user_facing_text(user_input)
    surfaces_list = ", ".join(surface_names)
    return (
        f"Demande reçue : « {safe_input} »\n"
        f"Domaine consulté : {domain}.\n"
        f"Contexte disponible : {surfaces_ready} surfaces runtime opérationnelles "
        f"({surfaces_list}).\n"
        "Réponse informative uniquement — l'autorité de décision reste réservée à KX108_ONLY.\n"
        "Aucune exécution, aucune mutation, aucun enregistrement mémoire ne sont engagés.\n"
        "Ce contexte est disponible pour inspection par l'opérateur humain avant toute intervention réelle."
    )


def build_user_scenario_controlled_response(
    *,
    user_input: str = _DEFAULT_USER_INPUT,
    domain: str = "bank",
    sigma_payload: dict[str, Any] | None = None,
    sop_text: str = (
        "1. Recevoir la demande utilisateur en lecture seule\n"
        "2. Consulter les surfaces runtime disponibles\n"
        "3. Préparer une réponse informative et encadrée\n"
        "4. Réserver toute décision finale à KX108_ONLY"
    ),
    title: str = "F36 user scenario controlled response",
    session_id: str = "f36-user-scenario",
    signal_id: str = "f36-tree-signal",
    activations: list[float] | None = None,
    theta: float = 0.15,
    request_type: str = "STRUCTURAL_PREPARATION",
) -> dict[str, Any]:
    """
    Build a controlled user scenario response by consulting F33 runtime entrypoint.

    Returns a scenario envelope with:
        scenario_id, version, mode, user_input, scenario_at,
        runtime_entrypoint (summary from F33/F32),
        workbench (summary built from F32 packet surfaces),
        controlled_response (text + can_decide=False + can_execute=False),
        proof_status, and the full BOUNDARY block.

    Never emits ACT, never mutates anything, never stores anything.
    The controlled_response.text contains no forbidden tokens.
    """
    sp = sigma_payload if sigma_payload is not None else _DEFAULT_SIGMA_PAYLOAD

    from periphery.brody_runtime.f33_runtime_entrypoint_readonly import (  # noqa: PLC0415
        call_brody_runtime_entrypoint,
    )

    f33_result = call_brody_runtime_entrypoint(
        domain=domain,
        sigma_payload=sp,
        sop_text=sop_text,
        title=title,
        session_id=session_id,
        signal_id=signal_id,
        activations=activations,
        theta=theta,
        request_type=request_type,
    )

    f32_packet = f33_result.get("f32_packet", {})
    surfaces = f32_packet.get("surfaces", {})
    surface_names = sorted(surfaces.keys())
    surfaces_ready = f33_result.get("surfaces_ready", 0)
    integration_status = f33_result.get("integration_status", "UNKNOWN")

    runtime_entrypoint = {
        "entrypoint_id": f33_result.get("entrypoint_id"),
        "version": f33_result.get("version"),
        "integration_status": integration_status,
        "entrypoint_status": f33_result.get("entrypoint_status"),
        "surfaces_ready": surfaces_ready,
        "surfaces_missing": f33_result.get("surfaces_missing", 0),
        "surfaces_total": f33_result.get("surfaces_total", 0),
        "proof_status": f33_result.get("proof_status"),
    }

    workbench = {
        "surface_id": "F36_WORKBENCH_SUMMARY",
        "surface_kind": "scenario_workbench_summary",
        "connector_status": (
            "READY_READONLY"
            if integration_status == "READY_READONLY"
            else f"PARTIAL_{surfaces_ready}_OF_7"
        ),
        "surfaces_consulted": surface_names,
        "surfaces_ready": surfaces_ready,
        "integration_status": integration_status,
        "f35_c03_available": True,
        **BOUNDARY,
    }

    text = _build_controlled_response_text(
        user_input=user_input,
        domain=domain,
        surface_names=surface_names,
        surfaces_ready=surfaces_ready,
    )

    controlled_response = {
        "response_kind": "contextual_explanation_only",
        "can_answer": True,
        "can_decide": False,
        "can_execute": False,
        "can_emit_act": False,
        "text": text,
        **BOUNDARY,
    }

    return {
        "scenario_id": SCENARIO_ID,
        "version": VERSION,
        "mode": "READONLY",
        "user_input": user_input,
        "domain": domain,
        "scenario_at": datetime.now(timezone.utc).isoformat(),
        "proof_status": PROOF_STATUS,
        "runtime_entrypoint": runtime_entrypoint,
        "workbench": workbench,
        "controlled_response": controlled_response,
        **BOUNDARY,
    }
