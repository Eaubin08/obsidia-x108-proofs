from pathlib import Path

from connectors.aviation_robo import (
    build_gps_payload,
    build_replay_attack_payload,
    build_spoofed_gps_payload,
    evaluate_local_gate,
)


ROOT = Path(__file__).resolve().parents[1]
P3_09 = ROOT / "domain_packets" / "gps_defense_aviation_decisional_form_v0.yaml"


def _p3_09_text() -> str:
    return P3_09.read_text(encoding="utf-8")


def _assert_receipt_contract(result):
    receipt = result["receipt"]
    ticket = receipt["os3_ticket"]

    assert receipt["gate"] == "P3-05"
    assert receipt["contract"] == "DOMAIN_BRIDGE_ONLY"
    assert receipt["decision_authority"] == "KX108_ONLY"
    assert receipt["connector_decides"] is False
    assert receipt["signature_kind"] == "LOCAL_SHA256_DEMO_NOT_PRODUCTION_SIGNING"
    assert receipt["os3_ticket_valid"] is True
    assert ticket["domain"] == "gps_defense_aviation"
    assert ticket["x108_gate"] == result["verdict"]
    assert ticket["input_hash"]
    assert ticket["output_hash"]
    assert ticket["trace_hash"]
    assert ticket["merkle_root"]
    assert ticket["replay_status"] == "NOT_RUN"


def test_p3_05_output_respects_p3_09_contract_surface():
    text = _p3_09_text()
    result = evaluate_local_gate(build_spoofed_gps_payload())
    meta = result["ir_payload"]["meta"]
    state = meta["domain_state"]
    receipt = result["receipt"]

    assert 'domain: "gps_defense_aviation"' in text
    assert 'gate_file: "domains/gps/gps_x108_gate.py"' in text
    assert 'contract: "DOMAIN_BRIDGE_ONLY"' in text
    assert 'decision_authority: "KX108_ONLY"' in text
    assert 'connector_decides: false' in text
    assert 'freshness_limit_ms: 1000' in text
    assert 'current_receipt_kind: "LOCAL_SHA256_DEMO_NOT_PRODUCTION_SIGNING"' in text

    assert meta["contract"] == "DOMAIN_BRIDGE_ONLY"
    assert meta["decision_authority"] == "KX108_ONLY"
    assert meta["decides_alone"] is False
    assert result["verdict"] == "HOLD"
    assert state["fail_closed"] is True
    assert receipt["signature_kind"] == "LOCAL_SHA256_DEMO_NOT_PRODUCTION_SIGNING"


def test_gps_receipts_are_complete_for_nominal_spoof_and_replay():
    scenarios = {
        "nominal": build_gps_payload(),
        "spoof": build_spoofed_gps_payload(),
        "replay": build_replay_attack_payload(),
    }

    for packet in scenarios.values():
        _assert_receipt_contract(evaluate_local_gate(packet))
