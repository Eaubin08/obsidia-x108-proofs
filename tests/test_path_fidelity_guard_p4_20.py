from obsidia_core.guardians.path_fidelity_guard import evaluate_path_fidelity


def nominal_payload():
    return {
        "flow_type": "POSITION_REPORT",
        "flight_id": "AF994",
        "risk_score": 0.12,
        "confidence_index": 0.96,
        "audit_score": 1.0,
        "freshness_ms": 24,
        "attestation_ready": True,
        "sensor_attested": True,
        "replay_window_detected": False,
        "gps_available": True,
        "inertial_available": True,
        "radio_available": True,
        "trajectory_drift_score": 0.02,
        "source_conflict_score": 0.01,
        "time_skew_score": 0.0,
        "brownout_score": 0.0,
        "ground_speed": 430,
        "g_load": 1.1,
        "rollback_possible": True,
    }


def test_p4_20_nominal_path_fidelity_is_evidence_only():
    payload = nominal_payload()
    payload["authorized_route_hash"] = "route-af994-demo"

    evidence = evaluate_path_fidelity(payload)

    assert evidence.path_fidelity_ok is True
    assert evidence.coherence_ok is True
    assert evidence.emits_verdict is False
    assert evidence.decision_authority == "KX108_ONLY"
    assert len(evidence.evidence_hash) == 64


def test_p4_20_spoof_or_replay_breaks_fidelity_without_authorizing():
    payload = nominal_payload()
    payload.update(
        {
            "authorized_route_hash": "route-af994-demo",
            "trajectory_drift_score": 0.82,
            "source_conflict_score": 0.71,
            "replay_window_detected": True,
            "freshness_ms": 86_400_000,
        }
    )

    evidence = evaluate_path_fidelity(payload)

    assert evidence.path_fidelity_ok is False
    assert evidence.emits_verdict is False
    assert "P4_20_SOURCE_COHERENCE_FAILED" in evidence.reason_codes
    assert "P4_20_DRIFT_BOUND_FAILED" in evidence.reason_codes
    assert "P4_20_REPLAY_CONSISTENCY_FAILED" in evidence.reason_codes
