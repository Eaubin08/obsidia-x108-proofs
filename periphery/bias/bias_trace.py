from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BiasTrace:
    action_id: str
    bias_score: float
    bias_source: str
    intercepted: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "bias_score": self.bias_score,
            "bias_source": self.bias_source,
            "intercepted": self.intercepted,
        }


def trace_bias(action_id: str, bias_score: float, source: str) -> BiasTrace:
    return BiasTrace(
        action_id=action_id,
        bias_score=bias_score,
        bias_source=source,
        intercepted=bias_score > 0.3,
    )
