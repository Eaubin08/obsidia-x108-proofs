from periphery.cross_modal.contracts_v0 import build_cross_modal_coherence_report_v0
from periphery.gps_physical.bridge_v0 import RecordedGpsEvidenceV0
from periphery.gps_physical.closure_v0 import (
    build_gps_domain_gate_state_v0,
    build_gps_physical_world_closure_v0,
    gps_closure_to_gate_payload_v0,
)
from periphery.multimodal.bridge_v0 import ModalityObservationV0


def _recorded(proof_level: str = "RECORDED_REAL_GNSS", receiver_status: str = "UNKNOWN"):
    return RecordedGpsEvidenceV0(
        evidence_id="gps:e1",
        observed_at="2026-07-29T00:00:00Z",
        source_ref="source:noaa-rinex",
        source_hash="sha256:rinex",
        proof_level=proof_level,
        state={
            "satellites_count": 31,
            "signal_noise_ratio": 0.9,
            "inertial_available": False,
            "radio_available": True,
            "trajectory_drift_score": 0.0,
            "source_conflict_score": 0.0,
            "freshness_ms": 0.0,
        },
        evidence_refs=("artifact:gps-rinex-real",),
        receiver_status=receiver_status,
    )


def test_recorded_real_gnss_closure_preserves_claim_scope_without_live_promotion():
    evidence = _recorded("RECORDED_REAL_GNSS")
    closure = build_gps_physical_world_closure_v0(evidence)

    assert closure.recorded_real is True
    assert closure.claim_scope == "RECORDED_REAL_GNSS"
    assert closure.live_claim_closed is False
    assert closure.attack_claim_closed is False
    assert closure.physical_authenticity_proven is False
    assert "LIVE_SENSOR_ATTESTATION_NOT_PROVEN" in closure.blockers
    assert "MULTI_SOURCE_CORROBORATION_NOT_PROVEN" in closure.blockers


def test_receiver_configuration_blocker_survives_closure():
    closure = build_gps_physical_world_closure_v0(
        _recorded(receiver_status="BLOCKED_RECEIVER_CONFIGURATION")
    )
    assert "RECEIVER_CONFIGURATION_BLOCKED" in closure.blockers


def test_cross_modal_report_does_not_self_close_physical_authenticity():
    image = ModalityObservationV0(
        observation_id="img:1",
        modality="image",
        observed_at="2026-07-29T00:00:00Z",
        source_ref="camera:1",
        source_hash="hash:image",
        state={"unit": "m"},
        frame_ref="ECEF",
    )
    gps = ModalityObservationV0(
        observation_id="gps:1",
        modality="gnss",
        observed_at="2026-07-29T00:00:00Z",
        source_ref="receiver:1",
        source_hash="hash:gps",
        state={"unit": "m"},
        frame_ref="ECEF",
    )
    report = build_cross_modal_coherence_report_v0(
        report_id="cross:1",
        observations=(image, gps),
    )
    closure = build_gps_physical_world_closure_v0(_recorded(), cross_modal_report=report)

    assert closure.cross_modal_report_ref == "cross:1"
    assert "MULTI_SOURCE_CORROBORATION_NOT_PROVEN" in closure.blockers
    assert closure.physical_authenticity_proven is False


def test_recorded_payload_never_fakes_live_attestation():
    evidence = _recorded()
    closure = build_gps_physical_world_closure_v0(evidence)
    payload = gps_closure_to_gate_payload_v0(evidence, closure)

    assert payload["sensor_attested"] is False
    assert payload["attestation_ready"] is False
    assert payload["gps_available"] is True
    assert payload["inertial_available"] is False


def test_existing_gps_reality_gate_correctly_fail_closes_recorded_only_closure():
    evidence = _recorded()
    closure = build_gps_physical_world_closure_v0(evidence)
    state = build_gps_domain_gate_state_v0(evidence, closure)

    assert state.fail_closed is True
    assert state.state_name == "GPS_DEFENSE_AVIATION_UNTRUSTED"
    assert "CIC_ATTESTATION_FAILED" in state.reality_authenticity.reasons
    assert "MULTI_SOURCE_COHERENCE_FAILED" in state.reality_authenticity.reasons


def test_recorded_rf_remains_recorded_rf_not_live():
    closure = build_gps_physical_world_closure_v0(_recorded("RECORDED_REAL_RF"))
    assert closure.claim_scope == "RECORDED_REAL_RF"
    assert closure.recorded_real is True
    assert closure.live_claim_closed is False
    assert closure.allowed_to_decide is False
    assert closure.allowed_to_act is False


def test_non_public_proof_level_does_not_gain_recorded_real_claim():
    evidence = _recorded("STRUCTURED_STATE")
    closure = build_gps_physical_world_closure_v0(evidence)
    assert closure.recorded_real is False
    assert closure.claim_scope == "NON_PUBLIC_PHYSICAL_CLAIM"
