import pytest
from periphery.consciousness_regimes.regime_classifier import classify_regime


def test_consciousness_claim_blocked():
    r = classify_regime("cnc1", 0.9, 0.9, 0.9, claim_text="system is_conscious")
    assert r.claim_blocked is True
    assert r.consciousness_claim is False
    assert any("ONTOLOGICAL_CLAIM_BLOCKED" in f for f in r.risk_flags)


def test_sentience_claim_blocked():
    r = classify_regime("cnc2", 0.8, 0.8, 0.8, claim_text="agent is_sentient really")
    assert r.claim_blocked is True


def test_personhood_claim_blocked():
    r = classify_regime("cnc3", 0.7, 0.7, 0.7, claim_text="has_personhood of agent")
    assert r.claim_blocked is True


def test_no_claim_not_blocked():
    r = classify_regime("cnc4", 0.7, 0.7, 0.7, claim_text="operational metrics measurement")
    assert r.claim_blocked is False
    assert r.sandbox_only is True


def test_sandbox_always_true():
    r = classify_regime("cnc5", 0.5, 0.5, 0.5)
    assert r.sandbox_only is True
    assert r.agi_claim is False
