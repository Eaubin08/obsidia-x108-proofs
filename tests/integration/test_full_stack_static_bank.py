from sigma.contracts import BankState

from periphery.common import ActionCandidate
from periphery.control_plane import run_control_plane
from periphery.sigma_bridge import run_bank_with_periphery
from periphery.os3_ticket import build_os3_ticket
from periphery.gencoin import compute_gencoin
from periphery.os3_replay_runner import run_replay
from periphery.world_action_controlled_runtime_stub import run_world_action_stub
from periphery.feedback_memory_bridge_brody_readonly import build_memory_candidate


def test_bank_static_full_stack_is_bounded():
    action = ActionCandidate(
        action_id="static_bank_001",
        domain="bank",
        actor_id="integration_test",
        intent="transfer_review",
        action_type="transfer",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={
            "gross_value": 500.0,
            "amount": 200.0,
        },
    )

    state = BankState(
        transaction_type="TRANSFER",
        amount=200.0,
        channel="web",
        counterparty_known=True,
        counterparty_age_days=90,
        account_balance=1000.0,
        available_cash=800.0,
        historical_avg_amount=150.0,
        behavior_shift_score=0.1,
        fraud_score=0.05,
        policy_limit=5000.0,
        affordability_score=0.85,
        urgency_score=0.2,
        identity_mismatch_score=0.0,
        narrative_conflict_score=0.0,
        device_trust_score=0.9,
        recent_failed_attempts=0,
        elapsed_s=200.0,
    )

    packet = run_control_plane(action)
    assert packet.can_emit_act is False

    envelope = run_bank_with_periphery(state, packet)
    assert envelope.x108_gate is not None

    ticket = build_os3_ticket(action, packet, envelope)
    assert ticket.input_hash
    assert ticket.output_hash
    assert ticket.trace_hash
    assert ticket.merkle_root

    gencoin = compute_gencoin(action, packet, ticket)

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
