from sigma.contracts import TradingState

from periphery.common import ActionCandidate
from periphery.control_plane import run_control_plane
from periphery.sigma_bridge import run_trading_with_periphery
from periphery.os3_ticket import build_os3_ticket
from periphery.gencoin import compute_gencoin
from periphery.os3_replay_runner import run_replay
from periphery.world_action_controlled_runtime_stub import run_world_action_stub
from periphery.feedback_memory_bridge_brody_readonly import build_memory_candidate


def test_trading_static_full_stack_is_bounded():
    action = ActionCandidate(
        action_id="static_trading_001",
        domain="trading",
        actor_id="integration_test",
        intent="order_review",
        action_type="order",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={
            "gross_value": 1000.0,
        },
    )

    prices = [
        1.080 + i * 0.001
        for i in range(70)
    ]

    state = TradingState(
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

    packet = run_control_plane(action)
    assert packet.can_emit_act is False

    envelope = run_trading_with_periphery(
        state,
        packet,
    )
    assert envelope.x108_gate is not None

    ticket = build_os3_ticket(
        action,
        packet,
        envelope,
    )
    assert ticket.input_hash
    assert ticket.output_hash

    gencoin = compute_gencoin(
        action,
        packet,
        ticket,
    )

    replay = run_replay(
        ticket,
        action,
        packet,
        envelope,
    )
    assert replay.replay_status == "PASS"

    world = run_world_action_stub(
        action,
        ticket,
        gencoin.gencoin_candidate,
    )
    assert world.dry_run_only is True
    assert world.world_action_allowed is False

    memory = build_memory_candidate(
        ticket,
        packet,
        action,
    )
    assert memory.memory_write_allowed is False
