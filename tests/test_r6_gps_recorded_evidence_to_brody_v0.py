import copy
import json
from pathlib import Path

import pytest

from periphery.cognition.gps_defense_recorded_evidence_v0 import (
    build_recorded_gps_sigma_envelope_v0,
)


ROOT = Path(__file__).resolve().parents[1]
CTTC = ROOT / "artifacts" / "gps_iq_cttc_2013_04_04_recorded_real_rf_result.json"


def _artifact():
    return json.loads(CTTC.read_text(encoding="utf-8"))


def test_cttc_recorded_real_rf_builds_readonly_brody_sigma_envelope():
    envelope = build_recorded_gps_sigma_envelope_v0(_artifact())

    assert envelope["domain"] == "gps_defense_aviation"
    assert envelope["proof_status"] == "RECORDED_REAL_RF"
    assert envelope["synthetic"] is False
    assert envelope["physical_claim_eligible"] is True

    assert envelope["x108_gate"] == "HOLD"
    assert envelope["market_verdict"] == "RECALC_TRAJECTORY"
    assert envelope["reason_code"] == "UNKNOWNS_OR_CONFIDENCE_LOW"
    assert "INERTIAL_MISSING" in envelope["unknowns"]

    assert envelope["readonly"] is True
    assert envelope["advisory_only"] is True
    assert envelope["allowed_to_decide"] is False
    assert envelope["allowed_to_act"] is False
    assert envelope["emits_act"] is False
    assert envelope["emits_verdict"] is False
    assert envelope["memory_write"] is False
    assert envelope["kernel_mutation"] is False
    assert envelope["x108_mutation"] is False
    assert envelope["decision_authority"] == "KX108_ONLY"
    assert envelope["recorded_x108_gate_is_evidence_not_brody_authority"] is True
    assert len(envelope["evidence_artifact_sha256"]) == 64


def test_recorded_evidence_bridge_rejects_tampered_kernel_response():
    artifact = _artifact()
    artifact["kernel_http_evidence"]["raw_response"] += " "

    with pytest.raises(
        ValueError,
        match="GPS_KERNEL_RAW_RESPONSE_SHA256_MISMATCH",
    ):
        build_recorded_gps_sigma_envelope_v0(artifact)


def test_recorded_evidence_bridge_rejects_synthetic_physical_claim():
    artifact = _artifact()
    artifact["observation_envelope"]["synthetic"] = True

    with pytest.raises(
        ValueError,
        match="GPS_RECORDED_EVIDENCE_SYNTHETIC_FORBIDDEN",
    ):
        build_recorded_gps_sigma_envelope_v0(artifact)


def test_recorded_evidence_bridge_rejects_wrong_kernel_domain():
    artifact = _artifact()
    raw = json.loads(artifact["kernel_http_evidence"]["raw_response"])
    raw["domain"] = "bank"
    tampered = json.dumps(raw, separators=(",", ":"))
    artifact["kernel_http_evidence"]["raw_response"] = tampered

    import hashlib
    artifact["kernel_http_evidence"]["raw_response_sha256"] = hashlib.sha256(
        tampered.encode("utf-8")
    ).hexdigest()

    with pytest.raises(
        ValueError,
        match="GPS_KERNEL_DOMAIN_MISMATCH",
    ):
        build_recorded_gps_sigma_envelope_v0(artifact)


def test_recorded_evidence_bridge_rejects_bad_authority():
    artifact = _artifact()
    artifact["kernel_http_evidence"]["payload"]["meta"][
        "decision_authority"
    ] = "BRODY"

    with pytest.raises(
        ValueError,
        match="GPS_KERNEL_AUTHORITY_NOT_KX108_ONLY",
    ):
        build_recorded_gps_sigma_envelope_v0(artifact)
