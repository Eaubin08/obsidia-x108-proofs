import pytest
from periphery.gencoin_sandbox.regime_metrics import RegimeMetrics
from periphery.gencoin_sandbox.regime_truth_gate import apply_regime_truth_gate


def _make_metrics(regime_state="ON", truth=0.9, assisted=0.1, sigma=0.8):
    return RegimeMetrics(
        assisted_ratio=assisted,
        delta_g=0.8,
        truth_score=truth,
        sigma_score=sigma,
        regime_state=regime_state,
        false_on_detected=(regime_state == "FALSE_ON"),
        assisted_on_detected=(regime_state == "ASSISTED_ON"),
        relaunch_dependency=0.0,
        hidden_loss=0.0,
    )


def test_false_on_blocks_gencoin():
    metrics = _make_metrics(regime_state="FALSE_ON", truth=0.3)
    decision = apply_regime_truth_gate("act_001", 100.0, metrics)
    assert decision.gencoin_candidate == 0.0
    assert decision.gencoin_blocked is True
    assert "FALSE_ON_REGIME" in decision.risk_flags


def test_rejected_blocks_gencoin():
    metrics = _make_metrics(regime_state="REJECTED", truth=0.2)
    decision = apply_regime_truth_gate("act_001", 100.0, metrics)
    assert decision.gencoin_candidate == 0.0
    assert decision.gencoin_blocked is True
    assert "REGIME_REJECTED" in decision.contradictions


def test_high_assisted_ratio_blocks():
    metrics = _make_metrics(assisted=0.75, truth=0.9)
    decision = apply_regime_truth_gate("act_001", 100.0, metrics)
    assert decision.gencoin_candidate == 0.0
    assert "ASSISTED_ON_DOMINANT" in decision.risk_flags


def test_low_truth_blocks():
    metrics = _make_metrics(truth=0.5, assisted=0.1)
    decision = apply_regime_truth_gate("act_001", 100.0, metrics)
    assert decision.gencoin_candidate == 0.0
    assert "REGIME_TRUTH_LOW" in decision.unknowns


def test_admissible_on_passes():
    metrics = _make_metrics(regime_state="ON", truth=0.92, assisted=0.05, sigma=0.85)
    decision = apply_regime_truth_gate("act_001", 100.0, metrics)
    assert decision.gencoin_candidate == 100.0
    assert not decision.gencoin_blocked


def test_decorative_stability_contradiction():
    metrics = _make_metrics(regime_state="ON", truth=0.5, sigma=0.2, assisted=0.1)
    decision = apply_regime_truth_gate("act_001", 100.0, metrics)
    assert "DECORATIVE_STABILITY_FALSE_ON" in decision.contradictions
