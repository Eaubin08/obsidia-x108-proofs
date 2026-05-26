import pytest
from periphery.cognitive_trees.tree_activation_vector import build_activation_vector, uniform_activation, N_TREES


def test_vector_has_34_elements():
    v = uniform_activation("v1", 0.2)
    assert len(v.activations) == N_TREES == 34


def test_activations_clamped_to_unit_interval():
    v = build_activation_vector("v2", [2.0, -1.0] + [0.5] * 32)
    assert v.activations[0] == 1.0
    assert v.activations[1] == 0.0


def test_context_signal_only():
    v = build_activation_vector("v3", [0.5] * 34)
    assert v.context_signal_only is True
    assert v.can_decide is False
    assert v.can_emit_act is False


def test_wrong_length_raises():
    with pytest.raises(ValueError):
        from periphery.cognitive_trees.tree_activation_vector import TreeActivationVector
        TreeActivationVector("bad", [0.5] * 10)


def test_dict_fields():
    v = uniform_activation("v5", 0.1)
    d = v.to_dict()
    assert "activations" in d and "context_signal_only" in d and "can_emit_act" in d
