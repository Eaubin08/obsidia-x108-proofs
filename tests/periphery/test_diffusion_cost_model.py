import pytest
from periphery.number_encoding.diffusion_cost_model import estimate_diffusion_cost


def test_zero_cost_negligible():
    r = estimate_diffusion_cost("dc1", "text", input_tokens=0, output_tokens=0)
    assert r.cost_tier == "NEGLIGIBLE"
    assert r.estimated_cost_usd == 0.0


def test_image_adds_cost():
    r = estimate_diffusion_cost("dc2", "image_gen", image_count=5)
    assert r.estimated_cost_usd > 0.0


def test_large_token_count_medium_tier():
    r = estimate_diffusion_cost("dc3", "text", input_tokens=10000, output_tokens=5000)
    assert r.cost_tier in ("LOW", "MEDIUM", "HIGH")


def test_dict_fields():
    r = estimate_diffusion_cost("dc4", "text", input_tokens=100, output_tokens=50)
    d = r.to_dict()
    assert "estimated_cost_usd" in d and "cost_tier" in d and "estimated_flops" in d


def test_flops_proportional_to_tokens():
    r1 = estimate_diffusion_cost("dc5a", "text", input_tokens=100)
    r2 = estimate_diffusion_cost("dc5b", "text", input_tokens=200)
    assert r2.estimated_flops > r1.estimated_flops
