import pytest
from periphery.gencoin_sandbox.avdr_phase_mapper import map_avdr_phase


def test_resolution_on_high_scores():
    result = map_avdr_phase("x", truth_score=0.92, sigma_score=0.85)
    assert result.phase == "RESOLUTION"


def test_accueil_on_low_scores():
    result = map_avdr_phase("x", truth_score=0.2, sigma_score=0.15)
    assert result.phase == "ACCUEIL"


def test_vibration_partial():
    result = map_avdr_phase("x", truth_score=0.55, sigma_score=0.45)
    assert result.phase == "VIBRATION"


def test_deploiement_mid():
    result = map_avdr_phase("x", truth_score=0.75, sigma_score=0.65)
    assert result.phase == "DEPLOIEMENT"


def test_has_reason():
    result = map_avdr_phase("x", truth_score=0.92, sigma_score=0.85)
    assert result.reason
    assert result.action_id == "x"
