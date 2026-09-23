import pytest
from periphery.consciousness_regimes.regime_classifier import classify_regime
from periphery.consciousness_regimes.passfail_metrics import evaluate_passfail
from periphery.consciousness_regimes.collective_sandbox_summary import build_collective_summary


def test_high_scores_operational_high():
    r = classify_regime("cr1", coherence=0.9, integration=0.9, responsiveness=0.9)
    assert r.operational_label == "OPERATIONAL_HIGH"
    assert r.sandbox_only is True
    assert r.consciousness_claim is False


def test_low_scores_dormant():
    r = classify_regime("cr2", coherence=0.1, integration=0.1, responsiveness=0.1)
    assert r.operational_label == "DORMANT"


def test_passfail_all_pass():
    r = evaluate_passfail("cr3", coherence=0.8, integration=0.8, responsiveness=0.8)
    assert r.overall_pass is True
    assert r.sandbox_only is True


def test_passfail_partial_fail():
    r = evaluate_passfail("cr4", coherence=0.8, integration=0.3, responsiveness=0.5)
    assert r.integration_pass is False
    assert r.overall_pass is False


def test_collective_summary():
    r1 = classify_regime("cr5a", 0.8, 0.8, 0.8)
    r2 = classify_regime("cr5b", 0.6, 0.6, 0.6)
    s = build_collective_summary("cs1", [r1, r2])
    assert s.regime_count == 2
    assert s.sandbox_only is True
    assert s.no_consciousness_claim is True
