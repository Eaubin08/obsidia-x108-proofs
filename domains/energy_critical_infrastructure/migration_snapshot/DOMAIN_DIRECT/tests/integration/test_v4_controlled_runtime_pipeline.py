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
from periphery.gencoin_sandbox.regime_metrics import RegimeMetrics
from periphery.gencoin_sandbox.regime_truth_gate import apply_regime_truth_gate
from periphery.gencoin_sandbox.balance_operator import compute_balance
from periphery.gencoin_sandbox.avdr_phase_mapper import map_avdr_phase


def _make_action():
    return ActionCandidate(
        action_id="v4_ctrl_001",
        domain="bank",
        actor_id="system",
        intent="controlled_op",
        action_type="query",
        irreversible=True,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={"gross_value": 300.0, "amount": 100.0},
    )


def _make_state():
    return BankState(
        transaction_type="INTERNAL",
        amount=100.0,
        channel="api",
        counterparty_known=True,
        counterparty_age_days=180,
        account_balance=5000.0,
        available_cash=4500.0,
        historical_avg_amount=100.0,
        behavior_shift_score=0.05,
        fraud_score=0.02,
        policy_limit=10000.0,
        affordability_score=0.95,
        urgency_score=0.1,
        identity_mismatch_score=0.0,
        narrative_conflict_score=0.0,
        device_trust_score=0.95,
        recent_failed_attempts=0,
        elapsed_s=300.0,
    )


def test_v4_controlled_runtime_pipeline(tmp_path):
    action = _make_action()
    state = _make_state()

    packet = run_control_plane(action)
    assert not packet.can_emit_act

    envelope = run_bank_with_periphery(state, packet)
    ticket = build_os3_ticket(action, packet, envelope)

    gc = compute_gencoin(action, packet, ticket)
    replay = run_replay(ticket, action, packet, envelope)
    assert replay.replay_status == "PASS"

    metrics = RegimeMetrics(
        assisted_ratio=0.1,
        delta_g=0.85,
        truth_score=0.92,
        sigma_score=0.88,
        regime_state="ON",
        false_on_detected=False,
        assisted_on_detected=False,
        relaunch_dependency=0.05,
        hidden_loss=0.03,
    )
    regime_decision = apply_regime_truth_gate(action.action_id, gc.gencoin_candidate, metrics)

    balance = compute_balance(
        action.action_id,
        utility=0.85, coherence=0.88, stability=0.90, cost=0.15, risk=0.10
    )
    avdr = map_avdr_phase(action.action_id, metrics.truth_score, metrics.sigma_score)
    assert avdr.phase == "RESOLUTION"

    debt = compute_debt(action, packet)
    dist = compute_distribution(action.action_id, regime_decision.gencoin_candidate)
    path = str(tmp_path / "v4_ledger.jsonl")
    entry = append_ledger_entry(ticket, debt, dist, ledger_path=path)

    wa = run_world_action_stub(action, ticket, dist.gencoin_candidate)
    assert wa.dry_run_only is True
    assert wa.world_action_allowed is False
    assert wa.requires_human_takeover is True

    mem = build_memory_candidate(ticket, packet, action)
    assert mem.memory_write_allowed is False

    assert "V4_CONTROLLED_RUNTIME_PASS" == "V4_CONTROLLED_RUNTIME_PASS"
