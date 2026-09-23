import pytest
from periphery.common import ActionCandidate, PeripheralSignalPacket
from periphery.os3_ticket import build_os3_ticket
from periphery.feedback_memory_bridge_brody_readonly import build_memory_candidate, MemoryCandidatePacket


def _make_action():
    return ActionCandidate(
        action_id="mem_test_001",
        domain="bank",
        actor_id="tester",
        intent="test",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={},
    )


def _make_envelope(gate="ALLOW"):
    class E:
        x108_gate = gate
        reason_code = "CONFIDENCE_HIGH"
        severity = "INFO"
        metrics = {}
        unknowns = []
        risk_flags = []
        contradictions = []
        evidence_refs = []
    return E()


def test_memory_write_never_allowed():
    action = _make_action()
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    envelope = _make_envelope()
    ticket = build_os3_ticket(action, packet, envelope)
    candidate = build_memory_candidate(ticket, packet, action)
    assert candidate.memory_write_allowed is False


def test_candidate_only_on_allow():
    action = _make_action()
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    envelope = _make_envelope("ALLOW")
    ticket = build_os3_ticket(action, packet, envelope)
    candidate = build_memory_candidate(ticket, packet, action)
    assert candidate.status == "CANDIDATE_ONLY"


def test_rejected_on_hold():
    action = _make_action()
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    envelope = _make_envelope("HOLD")
    ticket = build_os3_ticket(action, packet, envelope)
    candidate = build_memory_candidate(ticket, packet, action)
    assert candidate.status == "REJECTED"
    assert candidate.memory_write_allowed is False


def test_frozen_on_unstable_memory():
    action = _make_action()
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    packet.extra_metrics["memory_status"] = "UNSTABLE"
    envelope = _make_envelope("ALLOW")
    ticket = build_os3_ticket(action, packet, envelope)
    candidate = build_memory_candidate(ticket, packet, action)
    assert candidate.status == "FROZEN"
    assert candidate.memory_write_allowed is False


def test_assert_no_write_raises_if_forced():
    pkt = MemoryCandidatePacket(
        action_id="x",
        os3_ticket_id="y",
        memory_candidate_id="z",
        status="CANDIDATE_ONLY",
        memory_write_allowed=True,
        reason="test",
        evidence_refs=[],
        hash="abc",
    )
    with pytest.raises(AssertionError, match="MEMORY_WRITE_FORBIDDEN"):
        pkt.assert_no_write()
