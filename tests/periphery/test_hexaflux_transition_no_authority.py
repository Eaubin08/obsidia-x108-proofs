import pytest
from periphery.hexaflux.transition_mapper import map_hexaflux_transition
from periphery.hexaflux.ltcu_plus import compute_ltcu_plus


def test_valid_transition_mapped():
    r = map_hexaflux_transition("hf1", "LATENT", "IGNITION")
    assert r.is_valid is True
    assert r.transition_type == "ACTIVATION_TRIGGER"
    assert r.authorizes is False


def test_invalid_transition():
    r = map_hexaflux_transition("hf2", "LATENT", "COMPRESSION")
    assert r.is_valid is False
    assert r.transition_type == "UNKNOWN_TRANSITION"


def test_advisory_only_invariant():
    r = map_hexaflux_transition("hf3", "EXPANSION", "STABILIZATION")
    assert r.advisory_only is True
    assert r.authorizes is False


def test_ltcu_plus_no_authority():
    r = compute_ltcu_plus("hf4", context_drift=0.2, temporal_coherence=0.9)
    assert r.advisory_only is True
    assert r.authorizes is False


def test_ltcu_high_drift_phase():
    r = compute_ltcu_plus("hf5", context_drift=0.9, temporal_coherence=0.3)
    assert r.phase == "DRIFT_HIGH"
