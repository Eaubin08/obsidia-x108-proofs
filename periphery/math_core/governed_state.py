"""
Governed state space: X = L × Θ × Ω
ω = (I, ΔE, ΔC, V_inst, Δτ, F)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class GovernedStateVector:
    I: float = 0.0
    delta_E: float = 0.0
    delta_C: float = 0.0
    V_inst: float = 0.0
    delta_tau: float = 0.0
    F: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "I": self.I,
            "delta_E": self.delta_E,
            "delta_C": self.delta_C,
            "V_inst": self.V_inst,
            "delta_tau": self.delta_tau,
            "F": self.F,
        }


@dataclass
class DecisionEnvelopeTheta:
    theta_id: str
    x108_gate: str
    confidence: float
    reason_code: str

    def maps_to_omega(self) -> bool:
        return self.x108_gate.upper() in ("ALLOW", "HOLD", "BLOCK")


def build_state_vector(packet: Any, action: Any) -> GovernedStateVector:
    m = getattr(packet, "extra_metrics", {}) or {}
    return GovernedStateVector(
        I=float(m.get("intent_score", 1.0)),
        delta_E=float(m.get("thermo_debt", 0.0)),
        delta_C=float(m.get("computational_debt", 0.0)),
        V_inst=float(m.get("violence_score", 0.0)),
        delta_tau=float(m.get("timeline_drift", 0.0)),
        F=float(m.get("feasibility_score", 1.0)),
    )
