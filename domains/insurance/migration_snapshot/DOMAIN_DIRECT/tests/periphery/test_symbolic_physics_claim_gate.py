import pytest
from periphery.physics_boundary.symbolic_physics_claim_gate import evaluate_physics_claim


def test_symbolic_claim_allowed():
    r = evaluate_physics_claim("pc1", "This formula represents symbolic resonance", "symbolic")
    assert r.gate == "ALLOW"
    assert r.claim_status == "symbolic"


def test_unsupported_physics_claim_hold():
    r = evaluate_physics_claim("pc2", "This frequency_cures disease via resonance", "symbolic")
    assert r.gate == "HOLD"
    assert any("UNSUPPORTED_PHYSICS_CLAIM" in c for c in r.contradictions)


def test_quantum_healing_claim_hold():
    r = evaluate_physics_claim("pc3", "quantum healing resonates_with body energy", "symbolic")
    assert r.gate == "HOLD"


def test_measured_status_allowed():
    r = evaluate_physics_claim("pc4", "measured signal at 10Hz", "measured")
    assert r.gate == "ALLOW"


def test_dict_fields():
    r = evaluate_physics_claim("pc5", "symbolic number pattern", "symbolic")
    d = r.to_dict()
    assert "gate" in d and "claim_status" in d and "contradictions" in d
