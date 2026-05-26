import pytest
from periphery.bdf.double_brain_router import route_double_brain
from periphery.bdf.llm_diffusion_mix import compute_diffusion_mix


def test_analytical_mode_high_complexity():
    r = route_double_brain("bdf1", complexity=0.9, uncertainty=0.1)
    assert r.mode == "ANALYTICAL"
    assert r.emits_act is False
    assert r.emits_verdict is False


def test_intuitive_mode_high_urgency():
    r = route_double_brain("bdf2", urgency=0.95)
    assert r.mode == "INTUITIVE"
    assert r.advisory_only is True


def test_balanced_mode_default():
    r = route_double_brain("bdf3")
    assert r.mode == "BALANCED"
    assert r.emits_act is False


def test_diffusion_mix_no_act():
    r = compute_diffusion_mix("bdf4", creativity_score=0.8)
    assert r.emits_act is False
    assert r.advisory_only is True
    assert 0 < r.temperature <= 1.0


def test_weights_sum_to_one():
    r = route_double_brain("bdf5", complexity=0.5)
    assert abs(r.system_1_weight + r.system_2_weight - 1.0) < 0.01
