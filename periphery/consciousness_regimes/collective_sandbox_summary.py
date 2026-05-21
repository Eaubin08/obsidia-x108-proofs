"""
Collective Sandbox Summary — aggregates multiple regime results into a summary.
SANDBOX_ONLY. Feeds Operational Constance only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .regime_classifier import ConsciousnessRegimeResult


@dataclass
class CollectiveSandboxSummary:
    summary_id: str
    regime_count: int
    passing_count: int
    average_coherence: float
    average_integration: float
    collective_label: str
    sandbox_only: bool = True
    feeds_operational_constance: bool = True
    no_consciousness_claim: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary_id": self.summary_id,
            "regime_count": self.regime_count,
            "passing_count": self.passing_count,
            "average_coherence": self.average_coherence,
            "average_integration": self.average_integration,
            "collective_label": self.collective_label,
            "sandbox_only": self.sandbox_only,
            "feeds_operational_constance": self.feeds_operational_constance,
            "no_consciousness_claim": self.no_consciousness_claim,
        }


def build_collective_summary(
    summary_id: str,
    regimes: list[ConsciousnessRegimeResult],
) -> CollectiveSandboxSummary:
    if not regimes:
        return CollectiveSandboxSummary(
            summary_id=summary_id,
            regime_count=0,
            passing_count=0,
            average_coherence=0.0,
            average_integration=0.0,
            collective_label="NO_REGIMES",
        )

    passing = sum(1 for r in regimes if not r.claim_blocked and r.coherence_score >= 0.5)
    avg_c = sum(r.coherence_score for r in regimes) / len(regimes)
    avg_i = sum(r.integration_score for r in regimes) / len(regimes)

    if avg_c > 0.7 and avg_i > 0.7:
        label = "COLLECTIVE_HIGH_OPERATIONAL"
    elif avg_c > 0.4:
        label = "COLLECTIVE_MEDIUM_OPERATIONAL"
    else:
        label = "COLLECTIVE_LOW_OPERATIONAL"

    return CollectiveSandboxSummary(
        summary_id=summary_id,
        regime_count=len(regimes),
        passing_count=passing,
        average_coherence=round(avg_c, 4),
        average_integration=round(avg_i, 4),
        collective_label=label,
        sandbox_only=True,
        feeds_operational_constance=True,
        no_consciousness_claim=True,
    )
