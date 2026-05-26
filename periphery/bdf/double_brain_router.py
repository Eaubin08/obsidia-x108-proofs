"""
Double Brain Router — routes between analytical (System 2) and intuitive (System 1) generation.
BDF routes generation mode, never acts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DoubleBrainRoute:
    route_id: str
    mode: str
    system_1_weight: float
    system_2_weight: float
    rationale: str
    advisory_only: bool = True
    emits_act: bool = False
    emits_verdict: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "route_id": self.route_id,
            "mode": self.mode,
            "system_1_weight": self.system_1_weight,
            "system_2_weight": self.system_2_weight,
            "rationale": self.rationale,
            "advisory_only": self.advisory_only,
            "emits_act": self.emits_act,
            "emits_verdict": self.emits_verdict,
        }


def route_double_brain(
    route_id: str,
    complexity: float = 0.5,
    urgency: float = 0.5,
    uncertainty: float = 0.5,
) -> DoubleBrainRoute:
    if complexity > 0.7 or uncertainty > 0.7:
        mode = "ANALYTICAL"
        s1, s2 = 0.2, 0.8
    elif urgency > 0.8:
        mode = "INTUITIVE"
        s1, s2 = 0.8, 0.2
    else:
        mode = "BALANCED"
        s1, s2 = 0.5, 0.5

    return DoubleBrainRoute(
        route_id=route_id,
        mode=mode,
        system_1_weight=s1,
        system_2_weight=s2,
        rationale=f"BDF_ROUTE:{mode}_c={complexity:.2f}_u={uncertainty:.2f}",
        advisory_only=True,
        emits_act=False,
        emits_verdict=False,
    )
