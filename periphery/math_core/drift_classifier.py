"""
periphery/math_core/drift_classifier.py
==========================================
Source : MATH_MEMORY_INDEX[Classifieur_Derive] — CANONICAL_CANDIDATE
Route  : PYTHON_PATCH_PROPOSAL — HUMAN_APPROVED_WRITE 2026-06-25

Classification du niveau de dérive :
  δ(s,s') = || J(s') - J(s) ||_Ω
  Seuils : δ₁ = 0.15 (ALERT), δ₂ = 0.40 (BLOCK), δ₃ = 0.70 (CRISIS)
  Classe : STABLE | ALERT | BLOCK | CRISIS

Propriété D1 : STABLE ⟺ δ < δ₁
Propriété D2 : BLOCK ou CRISIS ⇒ pas de décision autorisée
Propriété D3 : CRISIS ⟺ δ ≥ δ₃

RÈGLE : kernel_mutation=False. Ne pas modifier proofs/, sealed, V18, kernel.
NOTE  : P107 est A_PROUVER — ne pas présenter comme prouvé.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Sequence


DELTA_1 = 0.15  # seuil ALERT
DELTA_2 = 0.40  # seuil BLOCK
DELTA_3 = 0.70  # seuil CRISIS


class DriftClass(str, Enum):
    STABLE = "STABLE"
    ALERT  = "ALERT"
    BLOCK  = "BLOCK"
    CRISIS = "CRISIS"


def classify_drift(delta: float) -> DriftClass:
    """
    Source : MATH_MEMORY_INDEX[Classifieur_Derive]
    D1 : STABLE ⟺ δ < δ₁
    D2 : BLOCK | CRISIS ⇒ décision interdite
    D3 : CRISIS ⟺ δ ≥ δ₃
    """
    if delta >= DELTA_3:
        return DriftClass.CRISIS
    if delta >= DELTA_2:
        return DriftClass.BLOCK
    if delta >= DELTA_1:
        return DriftClass.ALERT
    return DriftClass.STABLE


def decision_allowed(drift: DriftClass) -> bool:
    """D2 : BLOCK | CRISIS ⇒ False."""
    return drift not in (DriftClass.BLOCK, DriftClass.CRISIS)


def omega_distance(omega_a: Sequence[float], omega_b: Sequence[float]) -> float:
    """δ(s,s') = ||J(s') - J(s)||_Ω — norme L2 dans Ω."""
    if len(omega_a) != len(omega_b):
        raise ValueError("Les vecteurs Ω doivent avoir la même dimension.")
    return float(sum((b - a) ** 2 for a, b in zip(omega_a, omega_b)) ** 0.5)


@dataclass
class DriftReport:
    delta: float
    drift_class: DriftClass
    decision_allowed: bool

    @classmethod
    def compute(
        cls,
        omega_prev: Sequence[float],
        omega_curr: Sequence[float],
    ) -> "DriftReport":
        delta = omega_distance(omega_prev, omega_curr)
        dc = classify_drift(delta)
        return cls(
            delta=delta,
            drift_class=dc,
            decision_allowed=decision_allowed(dc),
        )

    def to_dict(self) -> dict:
        return {
            "delta": self.delta,
            "drift_class": self.drift_class.value,
            "decision_allowed": self.decision_allowed,
            "thresholds": {"delta_1": DELTA_1, "delta_2": DELTA_2, "delta_3": DELTA_3},
        }
