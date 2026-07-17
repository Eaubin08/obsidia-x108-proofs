"""
periphery/math_core/obsidia_system.py
========================================
Source : MATH_MEMORY_INDEX[Quintuplet_Formel_O] — CANONICAL_CANDIDATE
Route  : PYTHON_PATCH_PROPOSAL — HUMAN_APPROVED_WRITE 2026-06-25

O = (S, Φ, I, τ, L) — quintuplet formel du système Obsidia.
  S  = espace des états
  Φ  = opérateur de transition (graphe de sens)
  I  = ensemble des invariants permanents
  τ  = horloge logique (timestamp logique discret)
  L  = fonction de Lyapunov candidate (5 termes — P107 À_PROUVER)

Condition de gouvernance : ∀s ∈ S, I(s) = True ⇒ Φ(s) défini.
Condition de stabilité   : L(Φ(s)) ≤ L(s) — À_PROUVER (P107).

RÈGLE : kernel_mutation=False. Ne pas modifier proofs/, sealed, V18, kernel.
NOTE  : P107 (L(Φ(s))≤L(s)) est A_PROUVER — ne pas présenter comme prouvé.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ObsidiaState:
    """
    s ∈ S — état du système Obsidia.
    Source : MATH_MEMORY_INDEX[Quintuplet_Formel_O]
    """
    coherence: float = 1.0
    invariants: Dict[str, bool] = field(default_factory=dict)
    tau: int = 0
    E_in: float = 0.0
    E_out: float = 0.0
    control_flag: str = "OK"
    history: List[str] = field(default_factory=list)

    def all_invariants_ok(self) -> bool:
        return all(self.invariants.values()) if self.invariants else True

    def lyapunov(
        self,
        w_coh: float = 0.25,
        w_inv: float = 0.30,
        w_energy: float = 0.20,
        w_ctrl: float = 0.15,
        w_tau: float = 0.10,
        beta: float = 0.1,
        tau_ref: int = 100,
    ) -> float:
        """
        L(s) = w_coh·(1-σ) + w_inv·V_inv + w_energy·|ΔE| + w_ctrl·F + w_tau·τ_norm
        5 termes — MATH_MEMORY_INDEX[Lyapunov_Complet_5termes]
        P107 : L(Φ(s)) ≤ L(s) — À_PROUVER, ne pas présenter comme prouvé.
        """
        sigma = self.coherence
        V_inv = 0.0 if self.all_invariants_ok() else 1.0
        delta_E = abs(self.E_out - self.E_in)
        F = 0.0 if self.control_flag == "OK" else 1.0
        tau_norm = min(1.0, self.tau / max(1, tau_ref)) * beta
        return (
            w_coh * (1.0 - sigma)
            + w_inv * V_inv
            + w_energy * delta_E
            + w_ctrl * F
            + w_tau * tau_norm
        )


@dataclass
class ObsidiaSystem:
    """
    O = (S, Φ, I, τ, L) — système formel.
    Source : MATH_MEMORY_INDEX[Quintuplet_Formel_O]
    """
    state: ObsidiaState = field(default_factory=ObsidiaState)
    invariant_names: List[str] = field(default_factory=list)

    def verify_invariants(self) -> bool:
        """∀s ∈ S, I(s) = True ⇒ Φ(s) défini."""
        return self.state.all_invariants_ok()

    def transition(self, phi: Callable[[ObsidiaState], ObsidiaState]) -> None:
        """
        Applique Φ au state.
        P107 (L(Φ(s)) ≤ L(s)) est une propriété À_PROUVER — non garantie ici.
        """
        if not self.verify_invariants():
            raise RuntimeError("Transition bloquée : invariants non satisfaits.")
        new_state = phi(self.state)
        self.state = new_state
        self.state.tau += 1

    def report(self) -> Dict[str, Any]:
        return {
            "tau": self.state.tau,
            "coherence": self.state.coherence,
            "invariants_ok": self.state.all_invariants_ok(),
            "lyapunov": self.state.lyapunov(),
            "control_flag": self.state.control_flag,
            "p107_status": "A_PROUVER",
        }
