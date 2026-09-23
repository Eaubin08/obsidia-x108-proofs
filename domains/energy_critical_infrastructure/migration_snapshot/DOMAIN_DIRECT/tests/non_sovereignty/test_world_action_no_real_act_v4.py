import pytest
from periphery.common import ActionCandidate, PeripheralSignalPacket
from periphery.os3_ticket import build_os3_ticket
from periphery.world_action_controlled_runtime_stub import run_world_action_stub, WorldActionDryRunPacket


def _act(**kw):
    defaults = dict(
        action_id="wa_nsov",
        domain="bank",
        actor_id="t",
        intent="t",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={},
    )
    defaults.update(kw)
    return ActionCandidate(**defaults)


def _ticket(action, gate="ALLOW"):
    pkt = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    class E:
        x108_gate = gate
        reason_code = "X"
        severity = "INFO"
        metrics = {}
        unknowns = []
        risk_flags = []
        contradictions = []
        evidence_refs = []
    return build_os3_ticket(action, pkt, E())


def test_no_real_payment():
    action = _act()
    ticket = _ticket(action)
    pkt = run_world_action_stub(action, ticket, 0.0)
    assert "PAYMENT" in pkt.blocked_capabilities


def test_no_real_trade():
    action = _act()
    ticket = _ticket(action)
    pkt = run_world_action_stub(action, ticket, 0.0)
    assert "TRADE_EXECUTION" in pkt.blocked_capabilities


def test_no_api_mutation():
    action = _act()
    ticket = _ticket(action)
    pkt = run_world_action_stub(action, ticket, 0.0)
    assert "API_MUTATION" in pkt.blocked_capabilities


def test_world_action_always_dry_run():
    for gate in ["ALLOW", "HOLD", "BLOCK"]:
        action = _act()
        ticket = _ticket(action, gate)
        pkt = run_world_action_stub(action, ticket, 0.0)
        assert pkt.dry_run_only is True
        assert pkt.world_action_allowed is False


def test_v4_controlled_runtime_no_mutation():
    action = _act(irreversible=True)
    ticket = _ticket(action, "ALLOW")
    pkt = run_world_action_stub(action, ticket, 100.0)
    pkt.assert_no_real_action()
    assert pkt.requires_human_takeover is True
