"""
HexaFlux Transition Mapper — maps 6-phase flux transitions.
Maps transitions, never authorizes. Advisory context only.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_PHASES = ["LATENT", "IGNITION", "EXPANSION", "STABILIZATION", "COMPRESSION", "DISSOLUTION"]

_TRANSITIONS = {
    ("LATENT", "IGNITION"): "ACTIVATION_TRIGGER",
    ("IGNITION", "EXPANSION"): "GROWTH_PHASE",
    ("EXPANSION", "STABILIZATION"): "PLATEAU_REACHED",
    ("STABILIZATION", "COMPRESSION"): "CONSOLIDATION",
    ("COMPRESSION", "DISSOLUTION"): "RELEASE_CYCLE",
    ("DISSOLUTION", "LATENT"): "RESET_TO_LATENT",
    ("STABILIZATION", "DISSOLUTION"): "BYPASS_COMPRESSION",
    ("EXPANSION", "DISSOLUTION"): "RAPID_COLLAPSE",
}


@dataclass
class HexaFluxTransition:
    transition_id: str
    from_phase: str
    to_phase: str
    transition_type: str
    is_valid: bool
    advisory_only: bool = True
    authorizes: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "from_phase": self.from_phase,
            "to_phase": self.to_phase,
            "transition_type": self.transition_type,
            "is_valid": self.is_valid,
            "advisory_only": self.advisory_only,
            "authorizes": self.authorizes,
        }


def map_hexaflux_transition(transition_id: str, from_phase: str, to_phase: str) -> HexaFluxTransition:
    transition_type = _TRANSITIONS.get((from_phase, to_phase), "UNKNOWN_TRANSITION")
    is_valid = (from_phase, to_phase) in _TRANSITIONS
    return HexaFluxTransition(
        transition_id=transition_id,
        from_phase=from_phase,
        to_phase=to_phase,
        transition_type=transition_type,
        is_valid=is_valid,
        advisory_only=True,
        authorizes=False,
    )
