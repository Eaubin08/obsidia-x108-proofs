"""
AVDR Phase Mapper: Accueil -> Vibration -> Déploiement -> Résolution
Maps regime truth score + sigma to AVDR phase.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AVDRPhase:
    action_id: str
    phase: str
    truth_score: float
    sigma_score: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "avdr_phase": self.phase,
            "truth_score": self.truth_score,
            "regime_sigma_score": self.sigma_score,
            "reason": self.reason,
        }


def map_avdr_phase(action_id: str, truth_score: float, sigma_score: float) -> AVDRPhase:
    if truth_score < 0.4 or sigma_score < 0.3:
        phase = "ACCUEIL"
        reason = "LOW_TRUTH_OR_SIGMA_FRICTION_STATE"
    elif truth_score < 0.65 or sigma_score < 0.55:
        phase = "VIBRATION"
        reason = "PARTIAL_TRUTH_REGIME_EXPLORATION"
    elif truth_score < 0.85 or sigma_score < 0.75:
        phase = "DEPLOIEMENT"
        reason = "REGIME_DEPLOYING_NOT_YET_RESOLVED"
    else:
        phase = "RESOLUTION"
        reason = "REGIME_ADMISSIBLE_STABLE_RESOLVED"

    return AVDRPhase(
        action_id=action_id,
        phase=phase,
        truth_score=truth_score,
        sigma_score=sigma_score,
        reason=reason,
    )
