import json
from pathlib import Path

from periphery.demo.real_e2e_v0 import (
    recorded_evidence_from_real_artifact_v0,
    run_recorded_real_e2e_demo_v0,
)


ROOT = Path(__file__).resolve().parents[2]
RINEX = ROOT / "artifacts" / "gps_rinex_noaa_ab02_2026_210_real_result.json"
RF = ROOT / "artifacts" / "gps_iq_cttc_2013_04_04_recorded_real_rf_result.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_real_rinex_artifact_replays_through_canonical_closure():
    artifact = _load(RINEX)
    result = run_recorded_real_e2e_demo_v0(
        artifact,
        demo_id="demo:rinex",
        source_artifact_ref="artifacts/gps_rinex_noaa_ab02_2026_210_real_result.json",
    )
    assert result.proof_level == "RECORDED_REAL_GNSS"
    assert result.closure.recorded_real is True
    assert result.closure.live_claim_closed is False
    assert result.closure.physical_authenticity_proven is False
    assert result.fail_closed is True
    assert result.domain_state_name == "GPS_DEFENSE_AVIATION_UNTRUSTED"
    assert "CIC_ATTESTATION_FAILED" in result.reality_authenticity_reasons
    assert "MULTI_SOURCE_COHERENCE_FAILED" in result.reality_authenticity_reasons
    assert result.live_execution_performed is False


def test_real_rf_artifact_replays_through_canonical_closure():
    artifact = _load(RF)
    result = run_recorded_real_e2e_demo_v0(
        artifact,
        demo_id="demo:rf",
        source_artifact_ref="artifacts/gps_iq_cttc_2013_04_04_recorded_real_rf_result.json",
    )
    assert result.proof_level == "RECORDED_REAL_RF"
    assert result.closure.recorded_real is True
    assert result.closure.claim_scope == "RECORDED_REAL_RF"
    assert result.closure.live_claim_closed is False
    assert result.fail_closed is True
    assert "CIC_ATTESTATION_FAILED" in result.reality_authenticity_reasons
    assert "MULTI_SOURCE_COHERENCE_FAILED" in result.reality_authenticity_reasons


def test_replay_normalization_corrects_historical_attestation_overclaim():
    artifact = _load(RINEX)
    assert artifact["domain_payload"]["attestation_ready"] is True
    evidence = recorded_evidence_from_real_artifact_v0(
        artifact,
        source_artifact_ref="artifacts/gps_rinex_noaa_ab02_2026_210_real_result.json",
    )
    result = run_recorded_real_e2e_demo_v0(
        artifact,
        demo_id="demo:rinex-boundary",
        source_artifact_ref="artifacts/gps_rinex_noaa_ab02_2026_210_real_result.json",
    )
    # Historical artifact provenance stays intact, but F22 canonical replay
    # never treats recorded-file eligibility as live sensor attestation.
    assert evidence.physical_authenticity_proven is False
    assert "LIVE_SENSOR_ATTESTATION_NOT_PROVEN" in evidence.uncertainty
    assert "CIC_ATTESTATION_FAILED" in result.reality_authenticity_reasons


def test_non_recorded_artifact_is_rejected():
    artifact = _load(RINEX)
    artifact["observation_envelope"]["proof_level"] = "STRUCTURED_STATE"
    try:
        recorded_evidence_from_real_artifact_v0(
            artifact,
            source_artifact_ref="artifact:bad",
        )
    except ValueError as exc:
        assert "only recorded-real GNSS/RF artifacts" in str(exc)
    else:
        raise AssertionError("non-recorded-real artifact must fail closed")


def test_replay_is_readonly_and_non_sovereign():
    result = run_recorded_real_e2e_demo_v0(
        _load(RF),
        demo_id="demo:authority",
        source_artifact_ref="artifacts/gps_iq_cttc_2013_04_04_recorded_real_rf_result.json",
    )
    assert result.readonly is True
    assert result.decision_authority == "KX108_ONLY"
    assert result.allowed_to_decide is False
    assert result.allowed_to_act is False
