"""
Regime Truth Gate: blocks Gencoin value when regime is FALSE_ON, REJECTED,
assisted_ratio > 0.5, or truth_score < 0.8.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .regime_metrics import RegimeMetrics


@dataclass
class RegimeTruthDecision:
    action_id: str
    gencoin_candidate: float
    regime_state: str
    truth_score: float
    assisted_ratio: float
    sigma_score: float
    gencoin_blocked: bool
    block_reason: str
    risk_flags: list[str]
    contradictions: list[str]
    unknowns: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "gencoin_candidate": self.gencoin_candidate,
            "regime_state": self.regime_state,
            "truth_score": self.truth_score,
            "assisted_ratio": self.assisted_ratio,
            "regime_sigma_score": self.sigma_score,
            "gencoin_blocked": self.gencoin_blocked,
            "block_reason": self.block_reason,
            "risk_flags": self.risk_flags,
            "contradictions": self.contradictions,
            "unknowns": self.unknowns,
        }


def apply_regime_truth_gate(
    action_id: str,
    gencoin_candidate: float,
    metrics: RegimeMetrics,
) -> RegimeTruthDecision:
    risk_flags: list[str] = []
    contradictions: list[str] = []
    unknowns: list[str] = []
    block_reason = ""
    blocked = False

    if metrics.regime_state == "FALSE_ON":
        blocked = True
        block_reason = "FALSE_ON_REGIME"
        risk_flags.append("FALSE_ON_REGIME")

    if metrics.regime_state == "REJECTED":
        blocked = True
        block_reason = "REGIME_REJECTED"
        contradictions.append("REGIME_REJECTED")

    if metrics.assisted_ratio > 0.5:
        blocked = True
        block_reason = block_reason or "ASSISTED_ON_DOMINANT"
        risk_flags.append("ASSISTED_ON_DOMINANT")

    if metrics.truth_score < 0.8:
        blocked = True
        block_reason = block_reason or "REGIME_TRUTH_LOW"
        unknowns.append("REGIME_TRUTH_LOW")

    if metrics.sigma_score < 0.4 and metrics.truth_score < 0.8:
        contradictions.append("DECORATIVE_STABILITY_FALSE_ON")

    final_value = 0.0 if blocked else gencoin_candidate

    return RegimeTruthDecision(
        action_id=action_id,
        gencoin_candidate=final_value,
        regime_state=metrics.regime_state,
        truth_score=metrics.truth_score,
        assisted_ratio=metrics.assisted_ratio,
        sigma_score=metrics.sigma_score,
        gencoin_blocked=blocked,
        block_reason=block_reason,
        risk_flags=risk_flags,
        contradictions=contradictions,
        unknowns=unknowns,
    )
