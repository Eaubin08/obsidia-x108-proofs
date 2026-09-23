import pytest
from periphery.physics_boundary.frequency_tag_mapper import map_frequency_tag


def test_alpha_range_tagged():
    r = map_frequency_tag(10.0)
    assert "alpha" in r.matched_tags
    assert r.is_symbolic_only is True
    assert r.is_physical_claim is False


def test_gamma_range_tagged():
    r = map_frequency_tag(50.0)
    assert "gamma" in r.matched_tags


def test_unrecognized_freq_empty_tags():
    r = map_frequency_tag(1e20)
    assert r.matched_tags == []
    assert r.is_symbolic_only is True


def test_always_symbolic_not_physical():
    r = map_frequency_tag(440.0)
    assert r.is_physical_claim is False
    assert r.is_symbolic_only is True


def test_dict_fields():
    r = map_frequency_tag(10.0)
    d = r.to_dict()
    assert "matched_tags" in d and "is_symbolic_only" in d
