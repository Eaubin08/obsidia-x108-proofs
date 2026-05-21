"""
Phase F integration test: Gencoin regime truth gate → world action bus chain.
Validates that FALSE_ON blocks gencoin and world action bus records dry-run only.
"""
import pytest
from periphery.gencoin_sandbox.regime_metrics import RegimeMetrics
from periphery.gencoin_sandbox.regime_truth_gate import apply_regime_truth_gate
from periphery.gencoin_sandbox.balance_operator import compute_balance
from periphery.gencoin_sandbox.avdr_phase_mapper import map_avdr_phase
from periphery.world_calls.world_action_bus import publish_event
from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket


def _make_metrics(regime_state: str, truth_score: float, assisted_ratio: float, sigma_score: float = 0.8) -> RegimeMetrics:
    return RegimeMetrics(
        assisted_ratio=assisted_ratio,
        delta_g=0.1,
        truth_score=truth_score,
        sigma_score=sigma_score,
        regime_state=regime_state,
        false_on_detected=(regime_state == "FALSE_ON"),
        assisted_on_detected=(regime_state == "ASSISTED_ON"),
        relaunch_dependency=0.1,
        hidden_loss=0.05,
    )


def test_false_on_blocks_gencoin_world_action():
    metrics = _make_metrics("FALSE_ON", truth_score=0.3, assisted_ratio=0.7)
    decision = apply_regime_truth_gate("act_gc_001", gencoin_candidate=1.0, metrics=metrics)
    assert decision.gencoin_blocked is True
    assert decision.gencoin_candidate == 0.0
    assert "FALSE_ON_REGIME" in decision.risk_flags


def test_valid_regime_allows_gencoin():
    metrics = _make_metrics("ON", truth_score=0.95, assisted_ratio=0.1)
    decision = apply_regime_truth_gate("act_gc_002", gencoin_candidate=0.7, metrics=metrics)
    assert decision.gencoin_blocked is False
    assert decision.gencoin_candidate > 0.0


def test_world_action_bus_dry_run_after_gate_pass():
    metrics = _make_metrics("ON", truth_score=0.9, assisted_ratio=0.05)
    gate = apply_regime_truth_gate("act_gc_003", gencoin_candidate=0.5, metrics=metrics)
    assert gate.gencoin_blocked is False

    ticket = issue_sovereign_ticket(
        action_id="act_gc_003",
        os3_ticket_id="os3_gc_003",
        x108_gate="ALLOW",
        scope="gencoin",
        autonomy_level=1,
        world_call_class="NO_WORLD_CALL",
    )
    evt = publish_event(
        action_id="act_gc_003",
        sovereign_ticket_id=ticket.ticket_id,
        world_call_class="NO_WORLD_CALL",
        action_risk_class="READ_ONLY",
        autonomy_level=0,
        intent="gencoin_value_candidate",
        domain="gencoin",
        blocked=False,
        block_reason="",
    )
    assert evt.dry_run_only is True


def test_balance_and_avdr_full_chain():
    metrics = _make_metrics("ON", truth_score=0.92, assisted_ratio=0.08, sigma_score=0.88)
    gate = apply_regime_truth_gate("act_gc_004", gencoin_candidate=0.8, metrics=metrics)
    balance = compute_balance("act_gc_004", utility=0.85, coherence=0.85, stability=0.85, cost=0.05, risk=0.05)
    avdr = map_avdr_phase("act_gc_004", truth_score=metrics.truth_score, sigma_score=metrics.sigma_score)
    assert gate.gencoin_blocked is False
    assert balance.status in ("canonique", "compatible")
    assert avdr.phase in ("RESOLUTION", "DEPLOIEMENT")


def test_high_assisted_ratio_blocks_and_no_world_egress():
    metrics = _make_metrics("ASSISTED_ON", truth_score=0.85, assisted_ratio=0.8)
    gate = apply_regime_truth_gate("act_gc_005", gencoin_candidate=1.0, metrics=metrics)
    assert gate.gencoin_blocked is True
    assert "ASSISTED_ON_DOMINANT" in gate.risk_flags

    evt = publish_event(
        action_id="act_gc_005",
        sovereign_ticket_id="no_ticket",
        world_call_class="NO_WORLD_CALL",
        action_risk_class="READ_ONLY",
        autonomy_level=0,
        intent="blocked_gencoin",
        domain="gencoin",
        blocked=True,
        block_reason="GENCOIN_BLOCKED_ASSISTED_ON",
    )
    assert evt.dry_run_only is True
