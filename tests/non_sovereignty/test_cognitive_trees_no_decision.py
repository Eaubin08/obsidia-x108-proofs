"""
Non-sovereignty: cognitive trees produce context signals only, never decisions.
"""
import pytest
from periphery.cognitive_trees.tree_activation_vector import build_activation_vector, uniform_activation
from periphery.cognitive_trees.shazam_cognitif import shazam_cognitif
from periphery.cognitive_trees.memory_world_mapper import map_memory_world
from periphery.cognitive_trees.dominant_trees import find_dominant_trees


def test_activation_vector_cannot_decide():
    v = uniform_activation("ns_ct1", 1.0)
    assert v.can_decide is False
    assert v.can_emit_act is False


def test_shazam_cannot_decide():
    v = build_activation_vector("ns_ct2", [0.9] * 34)
    r = shazam_cognitif(v)
    assert r.can_decide is False
    assert r.can_emit_act is False


def test_memory_world_cannot_decide():
    v = build_activation_vector("ns_ct3", [0.5] * 34)
    r = shazam_cognitif(v)
    ctx = map_memory_world(r)
    assert ctx.can_decide is False
    assert ctx.can_emit_act is False
    assert ctx.context_signal_only is True


def test_dominant_trees_not_authority():
    v = build_activation_vector("ns_ct4", [1.0] * 34)
    r = find_dominant_trees(v)
    assert r.dominant_is_authority is False
