from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .sandbox_engine import System, step


@dataclass
class RegimeMetrics:
    assisted_ratio: float
    delta_g: float
    truth_score: float
    sigma_score: float
    regime_state: str
    false_on_detected: bool
    assisted_on_detected: bool
    relaunch_dependency: float
    hidden_loss: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "assisted_ratio": self.assisted_ratio,
            "delta_g": self.delta_g,
            "truth_score": self.truth_score,
            "regime_sigma_score": self.sigma_score,
            "regime_state": self.regime_state,
            "false_on_detected": self.false_on_detected,
            "assisted_on_detected": self.assisted_on_detected,
            "relaunch_dependency": self.relaunch_dependency,
            "hidden_loss": self.hidden_loss,
        }


def compute_regime_metrics(system: System) -> RegimeMetrics:
    stepped = step(system)
    total_in = stepped.pin_raw + stepped.paux + stepped.pstorage_out
    hidden_loss = min(1.0, stepped.L_total / max(total_in, 1e-12))
    relaunch_dep = min(1.0, stepped.paux / max(total_in, 1e-12))

    return RegimeMetrics(
        assisted_ratio=stepped.assisted_ratio,
        delta_g=stepped.delta_g,
        truth_score=stepped.truth_score,
        sigma_score=stepped.sigma_score,
        regime_state=stepped.state.value,
        false_on_detected=(stepped.state.value == "FALSE_ON"),
        assisted_on_detected=(stepped.state.value == "ASSISTED_ON"),
        relaunch_dependency=relaunch_dep,
        hidden_loss=hidden_loss,
    )
