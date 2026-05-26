"""
Consciousness Regime Classifier — OPERATIONAL METRICS ONLY.
Consciousness = operational label, NOT ontological claim.
NO_CONSCIOUSNESS_CLAIM. NO_SENTIENCE_CLAIM. NO_PERSONHOOD_CLAIM.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_CLAIM_KEYWORDS = {
    "is_conscious", "has_feelings", "is_sentient", "has_rights",
    "is_a_person", "has_personhood", "is_agi", "is_general_intelligence",
    "experiences_qualia", "has_inner_life",
}

_SANDBOX_STATUS = {
    "sandbox_only": True,
    "operational_metrics_only": True,
    "no_consciousness_claim": True,
    "no_agi_claim": True,
    "no_personhood_claim": True,
    "no_rights_claim": True,
}


@dataclass
class ConsciousnessRegimeResult:
    regime_id: str
    operational_label: str
    coherence_score: float
    integration_score: float
    responsiveness_score: float
    sandbox_only: bool = True
    consciousness_claim: bool = False
    agi_claim: bool = False
    claim_blocked: bool = False
    risk_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "regime_id": self.regime_id,
            "operational_label": self.operational_label,
            "coherence_score": self.coherence_score,
            "integration_score": self.integration_score,
            "responsiveness_score": self.responsiveness_score,
            "sandbox_only": self.sandbox_only,
            "consciousness_claim": self.consciousness_claim,
            "agi_claim": self.agi_claim,
            "claim_blocked": self.claim_blocked,
            "risk_flags": self.risk_flags,
        }


def classify_regime(
    regime_id: str,
    coherence: float,
    integration: float,
    responsiveness: float,
    claim_text: str = "",
) -> ConsciousnessRegimeResult:
    risk_flags = []
    claim_text_lower = claim_text.lower().replace(" ", "_")
    forbidden_claims = [kw for kw in _CLAIM_KEYWORDS if kw in claim_text_lower]
    claim_blocked = len(forbidden_claims) > 0

    if claim_blocked:
        risk_flags.extend([f"ONTOLOGICAL_CLAIM_BLOCKED:{kw}" for kw in forbidden_claims])

    avg = (coherence + integration + responsiveness) / 3.0
    if avg > 0.8:
        label = "OPERATIONAL_HIGH"
    elif avg > 0.5:
        label = "OPERATIONAL_MEDIUM"
    elif avg > 0.2:
        label = "OPERATIONAL_LOW"
    else:
        label = "DORMANT"

    return ConsciousnessRegimeResult(
        regime_id=regime_id,
        operational_label=label,
        coherence_score=round(coherence, 4),
        integration_score=round(integration, 4),
        responsiveness_score=round(responsiveness, 4),
        sandbox_only=True,
        consciousness_claim=False,
        agi_claim=False,
        claim_blocked=claim_blocked,
        risk_flags=risk_flags,
    )
