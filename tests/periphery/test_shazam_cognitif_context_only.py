import pytest
from periphery.cognitive_trees.tree_activation_vector import build_activation_vector
from periphery.cognitive_trees.shazam_cognitif import shazam_cognitif


def test_governance_pattern_detected():
    activations = [0.0] * 34
    for i in (26, 27, 33):
        activations[i] = 0.9
    v = build_activation_vector("sc1", activations)
    r = shazam_cognitif(v)
    assert "GOVERNANCE_SOVEREIGNTY_PATTERN" in r.patterns_detected


def test_no_pattern_on_zero_vector():
    v = build_activation_vector("sc2", [0.0] * 34)
    r = shazam_cognitif(v)
    assert r.patterns_detected == []


def test_context_only_invariants():
    v = build_activation_vector("sc3", [0.5] * 34)
    r = shazam_cognitif(v)
    assert r.context_signal_only is True
    assert r.can_decide is False
    assert r.can_emit_act is False


def test_dict_fields():
    v = build_activation_vector("sc4", [0.3] * 34)
    r = shazam_cognitif(v)
    d = r.to_dict()
    assert "patterns_detected" in d and "context_signal_only" in d and "can_emit_act" in d
