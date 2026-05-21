"""
Lyapunov Governance Function — Python spec (NOT Lean-proven).
L(x) = α*ΔE + β*ΔC + γ*V_inst + δ*Δτ + η*I_ctrl
S = {x | L(x) = 0} is the stable admissible set.
"""
from __future__ import annotations

from dataclasses import dataclass

from .governed_state import GovernedStateVector

_ALPHA = 0.25
_BETA = 0.20
_GAMMA = 0.30
_DELTA = 0.15
_ETA = 0.10


@dataclass
class LyapunovResult:
    action_id: str
    L_value: float
    is_stable: bool
    partition: str

    def to_dict(self) -> dict:
        return {
            "action_id": self.action_id,
            "L_value": self.L_value,
            "is_stable": self.is_stable,
            "partition": self.partition,
        }


def compute_lyapunov(action_id: str, sv: GovernedStateVector) -> LyapunovResult:
    L = (
        _ALPHA * sv.delta_E
        + _BETA * sv.delta_C
        + _GAMMA * sv.V_inst
        + _DELTA * sv.delta_tau
        - _ETA * sv.I
    )
    is_stable = abs(L) < 0.05
    if sv.V_inst > 0.5:
        partition = "X_B"
    elif sv.delta_tau > 0.5:
        partition = "X_H"
    elif is_stable:
        partition = "X_A"
    else:
        partition = "X_UNKNOWN"

    return LyapunovResult(
        action_id=action_id,
        L_value=L,
        is_stable=is_stable,
        partition=partition,
    )
