import pytest
from periphery.consciousness_regimes.regime_classifier import classify_regime
from periphery.consciousness_regimes.collective_sandbox_summary import build_collective_summary


def test_empty_regimes():
    s = build_collective_summary("cs_empty", [])
    assert s.regime_count == 0
    assert s.collective_label == "NO_REGIMES"


def test_high_collective():
    regimes = [classify_regime(f"r{i}", 0.9, 0.9, 0.9) for i in range(3)]
    s = build_collective_summary("cs_high", regimes)
    assert s.collective_label == "COLLECTIVE_HIGH_OPERATIONAL"
    assert s.sandbox_only is True


def test_no_consciousness_claim_in_summary():
    regimes = [classify_regime("r1", 0.5, 0.5, 0.5)]
    s = build_collective_summary("cs_nc", regimes)
    assert s.no_consciousness_claim is True
    assert s.feeds_operational_constance is True


def test_dict_fields():
    regimes = [classify_regime("r1", 0.6, 0.6, 0.6)]
    s = build_collective_summary("cs_dict", regimes)
    d = s.to_dict()
    assert "sandbox_only" in d and "no_consciousness_claim" in d
