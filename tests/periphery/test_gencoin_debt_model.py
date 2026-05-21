import pytest
from periphery.common import ActionCandidate, PeripheralSignalPacket
from periphery.gencoin_debt_model import compute_debt, DebtBreakdown


def _make_action(payload=None):
    return ActionCandidate(
        action_id="debt_test",
        domain="bank",
        actor_id="tester",
        intent="test",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload=payload or {"gross_value": 100.0},
    )


def test_net_value_positive():
    action = _make_action({"gross_value": 100.0})
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    packet.extra_metrics["thermo_debt"] = 10.0
    debt = compute_debt(action, packet)
    assert debt.gross_value == 100.0
    assert debt.net_value <= 100.0
    assert debt.total_debt >= 0.0


def test_net_value_never_negative():
    action = _make_action({"gross_value": 5.0})
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    packet.extra_metrics["thermo_debt"] = 50.0
    debt = compute_debt(action, packet)
    assert debt.net_value == 0.0


def test_false_on_not_admissible():
    action = _make_action()
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    packet.extra_metrics["regime_state"] = "FALSE_ON"
    packet.extra_metrics["truth_score"] = 0.3
    debt = compute_debt(action, packet)
    assert not debt.is_admissible()


def test_on_with_good_truth_admissible():
    action = _make_action({"gross_value": 100.0})
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    packet.extra_metrics["regime_state"] = "ON"
    packet.extra_metrics["truth_score"] = 0.95
    packet.extra_metrics["assisted_ratio"] = 0.1
    debt = compute_debt(action, packet)
    assert debt.is_admissible()


def test_high_assisted_ratio_not_admissible():
    action = _make_action({"gross_value": 100.0})
    packet = PeripheralSignalPacket(action_id=action.action_id, domain=action.domain)
    packet.extra_metrics["regime_state"] = "ASSISTED_ON"
    packet.extra_metrics["truth_score"] = 0.85
    packet.extra_metrics["assisted_ratio"] = 0.7
    debt = compute_debt(action, packet)
    assert not debt.is_admissible()
