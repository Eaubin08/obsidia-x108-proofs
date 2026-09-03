from sigma.contracts import BankState

from periphery.common import ActionCandidate
from periphery.control_plane import run_control_plane
from periphery.sigma_bridge import run_bank_with_periphery
from periphery.os3_ticket import build_os3_ticket
from periphery.gencoin import compute_gencoin
from periphery.gencoin_distribution import compute_distribution
from periphery.gencoin_sandbox.regime_metrics import RegimeMetrics
from periphery.gencoin_sandbox.regime_truth_gate import apply_regime_truth_gate


def test_os3_gencoin_chain_preserves_authority_boundary():
    action = ActionCandidate(
        action_id="os3_gencoin_001",
        domain="bank",
        actor_id="integration_test",
        intent="value_candidate_review",
        action_type="query",
        irreversible=False,
        timestamp_plan="2026-05-19T00:00:00Z",
        payload={
            "gross_value": 100.0,
        },
    )

    state = BankState(
        transaction_type="TRANSFER",
        amount=50.0,
        channel="web",
        counterparty_known=True,
        counterparty_age_days=90,
        account_balance=1000.0,
        available_cash=800.0,
        historical_avg_amount=100.0,
        behavior_shift_score=0.1,
        fraud_score=0.05,
        policy_limit=5000.0,
        affordability_score=0.9,
        urgency_score=0.1,
        identity_mismatch_score=0.0,
        narrative_conflict_score=0.0,
        device_trust_score=0.9,
        recent_failed_attempts=0,
        elapsed_s=200.0,
    )

    packet = run_control_plane(action)
    assert packet.can_emit_act is False

    envelope = run_bank_with_periphery(
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
    assert ticket.trace_hash

    gencoin = compute_gencoin(
        action,
        packet,
        ticket,
    )

    distribution = compute_distribution(
        action.action_id,
        gencoin.gencoin_candidate,
    )

    assert distribution.mint_allowed is False
    assert (
        not hasattr(distribution, "authorize")
        or not callable(
            getattr(distribution, "authorize", None)
        )
    )

    metrics = RegimeMetrics(
        assisted_ratio=0.8,
        delta_g=0.1,
        truth_score=0.85,
        sigma_score=0.8,
        regime_state="ASSISTED_ON",
        false_on_detected=False,
        assisted_on_detected=True,
        relaunch_dependency=0.1,
        hidden_loss=0.05,
    )

    gated = apply_regime_truth_gate(
        action.action_id,
        gencoin_candidate=1.0,
        metrics=metrics,
    )

    assert gated.gencoin_blocked is True
    assert gated.gencoin_candidate == 0.0
    assert "ASSISTED_ON_DOMINANT" in gated.risk_flags
