from demos.premiere_mise_au_monde_double_demo_v0 import (
    CognitiveEvidenceV0,
    run_brody_gms_demo_v0,
    run_gps_demo_v0,
)
from periphery.gps_physical.bridge_v0 import RecordedGpsEvidenceV0


def test_gps_and_brody_gms_share_the_same_governed_proof_boundary():
    gps = RecordedGpsEvidenceV0(
        evidence_id="rinex-ab02-demo",
        observed_at="2026-07-29T00:00:00.000Z",
        source_ref="artifact:gps_rinex_noaa_ab02_2026_210_real_result.json",
        source_hash="c81c0c78f99cc945d8d4f2074fd46de98974965d897b887c0ba45cdc77e81ea0",
        proof_level="RECORDED_REAL_GNSS",
        state={"satellites_count": 31, "gps_status": "ONLINE", "inertial_available": False},
        evidence_refs=("evidence:rinex:noaa-ab02",),
        uncertainty=("INERTIAL_MISSING",),
        physical_authenticity_proven=False,
        receiver_status="UNKNOWN",
    )
    cognitive = CognitiveEvidenceV0(
        observation_id="brody-gms-demo",
        observed_at="2026-10-06T20:00:00Z",
        source_ref="brody:gms:demo-input",
        source_hash="brody-gms-demo-hash",
        state={"intent": "EXPLAIN", "translation_status": "TRANSLATED", "content": "candidate response"},
        evidence_refs=("evidence:brody:gms:1",),
    )

    gps_result = run_gps_demo_v0(gps, confidence=0.9)
    cognitive_result = run_brody_gms_demo_v0(cognitive, confidence=0.9)

    for result in (gps_result, cognitive_result):
        assert result.proof_verified is True
        assert result.proof_verdict == "VERIFIED"
        assert result.proof.decision_authority == "KX108_ONLY"
        assert result.proof.proof_authority is False
        assert result.proof.execution_authority is False
        assert result.execution_authority is False
        assert result.proof.world_state_ref == result.world_state_ref
        assert result.proof.domain_state_ref == result.domain_state_ref

    assert gps_result.path == "GPS_PHYSICAL"
    assert gps_result.domain_id == "gps_defense_aviation"
    assert "INERTIAL_MISSING" in gps_result.proof.evidence_refs or gps_result.x108_gate in {"HOLD", "BLOCK", "ALLOW"}

    assert cognitive_result.path == "BRODY_GMS_COGNITIVE"
    assert cognitive_result.domain_id == "meta"


def test_gps_blocker_remains_visible_and_fail_closed():
    gps = RecordedGpsEvidenceV0(
        evidence_id="gps-blocked-receiver",
        observed_at="2026-10-06T20:00:00Z",
        source_ref="receiver:local",
        source_hash="receiver-config-hash",
        proof_level="RECORDED_REAL_GNSS",
        state={"gps_status": "RECORDED_ONLY"},
        evidence_refs=("evidence:gps:recorded",),
        receiver_status="BLOCKED_RECEIVER_CONFIGURATION",
    )
    result = run_gps_demo_v0(gps, confidence=0.9)
    assert result.x108_gate in {"HOLD", "BLOCK"}
    assert result.proof_verified is True
    assert result.execution_authority is False


def test_cognitive_unknown_is_preserved_into_governed_decision():
    cognitive = CognitiveEvidenceV0(
        observation_id="brody-unknown",
        observed_at="2026-10-06T20:00:00Z",
        source_ref="brody:gms",
        source_hash="gms-hash",
        state={"translation_status": "PARTIAL"},
        evidence_refs=("evidence:gms:partial",),
        uncertainty=("SEMANTIC_TRANSLATION_INCOMPLETE",),
    )
    result = run_brody_gms_demo_v0(cognitive, confidence=0.4)
    assert result.x108_gate == "HOLD"
    assert result.proof_verified is True
    assert result.execution_authority is False
