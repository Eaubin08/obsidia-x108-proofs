import pytest
from periphery.education.education_score import compute_education_score


def test_advanced_level():
    r = compute_education_score("ep1", 0.95, 0.92, 0.90, 0.88, 0.90)
    assert r.level == "ADVANCED"
    assert r.score >= 0.85


def test_below_threshold():
    r = compute_education_score("ep2", 0.1, 0.1, 0.1, 0.1, 0.1)
    assert r.level == "BELOW_THRESHOLD"


def test_score_clamped():
    r = compute_education_score("ep3", 1.0, 1.0, 1.0, 1.0, 1.0)
    assert 0.0 <= r.score <= 1.0


def test_score_dict_fields():
    r = compute_education_score("ep4", 0.7, 0.7, 0.7, 0.7, 0.7)
    d = r.to_dict()
    assert "score" in d and "level" in d and "stability" in d
