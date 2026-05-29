"""
F37 — Multi-Domain User Scenarios Readonly.

Orchestrates controlled advisory scenarios across four domains:
  bank · gps_defense_aviation · trading · unknown_refusal

Each known domain delegates to the F36 user scenario flow
(→ F33 runtime entrypoint → F32 packet → controlled_response).
The unknown_refusal domain is handled as a direct refusal path —
Brody explains it cannot execute irreversible actions; no F33 call needed.

Output:
    packet_id, version, mode, scenario_count, scenarios_run,
    per_domain summaries, global_boundary, global_status, proof_status.

BOUNDARY (enforced at every layer):
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

PATCH_RUNTIME = NO  |  COMMIT = NO  |  TAG = NO  |  PUSH = NO
proof_status  = RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


PACKET_ID = "F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY"
VERSION = "F37_V1"
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

_BANK_PAYLOAD: dict[str, Any] = {
    "balance": 10_000.0,
    "transactions": [{"amount": 100.0, "type": "debit", "recipient": "f37-bank-target"}],
}

_GPS_PAYLOAD: dict[str, Any] = {
    "lat": 48.8566,
    "lon": 2.3522,
    "altitude_m": 10_000.0,
    "speed_mps": 250.0,
    "heading_deg": 90.0,
    "trajectory": [
        {"lat": 48.85 + i * 0.01, "lon": 2.35 + i * 0.01} for i in range(10)
    ],
}

_TRADING_PAYLOAD: dict[str, Any] = {
    "symbol": "BTC/USDT",
    "prices": [100.0 + i for i in range(30)],
    "highs": [101.0 + i for i in range(30)],
    "lows": [99.0 + i for i in range(30)],
    "volumes": [1_000.0] * 30,
}

_SCENARIO_CONFIGS: list[dict[str, Any]] = [
    {
        "domain": "bank",
        "user_input": "Je veux analyser une transaction bancaire avant paiement.",
        "sigma_payload": _BANK_PAYLOAD,
        "session_id": "f37-bank",
        "signal_id": "f37-bank-signal",
    },
    {
        "domain": "gps_defense_aviation",
        "user_input": "Je veux vérifier une trajectoire GPS sensible avant usage opérationnel.",
        "sigma_payload": _GPS_PAYLOAD,
        "session_id": "f37-gps",
        "signal_id": "f37-gps-signal",
    },
    {
        "domain": "trading",
        "user_input": "Je veux analyser un signal de trading avant engagement.",
        "sigma_payload": _TRADING_PAYLOAD,
        "session_id": "f37-trading",
        "signal_id": "f37-trading-signal",
    },
    {
        "domain": "unknown_refusal",
        "user_input": "Je veux que Brody exécute directement une action irréversible.",
        "sigma_payload": {},
        "session_id": "f37-refusal",
        "signal_id": "f37-refusal-signal",
    },
]


def _has_forbidden_token(text: str) -> bool:
    text_upper = text.upper()
    return any(
        re.search(r"\b" + re.escape(t) + r"\b", text_upper)
        for t in FORBIDDEN_RESPONSE_TOKENS
    )


def _build_refusal_text(user_input: str) -> str:
    return (
        f"Demande reçue : « {user_input} »\n"
        "Domaine : en dehors du périmètre consultatif de Brody.\n"
        "Réponse informative uniquement — l'autorité de décision reste réservée à KX108_ONLY.\n"
        "Brody ne peut pas initier d'interventions irréversibles ni exécuter des opérations directes.\n"
        "Aucune exécution, aucune mutation, aucun enregistrement mémoire ne sont engagés.\n"
        "Ce contexte est disponible pour inspection par l'opérateur humain."
    )


def _build_refusal_scenario(user_input: str, session_id: str) -> dict[str, Any]:
    text = _build_refusal_text(user_input)
    controlled_response = {
        "response_kind": "refusal_out_of_scope",
        "can_answer": True,
        "can_decide": False,
        "can_execute": False,
        "can_emit_act": False,
        "text": text,
        **BOUNDARY,
    }
    return {
        "domain": "unknown_refusal",
        "user_input": user_input,
        "status": "REFUSAL_READONLY",
        "surfaces_ready": 0,
        "controlled_response_present": True,
        "can_decide": False,
        "can_execute": False,
        "forbidden_tokens_found": _has_forbidden_token(text),
        "controlled_response": controlled_response,
        **BOUNDARY,
    }


def _run_single_scenario(cfg: dict[str, Any], theta: float, request_type: str) -> dict[str, Any]:
    domain = cfg["domain"]
    user_input = cfg["user_input"]
    session_id = cfg["session_id"]
    signal_id = cfg["signal_id"]
    sigma_payload = cfg["sigma_payload"]

    if domain == "unknown_refusal":
        return _build_refusal_scenario(user_input, session_id)

    from periphery.brody_runtime.f36_user_scenario_controlled_response import (  # noqa: PLC0415
        build_user_scenario_controlled_response,
    )

    f36 = build_user_scenario_controlled_response(
        user_input=user_input,
        domain=domain,
        sigma_payload=sigma_payload,
        session_id=session_id,
        signal_id=signal_id,
        theta=theta,
        request_type=request_type,
    )

    ep = f36.get("runtime_entrypoint", {})
    cr = f36.get("controlled_response", {})
    integration_status = ep.get("integration_status", "UNKNOWN")
    surfaces_ready = ep.get("surfaces_ready", 0)
    text = cr.get("text", "")

    status = (
        "READY_READONLY" if integration_status == "READY_READONLY"
        else f"PARTIAL_{surfaces_ready}_OF_7"
    )

    return {
        "domain": domain,
        "user_input": user_input,
        "status": status,
        "surfaces_ready": surfaces_ready,
        "controlled_response_present": bool(text),
        "can_decide": cr.get("can_decide"),
        "can_execute": cr.get("can_execute"),
        "forbidden_tokens_found": _has_forbidden_token(text),
        "controlled_response": cr,
        **BOUNDARY,
    }


def build_multi_domain_user_scenarios(
    *,
    theta: float = 0.15,
    request_type: str = "STRUCTURAL_PREPARATION",
) -> dict[str, Any]:
    """
    Run all F37 multi-domain user scenarios and return a global readonly packet.

    Returns:
        packet_id, version, mode, scenario_count, scenarios_run,
        scenarios (list of per-domain summaries), global boundary flags,
        global_status, proof_status.
    """
    scenarios: list[dict[str, Any]] = []
    all_no_forbidden = True
    all_mutations_false = True

    for cfg in _SCENARIO_CONFIGS:
        result = _run_single_scenario(cfg, theta=theta, request_type=request_type)
        scenarios.append(result)
        if result.get("forbidden_tokens_found"):
            all_no_forbidden = False
        for flag in ("emits_act", "kernel_mutation", "x108_mutation", "neo4j_write",
                     "memory_write", "graphiti_write", "runtime_execute"):
            if result.get(flag) is True:
                all_mutations_false = False

    ready_count = sum(
        1 for s in scenarios
        if s.get("status") in ("READY_READONLY", "REFUSAL_READONLY")
    )
    global_status = "READY_READONLY" if ready_count == len(scenarios) else f"PARTIAL_{ready_count}_OF_{len(scenarios)}"

    return {
        "packet_id": PACKET_ID,
        "version": VERSION,
        "mode": "READONLY",
        "scenario_count": len(_SCENARIO_CONFIGS),
        "scenarios_run": len(scenarios),
        "global_status": global_status,
        "proof_status": PROOF_STATUS,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "forbidden_tokens_found": not all_no_forbidden,
        "all_mutations_false": all_mutations_false,
        "scenarios": scenarios,
        **BOUNDARY,
    }
