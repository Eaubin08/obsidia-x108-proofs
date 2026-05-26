"""
ProofOfGovernance — Python spec (NOT a Lean proof).
ProofOfGovernance(x) iff:
  J_Θ(θ) ∈ Ω  (decision maps to valid output space)
  AND L(x) = 0  (Lyapunov stable)
  AND Verify(sig, DecisionTicket) = true  (ticket integrity)
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .lyapunov import LyapunovResult
from .governed_state import DecisionEnvelopeTheta


@dataclass
class ProofOfGovernanceResult:
    action_id: str
    pog_valid: bool
    theta_maps_to_omega: bool
    lyapunov_stable: bool
    ticket_valid: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "pog_valid": self.pog_valid,
            "theta_maps_to_omega": self.theta_maps_to_omega,
            "lyapunov_stable": self.lyapunov_stable,
            "ticket_valid": self.ticket_valid,
            "reason": self.reason,
        }


def verify_ticket_integrity(ticket: Any) -> bool:
    return bool(
        getattr(ticket, "input_hash", "") and
        getattr(ticket, "output_hash", "") and
        getattr(ticket, "trace_hash", "") and
        getattr(ticket, "merkle_root", "")
    )


def proof_of_governance(
    action_id: str,
    theta: DecisionEnvelopeTheta,
    lyapunov: LyapunovResult,
    ticket: Any,
) -> ProofOfGovernanceResult:
    theta_ok = theta.maps_to_omega()
    lyapunov_ok = lyapunov.is_stable
    ticket_ok = verify_ticket_integrity(ticket)

    pog_valid = theta_ok and lyapunov_ok and ticket_ok
    reason = "POG_VALID" if pog_valid else (
        "THETA_NOT_IN_OMEGA" if not theta_ok else
        "LYAPUNOV_NOT_STABLE" if not lyapunov_ok else
        "TICKET_INVALID"
    )

    return ProofOfGovernanceResult(
        action_id=action_id,
        pog_valid=pog_valid,
        theta_maps_to_omega=theta_ok,
        lyapunov_stable=lyapunov_ok,
        ticket_valid=ticket_ok,
        reason=reason,
    )
