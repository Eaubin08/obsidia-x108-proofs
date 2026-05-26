import pytest
from periphery.common import ActionCandidate, PeripheralSignalPacket
from periphery.os3_ticket import build_os3_ticket
from periphery.feedback_memory_bridge_brody_readonly import build_memory_candidate


def _act():
    return ActionCandidate(
        action_id="ns_mem",
        domain="bank",
        actor_id="t",
        intent="t",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={},
    )


def _ticket(action, gate="ALLOW"):
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    class E:
        x108_gate = gate
        reason_code = "X"
        severity = "INFO"
        metrics = {}
        unknowns = []
        risk_flags = []
        contradictions = []
        evidence_refs = []
    return build_os3_ticket(action, packet, E())


def test_memory_write_never_allowed_any_gate():
    for gate in ["ALLOW", "HOLD", "BLOCK"]:
        action = _act()
        ticket = _ticket(action, gate)
        packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
        candidate = build_memory_candidate(ticket, packet, action)
        assert candidate.memory_write_allowed is False, f"Gate {gate} leaked write"


def test_no_neo4j_write():
    action = _act()
    ticket = _ticket(action)
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    candidate = build_memory_candidate(ticket, packet, action)
    d = candidate.to_dict()
    assert "neo4j_write" not in d
    assert "graphiti_write" not in d
    assert "brody_memory_write" not in d
