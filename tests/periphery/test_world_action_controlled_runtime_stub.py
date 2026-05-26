import pytest
from periphery.common import ActionCandidate, PeripheralSignalPacket
from periphery.os3_ticket import build_os3_ticket
from periphery.world_action_controlled_runtime_stub import run_world_action_stub, WorldActionDryRunPacket


def _make_action():
    return ActionCandidate(
        action_id="wa_test_001",
        domain="bank",
        actor_id="tester",
        intent="test",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={},
    )


def _make_ticket(action, gate="ALLOW"):
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    class E:
        x108_gate = gate
        reason_code = "CONFIDENCE_HIGH"
        severity = "INFO"
        metrics = {}
        unknowns = []
        risk_flags = []
        contradictions = []
        evidence_refs = []
    from periphery.os3_ticket import build_os3_ticket
    return build_os3_ticket(action, packet, E())


def test_dry_run_only():
    action = _make_action()
    ticket = _make_ticket(action)
    pkt = run_world_action_stub(action, ticket, 50.0)
    assert pkt.dry_run_only is True
    assert pkt.world_action_allowed is False


def test_no_real_capabilities():
    action = _make_action()
    ticket = _make_ticket(action)
    pkt = run_world_action_stub(action, ticket, 50.0)
    assert "PAYMENT" in pkt.blocked_capabilities
    assert "TRADE_EXECUTION" in pkt.blocked_capabilities
    assert "EMAIL" in pkt.blocked_capabilities
    assert "MEMORY_WRITE" in pkt.blocked_capabilities


def test_human_takeover_required():
    action = _make_action()
    ticket = _make_ticket(action)
    pkt = run_world_action_stub(action, ticket, 0.0)
    assert pkt.requires_human_takeover is True
    assert pkt.consent_checkpoint_required is True


def test_assert_no_real_action_raises():
    pkt = WorldActionDryRunPacket(
        action_id="x",
        domain="bank",
        x108_gate="ALLOW",
        os3_valid=True,
        gencoin_candidate=100.0,
        world_action_allowed=True,
        dry_run_only=True,
    )
    with pytest.raises(AssertionError, match="WORLD_ACTION_FORBIDDEN"):
        pkt.assert_no_real_action()


def test_dict_output_complete():
    action = _make_action()
    ticket = _make_ticket(action)
    pkt = run_world_action_stub(action, ticket, 50.0)
    d = pkt.to_dict()
    assert "x108_gate" in d
    assert "dry_run_only" in d
    assert d["world_action_allowed"] is False
