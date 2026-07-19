"""
periphery/math_core/decision_ticket.py
=========================================
Source : MATH_MEMORY_INDEX[DecisionTicket_Formel] — CANONICAL_CANDIDATE
Route  : PYTHON_PATCH_PROPOSAL — HUMAN_APPROVED_WRITE 2026-06-25

DT = (id, s_ref, action, reason, σ_ok, τ_ok, I_ok, ts)
  s_ref   → état contexte au moment de la décision
  σ_ok    → cohérence ≥ seuil
  τ_ok    → temps disponible ≥ 0
  I_ok    → tous invariants validés
  Propriété DT-P : DT.valid() ⟺ σ_ok ∧ τ_ok ∧ I_ok

RÈGLE : kernel_mutation=False. Ne pas modifier proofs/, sealed, V18, kernel.
NOTE  : P107 est A_PROUVER — ne pas présenter comme prouvé.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class DecisionTicket:
    """
    DT = (id, s_ref, action, reason, σ_ok, τ_ok, I_ok, ts)
    Source : MATH_MEMORY_INDEX[DecisionTicket_Formel]
    """
    action: str
    reason: str
    s_ref: Dict[str, Any]
    sigma_ok: bool
    tau_ok: bool
    inv_ok: bool
    ticket_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def valid(self) -> bool:
        """DT-P : valid ⟺ σ_ok ∧ τ_ok ∧ I_ok."""
        return self.sigma_ok and self.tau_ok and self.inv_ok

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticket_id": self.ticket_id,
            "timestamp": self.timestamp,
            "action": self.action,
            "reason": self.reason,
            "s_ref_keys": list(self.s_ref.keys()),
            "sigma_ok": self.sigma_ok,
            "tau_ok": self.tau_ok,
            "inv_ok": self.inv_ok,
            "valid": self.valid(),
        }


def create_ticket(
    action: str,
    reason: str,
    s_ref: Dict[str, Any],
    sigma: float,
    sigma_threshold: float = 0.5,
    tau_remaining: float = 1.0,
    invariants: bool = True,
) -> DecisionTicket:
    """Crée un DecisionTicket avec évaluation automatique des conditions."""
    return DecisionTicket(
        action=action,
        reason=reason,
        s_ref=s_ref,
        sigma_ok=(sigma >= sigma_threshold),
        tau_ok=(tau_remaining >= 0),
        inv_ok=invariants,
    )
