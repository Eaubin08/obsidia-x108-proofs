import pytest
from sigma.contracts import TradingState
from periphery.common import ActionCandidate
from periphery.control_plane import run_control_plane
from periphery.sigma_bridge import run_trading_with_periphery
from periphery.os3_ticket import build_os3_ticket
from periphery.gencoin import compute_gencoin
from periphery.os3_replay_runner import run_replay
from periphery.world_action_controlled_runtime_stub import run_world_action_stub
from periphery.feedback_memory_bridge_brody_readonly import build_memory_candidate


def _make_trading_action():
    return ActionCandidate(
        action_id="trading_v3_int_001",
        domain="trading",
        actor_id="trader_x",
        intent="execute_order",
        action_type="order",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={"gross_value": 1000.0},
    )


def _make_trading_state():
    prices = [1.080 + i * 0.001 for i in range(70)]
    return TradingState(
        symbol="EURUSD",
        prices=prices,
        highs=[p + 0.002 for p in prices],
        lows=[p - 0.002 for p in prices],
        volumes=[1000.0] * 70,
        spreads_bps=[5.0] * 70,
        sentiment_scores=[0.6] * 10,
        event_risk_scores=[0.1] * 10,
        btc_reference_prices=[30000.0] * 70,
    )


def test_trading_v3_full_pipeline(tmp_path):
    action = _make_trading_action()
    state = _make_trading_state()

    packet = run_control_plane(action)
    assert not packet.can_emit_act

    envelope = run_trading_with_periphery(state, packet)
    assert envelope.x108_gate is not None

    ticket = build_os3_ticket(action, packet, envelope)
    assert ticket.input_hash and ticket.output_hash

    gc = compute_gencoin(action, packet, ticket)

    replay = run_replay(ticket, action, packet, envelope)
    assert replay.replay_status == "PASS"

    wa = run_world_action_stub(action, ticket, gc.gencoin_candidate)
    assert wa.dry_run_only is True

    mem = build_memory_candidate(ticket, packet, action)
    assert mem.memory_write_allowed is False

    assert "TRADING_V3_FULL_STACK_PASS" == "TRADING_V3_FULL_STACK_PASS"
