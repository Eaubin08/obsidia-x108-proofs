import pytest
from periphery.cognitive_trees.tree_activation_vector import build_activation_vector
from periphery.cognitive_trees.dominant_trees import find_dominant_trees


def test_threshold_filters_correctly():
    activations = [0.8 if i in (3, 5, 7) else 0.05 for i in range(34)]
    v = build_activation_vector("dt1", activations)
    r = find_dominant_trees(v, theta=0.15)
    assert set(r.dominant_ids) == {3, 5, 7}
    assert r.dominant_count == 3


def test_zero_activations_no_dominant():
    v = build_activation_vector("dt2", [0.0] * 34)
    r = find_dominant_trees(v, theta=0.15)
    assert r.dominant_count == 0
    assert r.dominant_ids == []


def test_dominant_is_not_authority():
    v = build_activation_vector("dt3", [1.0] * 34)
    r = find_dominant_trees(v)
    assert r.dominant_is_authority is False
    assert r.context_signal_only is True


def test_default_theta_015():
    activations = [0.2 if i % 2 == 0 else 0.1 for i in range(34)]
    v = build_activation_vector("dt4", activations)
    r = find_dominant_trees(v)
    assert all(v.activations[i] >= 0.15 for i in r.dominant_ids)
