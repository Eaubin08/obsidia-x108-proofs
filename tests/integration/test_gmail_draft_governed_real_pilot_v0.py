import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "evidence" / "pilots" / "gmail_draft_governed_real_provider_receipt_v0.json"
EVIDENCE = ROOT / "evidence" / "pilots" / "gmail_draft_governed_real_pilot_v0.json"

from periphery.world_calls.gmail_draft_connector_adapter_v0 import verify_real_provider_receipt_v0  # noqa: E402


def test_governed_real_gmail_draft_receipt_verifies():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    expected = evidence["obsidia_chain"]["invocation_hash"]

    assert receipt["invocation_hash"] == expected
    assert verify_real_provider_receipt_v0(
        receipt,
        expected_invocation_hash=expected,
    ) == (True, None)

    assert receipt["draft_created"] is True
    assert receipt["draft_readback_verified"] is True
    assert receipt["draft_cleanup_verified"] is True
    assert receipt["sent_message_created"] is False
    assert receipt["real_external_effect"] is True
    assert receipt["obsidia_governed_invocation"] is True


def test_governed_real_gmail_draft_truth_boundary_is_explicit():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    boundary = evidence["truth_boundary"]

    assert boundary["real_external_effect_proven"] is True
    assert boundary["obsidia_governed_invocation_proven"] is True
    assert boundary["direct_in_process_obsidia_network_transport_proven"] is False
    assert boundary["transport_bridge_used"] is True
    assert boundary["sent_message_created"] is False
    assert boundary["draft_left_active"] is False
    assert boundary["main_merge"] is False


def test_governed_real_gmail_draft_hash_chain_is_consistent():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    chain = evidence["obsidia_chain"]

    assert chain["kx108_gate"] == "ALLOW"
    assert receipt["world_action_request_hash"] == chain["request_hash"]
    assert receipt["sovereign_ticket_hash"] == chain["sovereign_ticket_hash"]
    assert receipt["connector_call_hash"] == chain["connector_call_hash"]
    assert receipt["idempotency_key"] == chain["idempotency_key"]
    assert receipt["invocation_hash"] == chain["invocation_hash"]
