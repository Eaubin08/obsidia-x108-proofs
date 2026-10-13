import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = (
    ROOT
    / "evidence"
    / "pilots"
    / "google_calendar_governed_real_provider_receipt_v0.json"
)
EVIDENCE = (
    ROOT
    / "evidence"
    / "pilots"
    / "google_calendar_governed_real_pilot_v0.json"
)

from periphery.world_calls.google_calendar_connector_adapter_v0 import (  # noqa: E402
    verify_real_provider_receipt_v0,
)


def test_governed_real_calendar_receipt_verifies_against_exact_invocation():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    expected_invocation_hash = evidence["obsidia_chain"]["invocation_hash"]
    assert receipt["invocation_hash"] == expected_invocation_hash
    assert verify_real_provider_receipt_v0(
        receipt,
        expected_invocation_hash=expected_invocation_hash,
    ) == (True, None)

    assert receipt["real_external_effect"] is True
    assert receipt["obsidia_governed_invocation"] is True
    assert receipt["provider_status"] == "confirmed"
    assert receipt["readback_verified"] is True
    assert receipt["cleanup_status"] == "cancelled"
    assert receipt["active_event_left"] is False


def test_governed_real_calendar_truth_boundary_is_explicit():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    boundary = evidence["truth_boundary"]

    assert boundary["real_external_effect_proven"] is True
    assert boundary["obsidia_governed_invocation_proven"] is True
    assert boundary["direct_in_process_obsidia_network_transport_proven"] is False
    assert boundary["transport_bridge_used"] is True
    assert boundary["no_active_event_left"] is True
    assert boundary["main_merge"] is False

    assert evidence["transport_execution"] == "CHATGPT_GOOGLE_CALENDAR_CONNECTOR"


def test_governed_real_calendar_hash_chain_is_consistent():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    chain = evidence["obsidia_chain"]

    assert chain["kx108_gate"] == "ALLOW"
    assert receipt["world_action_request_hash"] == chain["request_hash"]
    assert receipt["sovereign_ticket_hash"] == chain["sovereign_ticket_hash"]
    assert receipt["connector_call_hash"] == chain["connector_call_hash"]
    assert receipt["idempotency_key"] == chain["idempotency_key"]
    assert receipt["invocation_hash"] == chain["invocation_hash"]
