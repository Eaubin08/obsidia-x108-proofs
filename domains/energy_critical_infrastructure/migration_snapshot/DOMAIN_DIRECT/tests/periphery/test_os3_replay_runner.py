import pytest
from periphery.common import ActionCandidate, PeripheralSignalPacket
from periphery.os3_ticket import build_os3_ticket
from periphery.os3_replay_manifest import build_replay_manifest
from periphery.os3_replay_runner import run_replay, replay_compare


def _make_action() -> ActionCandidate:
    return ActionCandidate(
        action_id="replay_test_001",
        domain="bank",
        actor_id="tester",
        intent="check_replay",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={"gross_value": 100.0},
    )


def _make_envelope():
    class Envelope:
        x108_gate = "ALLOW"
        reason_code = "CONFIDENCE_HIGH"
        severity = "INFO"
        metrics = {}
        unknowns = []
        risk_flags = []
        contradictions = []
        evidence_refs = []
    return Envelope()


def test_replay_pass_on_identical_inputs():
    action = _make_action()
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    envelope = _make_envelope()
    ticket = build_os3_ticket(action, packet, envelope)
    manifest = run_replay(ticket, action, packet, envelope)
    assert manifest.replay_status == "PASS"
    assert manifest.replay_compare_result == "MATCH"


def test_replay_fail_on_hash_mismatch():
    action = _make_action()
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    envelope = _make_envelope()
    ticket = build_os3_ticket(action, packet, envelope)
    ticket.input_hash = "aaaa1111" * 8
    manifest = run_replay(ticket, action, packet, envelope)
    assert manifest.replay_status == "FAIL"
    assert manifest.replay_compare_result == "MISMATCH"


def test_replay_no_world_action():
    action = _make_action()
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    envelope = _make_envelope()
    ticket = build_os3_ticket(action, packet, envelope)
    manifest = run_replay(ticket, action, packet, envelope)
    assert manifest.manifest_id
    assert manifest.os3_ticket_id == ticket.ticket_id
    assert "world_action" not in manifest.to_dict()


def test_replay_compare():
    assert replay_compare("abc", "abc") == "MATCH"
    assert replay_compare("abc", "xyz") == "MISMATCH"
