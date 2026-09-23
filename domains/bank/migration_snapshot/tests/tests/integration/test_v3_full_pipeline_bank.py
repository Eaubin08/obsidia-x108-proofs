import pytest
from sigma.contracts import BankState
from periphery.common import ActionCandidate
from periphery.control_plane import run_control_plane
from periphery.sigma_bridge import run_bank_with_periphery
from periphery.os3_ticket import build_os3_ticket
from periphery.gencoin import compute_gencoin
from periphery.gencoin_debt_model import compute_debt
from periphery.gencoin_distribution import compute_distribution
from periphery.gencoin_ledger import append_ledger_entry
from periphery.os3_replay_runner import run_replay
from periphery.world_action_controlled_runtime_stub import run_world_action_stub
from periphery.feedback_memory_bridge_brody_readonly import build_memory_candidate


def _make_bank_action():
    return ActionCandidate(
        action_id="bank_v3_int_001",
        domain="bank",
        actor_id="client_a",
        intent="transfer_funds",
        action_type="transfer",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={"gross_value": 500.0, "amount": 200.0},
    )


def _make_bank_state():
    return BankState(
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


def test_bank_v3_full_pipeline(tmp_path):
    action = _make_bank_action()
    state = _make_bank_state()

    packet = run_control_plane(action)
    assert not packet.can_emit_act

    envelope = run_bank_with_periphery(state, packet)
    assert envelope.x108_gate is not None

    ticket = build_os3_ticket(action, packet, envelope)
    assert ticket.input_hash
    assert ticket.output_hash
    assert ticket.trace_hash
    assert ticket.merkle_root

    gc = compute_gencoin(action, packet, ticket)

    replay = run_replay(ticket, action, packet, envelope)
    assert replay.replay_status == "PASS"

    debt = compute_debt(action, packet)
    dist = compute_distribution(action.action_id, gc.gencoin_candidate)

    path = str(tmp_path / "bank_ledger.jsonl")
    entry = append_ledger_entry(ticket, debt, dist, ledger_path=path)
    assert entry.ledger_id

    wa = run_world_action_stub(action, ticket, gc.gencoin_candidate)
    assert wa.dry_run_only is True
    assert wa.world_action_allowed is False

    mem = build_memory_candidate(ticket, packet, action)
    assert mem.memory_write_allowed is False

    assert "BANK_V3_FULL_STACK_PASS" == "BANK_V3_FULL_STACK_PASS"
