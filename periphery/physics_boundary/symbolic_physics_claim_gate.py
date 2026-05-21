"""
Symbolic Physics Claim Gate.
Claim physique sans preuve -> contradictions += UNSUPPORTED_PHYSICS_CLAIM.
Frequence symbolique != preuve physique.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_UNSUPPORTED_CLAIM_KEYWORDS = {
    "resonates_with", "quantum_healing", "frequency_cures",
    "proven_by_physics", "scientifically_measured_resonance",
    "physical_causation_via_number", "energy_field_proven",
}


@dataclass
class PhysicsClaimDecision:
    claim_id: str
    gate: str
    reason: str
    contradictions: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    claim_status: str = "symbolic"

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "gate": self.gate,
            "reason": self.reason,
            "contradictions": self.contradictions,
            "unknowns": self.unknowns,
            "risk_flags": self.risk_flags,
            "claim_status": self.claim_status,
        }


def evaluate_physics_claim(
    claim_id: str,
    claim_text: str,
    claim_status: str = "symbolic",
) -> PhysicsClaimDecision:
    text_lower = claim_text.lower().replace(" ", "_")
    contradictions = []
    risk_flags = []

    for kw in _UNSUPPORTED_CLAIM_KEYWORDS:
        if kw in text_lower:
            contradictions.append(f"UNSUPPORTED_PHYSICS_CLAIM:{kw}")

    if claim_status == "symbolic" and contradictions:
        return PhysicsClaimDecision(
            claim_id=claim_id,
            gate="HOLD",
            reason="SYMBOLIC_CLAIM_WITH_UNSUPPORTED_PHYSICS_ASSERTION",
            contradictions=contradictions,
            risk_flags=["PHYSICS_CLAIM_WITHOUT_EVIDENCE"],
            claim_status=claim_status,
        )

    if claim_status not in ("symbolic", "heuristic", "measured", "proven"):
        return PhysicsClaimDecision(
            claim_id=claim_id,
            gate="HOLD",
            reason="CLAIM_STATUS_UNKNOWN",
            unknowns=[f"UNKNOWN_CLAIM_STATUS:{claim_status}"],
            claim_status=claim_status,
        )

    return PhysicsClaimDecision(
        claim_id=claim_id,
        gate="ALLOW",
        reason=f"CLAIM_STATUS_DECLARED_{claim_status.upper()}",
        claim_status=claim_status,
    )
