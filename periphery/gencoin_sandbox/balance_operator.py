"""
Balance Obsidienne: Peser -> Simplifier -> Réintégrer -> Statuer
B(x) = beta(x <-> psi_canonique) -> rho
Statuts: canonique / compatible / orbite / rejeté
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_W_UTILITY = 0.35
_W_COHERENCE = 0.25
_W_STABILITY = 0.20
_W_COST = -0.10
_W_RISK = -0.10


@dataclass
class BalanceResult:
    action_id: str
    balance_score: float
    status: str
    utility: float
    coherence: float
    stability: float
    cost: float
    risk: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "balance_score": self.balance_score,
            "status": self.status,
            "utility": self.utility,
            "coherence": self.coherence,
            "stability": self.stability,
            "cost": self.cost,
            "risk": self.risk,
        }


def compute_balance(
    action_id: str,
    utility: float,
    coherence: float,
    stability: float,
    cost: float,
    risk: float,
) -> BalanceResult:
    score = (
        _W_UTILITY * utility
        + _W_COHERENCE * coherence
        + _W_STABILITY * stability
        + _W_COST * cost
        + _W_RISK * risk
    )
    score = max(0.0, min(1.0, score))

    if score >= 0.80:
        status = "canonique"
    elif score >= 0.60:
        status = "compatible"
    elif score >= 0.40:
        status = "orbite"
    else:
        status = "rejeté"

    return BalanceResult(
        action_id=action_id,
        balance_score=score,
        status=status,
        utility=utility,
        coherence=coherence,
        stability=stability,
        cost=cost,
        risk=risk,
    )
