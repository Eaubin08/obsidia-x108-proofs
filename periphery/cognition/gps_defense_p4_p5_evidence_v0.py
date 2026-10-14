"""P4/P5 recorded GNSS evidence -> readonly Brody/Sigma envelope.

This module combines two already-bounded evidence products:
- frozen P4 temporal-integrity development evidence;
- deterministic P5 observational-support assessment.

It does not classify spoofing, does not consume a hostile label for the P4
decision, and never grants Brody decision authority.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from domains.gps.gps_x108_gate import GpsX108Gate


def _sha256_obj(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def _p4_gate_payload(p4_freeze: dict[str, Any]) -> dict[str, Any]:
    dev = p4_freeze["development_result"]
    return {
        "flow_type": "POSITION_REPORT",
        "flight_id": "FGI-P4-P5-RECORDED-EVIDENCE",
        "risk_score": 0.5,
        "confidence_index": 0.9,
        "audit_score": 1.0,
        "freshness_ms": 0,
        "attestation_ready": True,
        "sensor_attested": True,
        "replay_window_detected": False,
        "gps_available": True,
        "inertial_available": True,
        "radio_available": True,
        "trajectory_drift_score": 0.0,
        "source_conflict_score": 0.0,
        "time_skew_score": 0.0,
        "brownout_score": 0.0,
        "ground_speed": 0.0,
        "g_load": 1.0,
        "rollback_possible": True,
        "temporal_integrity_classification": dev["classification"],
        "temporal_integrity_evidence_hash": dev["domain_evidence_sha256"],
        "temporal_integrity_algorithm_version": p4_freeze["algorithm_version"],
        "temporal_integrity_status": p4_freeze["development_status"],
    }


def build_p4_p5_brody_sigma_envelope_v0(
    *,
    p4_freeze: dict[str, Any],
    p5_assessment: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(p4_freeze, dict):
        raise TypeError("P4_FREEZE_OBJECT_REQUIRED")
    if not isinstance(p5_assessment, dict):
        raise TypeError("P5_ASSESSMENT_OBJECT_REQUIRED")

    if p4_freeze.get("artifact") != "p4_temporal_classifier_freeze_v0":
        raise ValueError("P4_FREEZE_ARTIFACT_MISMATCH")
    if (
        p4_freeze.get("status")
        != "FROZEN_DEVELOPMENT_CLASSIFIER_AWAITING_BLIND_VALIDATION"
    ):
        raise ValueError("P4_CLASSIFIER_NOT_FROZEN")
    if p4_freeze.get("algorithm_version") != "P4_TEMPORAL_DISCONTINUITY_V0":
        raise ValueError("P4_ALGORITHM_VERSION_MISMATCH")
    if p4_freeze.get("decision_authority") != "KX108_ONLY":
        raise ValueError("P4_AUTHORITY_NOT_KX108_ONLY")
    if p4_freeze.get("emits_verdict") is not False:
        raise ValueError("P4_VERDICT_EMISSION_FORBIDDEN")
    if p4_freeze.get("blind_validation_required") is not True:
        raise ValueError("P4_BLIND_VALIDATION_BOUNDARY_MISSING")
    if p4_freeze.get("thresholds_may_change_before_blind_validation") is not False:
        raise ValueError("P4_FROZEN_THRESHOLD_BOUNDARY_VIOLATED")

    claim_boundary = str(p4_freeze.get("claim_boundary") or "")
    if claim_boundary != "TRAJECTORY_DISCONTINUITY_ONLY_NO_HOSTILE_OR_CAUSAL_ATTRIBUTION":
        raise ValueError("P4_CLAIM_BOUNDARY_MISMATCH")

    dev = p4_freeze.get("development_result")
    if not isinstance(dev, dict):
        raise ValueError("P4_DEVELOPMENT_RESULT_MISSING")
    if dev.get("classification") != "ANOMALY":
        raise ValueError("P4_EXPECTED_ANOMALY_MISSING")
    if dev.get("truth_or_onset_consumed") is not False:
        raise ValueError("P4_TRUTH_OR_ONSET_LEAK")
    if int(dev.get("violation_count") or 0) < 2:
        raise ValueError("P4_ANOMALY_RULE_NOT_SATISFIED")
    evidence_sha = str(dev.get("domain_evidence_sha256") or "")
    if len(evidence_sha) != 64:
        raise ValueError("P4_DOMAIN_EVIDENCE_SHA256_MISSING")

    if p5_assessment.get("artifact") != "gps_p5_causal_support_assessment":
        raise ValueError("P5_ASSESSMENT_ARTIFACT_MISMATCH")
    if p5_assessment.get("decision_authority") != "KX108_ONLY":
        raise ValueError("P5_AUTHORITY_NOT_KX108_ONLY")
    if p5_assessment.get("emits_verdict") is not False:
        raise ValueError("P5_VERDICT_EMISSION_FORBIDDEN")
    if (
        p5_assessment.get("support_level")
        != "STRONG_OBSERVATIONAL_SUPPORT_NOT_CAUSAL"
    ):
        raise ValueError("P5_SUPPORT_LEVEL_NOT_STRONG_OBSERVATIONAL")
    if p5_assessment.get("causal_attribution_closed") is not False:
        raise ValueError("P5_CAUSAL_ATTRIBUTION_MUST_REMAIN_OPEN")

    required_blockers = {
        "NO_INDEPENDENT_PHYSICAL_SOURCE_CORROBORATION",
        "NO_CONTROLLED_INTERVENTION",
        "NO_HELDOUT_HOSTILE_VALIDATION",
    }
    blockers = {
        str(item)
        for item in (p5_assessment.get("blockers") or [])
    }
    if not required_blockers.issubset(blockers):
        raise ValueError("P5_REQUIRED_CAUSAL_BLOCKERS_MISSING")

    forbidden_claims = {
        str(item)
        for item in (p5_assessment.get("forbidden_claims") or [])
    }
    if "SPOOFING_CAUSED_THE_OBSERVED_DISPLACEMENT" not in forbidden_claims:
        raise ValueError("P5_SPOOFING_CAUSAL_CLAIM_BOUNDARY_MISSING")

    gate_result = GpsX108Gate().evaluate(_p4_gate_payload(p4_freeze))
    state = (
        gate_result.get("ir_payload", {})
        .get("meta", {})
        .get("domain_state", {})
    )
    reasons = (
        state.get("reality_authenticity", {}).get("reasons", [])
        if isinstance(state, dict)
        else []
    )
    nuisances = state.get("nuisances", []) if isinstance(state, dict) else []

    if gate_result.get("verdict") != "HOLD":
        raise ValueError("P4_GATE_DID_NOT_HOLD")
    if gate_result.get("source") != "REALITY_AUTHENTICITY_GATE_FAIL_CLOSED":
        raise ValueError("P4_GATE_SOURCE_MISMATCH")
    if "TEMPORAL_INTEGRITY_ANOMALY" not in reasons:
        raise ValueError("P4_TEMPORAL_REASON_NOT_PRESERVED")
    if "GPS_SPOOFING" in nuisances:
        raise ValueError("P4_ANOMALY_WAS_PROMOTED_TO_SPOOFING")
    if gate_result.get("receipt", {}).get("connector_decides") is not False:
        raise ValueError("P4_CONNECTOR_DECISION_AUTHORITY_VIOLATION")

    p4_hash = _sha256_obj(p4_freeze)
    p5_hash = _sha256_obj(p5_assessment)
    receipt = gate_result.get("receipt") or {}
    os3 = receipt.get("os3_ticket") or {}

    return {
        "source": "GPS_P4_P5_RECORDED_EVIDENCE_TO_BRODY_V0",
        "mode": "READONLY_DOMAIN_SIGMA_ENVELOPE",
        "domain_sigma_envelope": True,
        "domain": "gps_defense_aviation",
        "proof_status": "RECORDED_REAL_RF_DERIVED_EVIDENCE",
        "p4_classifier_status": p4_freeze.get("status"),
        "p4_development_status": p4_freeze.get("development_status"),
        "p4_algorithm_version": p4_freeze.get("algorithm_version"),
        "p4_freeze_sha256": p4_hash,
        "p4_domain_evidence_sha256": evidence_sha,
        "p4_classification": dev.get("classification"),
        "p4_first_anomaly_transition": dev.get("first_anomaly_transition"),
        "p4_ecef_step_m": dev.get("ecef_step_m"),
        "p4_clock_residual_s": dev.get("clock_residual_s"),
        "p4_receiver_gap_s": dev.get("receiver_gap_s"),
        "p4_violation_count": dev.get("violation_count"),
        "p4_truth_or_onset_consumed": dev.get("truth_or_onset_consumed"),
        "p4_claim_boundary": claim_boundary,
        "blind_validation_required": True,
        "p5_assessment_sha256": p5_hash,
        "p5_support_level": p5_assessment.get("support_level"),
        "causal_attribution_closed": False,
        "p5_allowed_claim": p5_assessment.get("allowed_claim"),
        "forbidden_claims": sorted(forbidden_claims),
        "x108_gate": "HOLD",
        "gate_source": gate_result.get("source"),
        "gate_reason_codes": list(reasons),
        "recorded_gate_ticket_id": os3.get("ticket_id"),
        "recorded_gate_state_hash": state.get("domain_state_hash"),
        "contradictions": [],
        "unknowns": sorted(blockers),
        "risk_flags": ["TEMPORAL_INTEGRITY_ANOMALY"],
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
