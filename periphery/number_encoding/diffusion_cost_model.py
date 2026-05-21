"""
Diffusion Cost Model — estimates computational cost of text/image diffusion operations.
Candidate cost estimates only. Sandbox.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_TOKEN_COST_USD = 0.000002
_IMAGE_COST_USD = 0.02
_FLOPS_PER_TOKEN = 1e9


@dataclass
class DiffusionCostEstimate:
    operation_id: str
    operation_type: str
    input_tokens: int
    output_tokens: int
    image_count: int
    estimated_flops: float
    estimated_cost_usd: float
    cost_tier: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "image_count": self.image_count,
            "estimated_flops": self.estimated_flops,
            "estimated_cost_usd": self.estimated_cost_usd,
            "cost_tier": self.cost_tier,
        }


def estimate_diffusion_cost(
    operation_id: str,
    operation_type: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    image_count: int = 0,
) -> DiffusionCostEstimate:
    total_tokens = input_tokens + output_tokens
    flops = total_tokens * _FLOPS_PER_TOKEN
    text_cost = total_tokens * _TOKEN_COST_USD
    image_cost = image_count * _IMAGE_COST_USD
    total_cost = text_cost + image_cost

    if total_cost < 0.001:
        tier = "NEGLIGIBLE"
    elif total_cost < 0.01:
        tier = "LOW"
    elif total_cost < 0.1:
        tier = "MEDIUM"
    else:
        tier = "HIGH"

    return DiffusionCostEstimate(
        operation_id=operation_id,
        operation_type=operation_type,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        image_count=image_count,
        estimated_flops=flops,
        estimated_cost_usd=round(total_cost, 6),
        cost_tier=tier,
    )
