"""GPS/Defense recorded-RF evidence -> readonly Brody/Sigma envelope V0.

Consumes an already-produced physical GPS artifact. It never reclassifies RF,
never invents a gate, and never promotes a domain decision into Brody authority.
The observed X108 gate is extracted from the recorded kernel response.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


_ALLOWED_PROOF_LEVELS = {
    "RECORDED_REAL_GNSS",
    "RECORDED_REAL_RF",
    "RECORDED_RF_ATTACK",
    "REAL_PASSIVE_GNSS",
    "HARDWARE_IN_THE_LOOP",
}


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_obj(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def build_recorded_gps_sigma_envelope_v0(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise TypeError("GPS_RECORDED_ARTIFACT_REQUIRED")

    observation = artifact.get("observation_envelope")
    kernel = artifact.get("kernel_http_evidence")
    if not isinstance(observation, dict):
        raise ValueError("GPS_OBSERVATION_ENVELOPE_MISSING")
    if not isinstance(kernel, dict):
        raise ValueError("GPS_KERNEL_HTTP_EVIDENCE_MISSING")

    if observation.get("synthetic") is True:
        raise ValueError("GPS_RECORDED_EVIDENCE_SYNTHETIC_FORBIDDEN")

    proof_level = str(observation.get("proof_level") or "")
    if proof_level not in _ALLOWED_PROOF_LEVELS:
        raise ValueError(
            "GPS_RECORDED_EVIDENCE_PROOF_LEVEL_UNSUPPORTED:"
            + proof_level
        )

    if observation.get("eligible_for_physical_claim") is not True:
        raise ValueError("GPS_PHYSICAL_CLAIM_NOT_ELIGIBLE")

    raw_response = kernel.get("raw_response")
    raw_response_sha256 = str(kernel.get("raw_response_sha256") or "")
    if not isinstance(raw_response, str) or not raw_response.strip():
        raise ValueError("GPS_KERNEL_RAW_RESPONSE_MISSING")
    if len(raw_response_sha256) != 64:
        raise ValueError("GPS_KERNEL_RAW_RESPONSE_SHA256_MISSING")
    if _sha256_text(raw_response) != raw_response_sha256:
        raise ValueError("GPS_KERNEL_RAW_RESPONSE_SHA256_MISMATCH")

    try:
        decision = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError("GPS_KERNEL_RAW_RESPONSE_INVALID_JSON") from exc

    if not isinstance(decision, dict):
        raise ValueError("GPS_KERNEL_DECISION_NOT_OBJECT")

    domain = str(decision.get("domain") or "")
    if domain != "gps_defense_aviation":
        raise ValueError(
            "GPS_KERNEL_DOMAIN_MISMATCH:" + (domain or "NONE")
        )

    payload = kernel.get("payload")
    meta = (
        payload.get("meta")
        if isinstance(payload, dict)
        and isinstance(payload.get("meta"), dict)
        else {}
    )
    if meta.get("decision_authority") != "KX108_ONLY":
        raise ValueError("GPS_KERNEL_AUTHORITY_NOT_KX108_ONLY")
    if meta.get("decides_alone") is not False:
        raise ValueError("GPS_DOMAIN_CONNECTOR_SOVEREIGN_FORBIDDEN")

    x108_gate = str(decision.get("x108_gate") or "").upper()
    if x108_gate not in {"HOLD", "BLOCK", "ALLOW"}:
        raise ValueError("GPS_KERNEL_X108_GATE_INVALID:" + x108_gate)

    contradictions = decision.get("contradictions") or []
    unknowns = decision.get("unknowns") or []
    risk_flags = decision.get("risk_flags") or []
    for name, value in (
        ("contradictions", contradictions),
        ("unknowns", unknowns),
        ("risk_flags", risk_flags),
    ):
        if not isinstance(value, list):
            raise ValueError(f"GPS_KERNEL_{name.upper()}_NOT_LIST")

    artifact_hash = _sha256_obj(artifact)

    return {
        "source": "GPS_RECORDED_PHYSICAL_EVIDENCE_TO_BRODY_V0",
        "mode": "READONLY_DOMAIN_SIGMA_ENVELOPE",
        "domain_sigma_envelope": True,
        "domain": "gps_defense_aviation",
        "proof_status": proof_level,
        "evidence_artifact_sha256": artifact_hash,
        "observation_id": observation.get("observation_id"),
        "observation_input_hash": observation.get("input_hash"),
        "synthetic": False,
        "physical_claim_eligible": True,
        "recorded_kernel_status_http": kernel.get("status_http"),
        "recorded_kernel_raw_response_sha256": raw_response_sha256,
        "recorded_decision_id": decision.get("decision_id"),
        "recorded_trace_id": decision.get("trace_id"),
        "market_verdict": decision.get("market_verdict"),
        "x108_gate": x108_gate,
        "reason_code": decision.get("reason_code"),
        "severity": decision.get("severity"),
        "confidence_integrity": decision.get("confidence_integrity"),
        "confidence_governance": decision.get("confidence_governance"),
        "confidence_readiness": decision.get("confidence_readiness"),
        "contradictions": list(contradictions),
        "unknowns": list(unknowns),
        "risk_flags": list(risk_flags),
        "evidence_refs": list(decision.get("evidence_refs") or []),
        "readonly": True,
        "advisory_only": True,
        "context_signal_only": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "decision_authority": "KX108_ONLY",
        "recorded_x108_gate_is_evidence_not_brody_authority": True,
    }
