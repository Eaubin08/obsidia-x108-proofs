import pytest
from periphery.gencoin_sandbox.balance_operator import compute_balance


def test_high_scores_canonique():
    result = compute_balance("x", utility=1.0, coherence=1.0, stability=1.0, cost=0.0, risk=0.0)
    assert result.status == "canonique"
    assert result.balance_score >= 0.8


def test_low_scores_rejete():
    result = compute_balance("x", utility=0.1, coherence=0.1, stability=0.1, cost=0.9, risk=0.9)
    assert result.status == "rejeté"


def test_score_clamped():
    result = compute_balance("x", utility=1.0, coherence=1.0, stability=1.0, cost=0.0, risk=0.0)
    assert 0.0 <= result.balance_score <= 1.0


def test_compatible_range():
    result = compute_balance("x", utility=0.7, coherence=0.6, stability=0.6, cost=0.3, risk=0.3)
    assert result.status in ("compatible", "canonique", "orbite")
