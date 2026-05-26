from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DebtBreakdown:
    action_id: str
    gross_value: float
    computational_debt: float
    energy_debt: float
    memory_debt: float
    thermo_debt: float
    oc_debt: float
    total_debt: float
    net_value: float
    assisted_ratio: float = 0.0
    delta_g: float = 1.0
    truth_score: float = 1.0
    regime_state: str = "ON"

    def is_admissible(self) -> bool:
        return (
            self.net_value > 0.0
            and self.truth_score >= 0.8
            and self.assisted_ratio < 0.5
            and self.regime_state not in ("FALSE_ON", "REJECTED", "DECAY")
        )


def compute_debt(action_candidate: Any, packet: Any) -> DebtBreakdown:
    m = packet.extra_metrics
    payload = getattr(action_candidate, "payload", {}) or {}

    gross_value = float(payload.get("gross_value", 0.0))
    computational_debt = float(m.get("computational_debt", 0.0))
    energy_debt = float(m.get("thermo_debt", 0.0))
    memory_debt = float(m.get("memory_debt", 0.0))
    thermo_debt = float(m.get("thermo_debt", 0.0))
    oc_debt = float(m.get("oc_debt", 0.0))

    total_debt = computational_debt + energy_debt + memory_debt + oc_debt
    net_value = max(0.0, gross_value - total_debt)

    assisted_ratio = float(m.get("assisted_ratio", 0.0))
    delta_g = float(m.get("delta_g", 1.0))
    truth_score = float(m.get("truth_score", 1.0))
    regime_state = str(m.get("regime_state", "ON"))

    return DebtBreakdown(
        action_id=action_candidate.action_id,
        gross_value=gross_value,
        computational_debt=computational_debt,
        energy_debt=energy_debt,
        memory_debt=memory_debt,
        thermo_debt=thermo_debt,
        oc_debt=oc_debt,
        total_debt=total_debt,
        net_value=net_value,
        assisted_ratio=assisted_ratio,
        delta_g=delta_g,
        truth_score=truth_score,
        regime_state=regime_state,
    )
