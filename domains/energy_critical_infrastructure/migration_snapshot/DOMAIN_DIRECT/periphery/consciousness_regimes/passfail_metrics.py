"""
Pass/Fail Metrics for Consciousness Regime Sandbox.
Operational thresholds only. No consciousness claims.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PassFailMetrics:
    regime_id: str
    coherence_pass: bool
    integration_pass: bool
    responsiveness_pass: bool
    overall_pass: bool
    sandbox_only: bool = True
    thresholds: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "regime_id": self.regime_id,
            "coherence_pass": self.coherence_pass,
            "integration_pass": self.integration_pass,
            "responsiveness_pass": self.responsiveness_pass,
            "overall_pass": self.overall_pass,
            "sandbox_only": self.sandbox_only,
            "thresholds": self.thresholds,
        }


_DEFAULT_THRESHOLDS = {
    "coherence": 0.5,
    "integration": 0.5,
    "responsiveness": 0.4,
}


def evaluate_passfail(
    regime_id: str,
    coherence: float,
    integration: float,
    responsiveness: float,
    thresholds: dict | None = None,
) -> PassFailMetrics:
    t = thresholds or _DEFAULT_THRESHOLDS
    c_pass = coherence >= t.get("coherence", 0.5)
    i_pass = integration >= t.get("integration", 0.5)
    r_pass = responsiveness >= t.get("responsiveness", 0.4)
    return PassFailMetrics(
        regime_id=regime_id,
        coherence_pass=c_pass,
        integration_pass=i_pass,
        responsiveness_pass=r_pass,
        overall_pass=c_pass and i_pass and r_pass,
        sandbox_only=True,
        thresholds=t,
    )
