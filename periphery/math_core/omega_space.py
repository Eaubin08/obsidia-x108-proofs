"""
periphery/math_core/omega_space.py
====================================
Source : MATH_MEMORY_INDEX[Espace_Invariants_Omega] — CANONICAL_CANDIDATE
Route  : PYTHON_PATCH_PROPOSAL — HUMAN_APPROVED_WRITE 2026-06-25

Ω = espace des invariants observés.
ω = (I, ΔE, ΔC, Vinst, Δτ, F) ∈ {0,1}^k × ℝ≥0⁴ × {0,1}
J : S → Ω  (application d'observation)
ℓ(ω) = αE·ΔE + αC·ΔC + αV·Vinst + ατ·Δτ + αF·F
Ω₀ = {(1,0,0,0,0,0)} = attracteur stable

RÈGLE : kernel_mutation=False. Ne pas modifier proofs/, sealed, V18, kernel.
NOTE  : P107 (L(Phi(s))<=L(s)) est A_PROUVER — ne pas présenter comme prouvé.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class OmegaState:
    """
    ω ∈ Ω — état dans l'espace des invariants.
    Source : MATH_MEMORY_INDEX[Espace_Invariants_Omega]
    """
    inv: List[bool]     # vecteur d'invariants I₁,...,Iₖ
    dE: float           # ΔE = max(0, E_out - E_in)
    dC: float           # ΔC = max(0, C* - coh(s)), C* = 0.6
    Vinst: float        # instabilité instantanée
    dTau: float         # Δτ = max(0, τ - elapsed)
    F: bool             # flag contrôle (True si control_flag ≠ OK)

    def ell(
        self,
        alphaE: float = 0.25,
        alphaC: float = 0.20,
        alphaV: float = 0.30,
        alphaTau: float = 0.15,
        alphaF: float = 0.10,
    ) -> float:
        """ℓ(ω) = instabilité locale dans Ω."""
        return (
            alphaE * self.dE
            + alphaC * self.dC
            + alphaV * self.Vinst
            + alphaTau * self.dTau
            + alphaF * (1.0 if self.F else 0.0)
        )

    def is_attractor(self) -> bool:
        """Ω₀ : tous invariants True + toutes métriques = 0."""
        return (
            all(self.inv)
            and self.dE == 0.0
            and self.dC == 0.0
            and self.Vinst == 0.0
            and self.dTau == 0.0
            and not self.F
        )

    def classify(self) -> str:
        """Stratification gouvernée : BLOCK / HOLD / ALLOW."""
        if self.dE > 0 or self.Vinst > 0 or not all(self.inv):
            return "BLOCK"
        if self.dTau > 0 or self.dC > 0:
            return "HOLD"
        return "ALLOW"


def project_state_to_omega(state: Any, C_star: float = 0.6) -> OmegaState:
    """
    J : StateCore → Ω
    Application d'observation — source : MATH_MEMORY_INDEX[Espace_Invariants_Omega]
    """
    return OmegaState(
        inv=[getattr(state, "invariants_ok", True)],
        dE=max(0.0, getattr(state, "E_out", 0.0) - getattr(state, "E_in", 0.0)),
        dC=max(0.0, C_star - getattr(state, "coherence", 1.0)),
        Vinst=getattr(state, "Vinst", 0.0),
        dTau=max(0.0, getattr(state, "tau", 0) - getattr(state, "elapsed", 0)),
        F=(getattr(state, "control_flag", "OK") != "OK"),
    )


OMEGA_0 = OmegaState(inv=[True], dE=0.0, dC=0.0, Vinst=0.0, dTau=0.0, F=False)
