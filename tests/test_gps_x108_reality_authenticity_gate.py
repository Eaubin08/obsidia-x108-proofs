from domains.gps.gps_x108_gate import GpsX108Gate
from domains.gps.nuisance_registry import classify_gps_payload


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


def test_nominal_payload_builds_coherent_domain_state():
    state = GpsX108Gate().build_domain_state(nominal_payload())

    assert state.state_name == "GPS_DEFENSE_AVIATION_COHERENT"
    assert state.fail_closed is False
    assert state.nuisances == ()
    assert state.reality_authenticity.reasons == ()
    assert len(state.domain_state_hash) == 64


def test_spoofed_payload_fail_closes_before_kernel():
    payload = nominal_payload()
    payload.update(
        {
            "trajectory_drift_score": 0.82,
            "source_conflict_score": 0.71,
            "spoof_score": 0.84,
            "signal_noise_ratio": 0.41,
        }
    )

    result = GpsX108Gate().evaluate(payload)

    assert result["verdict"] == "HOLD"
    assert result["source"] == "REALITY_AUTHENTICITY_GATE_FAIL_CLOSED"
    assert result["receipt"]["connector_decides"] is False
    assert result["receipt"]["os3_ticket_valid"] is True
    assert result["receipt"]["os3_ticket"]["domain"] == "gps_defense_aviation"
    assert result["receipt"]["os3_ticket"]["x108_gate"] == "HOLD"
    assert result["receipt"]["os3_ticket"]["replay_status"] == "NOT_RUN"
    nuisances = result["ir_payload"]["meta"]["domain_state"]["nuisances"]
    assert "GPS_SPOOFING" in nuisances
    assert "MULTI_SOURCE_CONTRADICTION" in nuisances


def test_replay_attack_is_classified_as_provenance_failure():
    payload = nominal_payload()
    payload.update(
        {
            "freshness_ms": 86_400_000,
            "time_skew_score": 1.0,
            "replay_window_detected": True,
            "attestation_ready": False,
            "sensor_attested": False,
        }
    )

    labels = {entry.label for entry in classify_gps_payload(payload)}
    state = GpsX108Gate().build_domain_state(payload)

    assert "REPLAY_ATTACK" in labels
    assert "CIC_ATTESTATION_FAILURE" in labels
    assert "ORACLE_FRESHNESS_FAILED" in state.reality_authenticity.reasons
    assert "CIC_ATTESTATION_FAILED" in state.reality_authenticity.reasons


def test_nominal_hold_receipt_carries_os3_ticket_without_claiming_replay_run():
    result = GpsX108Gate().evaluate(nominal_payload())
    ticket = result["receipt"]["os3_ticket"]

    assert result["verdict"] in {"HOLD", "ALLOW"}
    assert result["receipt"]["os3_ticket_valid"] is True
    assert ticket["domain"] == "gps_defense_aviation"
    assert ticket["reason_code"] in {"REQUESTS_UNAVAILABLE", "KERNEL_UNREACHABLE", "KERNEL_X108"}
    assert ticket["input_hash"]
    assert ticket["output_hash"]
    assert ticket["trace_hash"]
    assert ticket["merkle_root"]
    assert ticket["replay_status"] == "NOT_RUN"


def test_nominal_kernel_payload_carries_complete_gps_state():
    gate = GpsX108Gate()
    payload = nominal_payload()
    state = gate.build_domain_state(payload)
    kernel_payload = gate.build_kernel_state_payload(payload, state)

    for key in (
        "gps_available",
        "inertial_available",
        "radio_available",
        "trajectory_drift_score",
        "source_conflict_score",
        "time_skew_score",
        "brownout_score",
        "attestation_ready",
        "rollback_possible",
    ):
        assert key in kernel_payload

    assert kernel_payload["inertial_available"] is True
    assert kernel_payload["radio_available"] is True
    assert kernel_payload["attestation_ready"] is True
