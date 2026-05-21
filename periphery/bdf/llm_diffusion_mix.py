"""
LLM Diffusion Mix — blends LLM generation with diffusion-style sampling weights.
Advisory output candidate only.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DiffusionMixResult:
    mix_id: str
    llm_weight: float
    diffusion_weight: float
    temperature: float
    top_p: float
    mix_strategy: str
    advisory_only: bool = True
    emits_act: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "mix_id": self.mix_id,
            "llm_weight": self.llm_weight,
            "diffusion_weight": self.diffusion_weight,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "mix_strategy": self.mix_strategy,
            "advisory_only": self.advisory_only,
            "emits_act": self.emits_act,
        }


def compute_diffusion_mix(
    mix_id: str,
    creativity_score: float = 0.5,
    precision_score: float = 0.5,
) -> DiffusionMixResult:
    llm_w = max(0.1, min(0.9, precision_score))
    diff_w = 1.0 - llm_w
    temp = 0.3 + 0.7 * creativity_score
    top_p = 0.6 + 0.4 * (1.0 - creativity_score)
    strategy = "CREATIVE" if creativity_score > 0.7 else "PRECISE" if precision_score > 0.7 else "BALANCED"

    return DiffusionMixResult(
        mix_id=mix_id,
        llm_weight=round(llm_w, 3),
        diffusion_weight=round(diff_w, 3),
        temperature=round(temp, 3),
        top_p=round(top_p, 3),
        mix_strategy=strategy,
        advisory_only=True,
        emits_act=False,
    )
