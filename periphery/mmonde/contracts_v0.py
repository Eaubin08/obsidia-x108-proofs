"""MMonde V0 — minimal situated-world contracts.

Representation only. No cognition, memory ownership, domain law, or decision authority.
OBSERVATION != TRUTH. WORLD_STATE != MEMORY. TEMPORAL != CAUSAL_PROVEN.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class WorldObservationV0:
    observation_id: str
    observed_at: str
    source_refs: tuple[str, ...] = ()
    source_hashes: tuple[str, ...] = ()
    entity_ref: str | None = None
    state: dict[str, Any] = field(default_factory=dict)
    relations: tuple[dict[str, Any], ...] = ()
    space: dict[str, Any] = field(default_factory=dict)
    uncertainty: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    causal_status: str = "UNKNOWN"
    readonly: bool = True
    representation_only: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.observation_id:
            raise ValueError("observation_id is required")
        if not self.observed_at:
            raise ValueError("observed_at is required")
        if self.causal_status == "CAUSAL_PROVEN" and not self.evidence_refs:
            raise ValueError("CAUSAL_PROVEN requires evidence_refs")
        if not self.readonly or not self.representation_only:
            raise ValueError("MMonde V0 is readonly representation only")
        if self.decision_authority != "KX108_ONLY":
            raise ValueError("decision authority must remain KX108_ONLY")
        if self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("MMonde V0 cannot decide or act")


@dataclass(frozen=True)
class WorldStateV0:
    world_state_id: str
    valid_at: str
    observations: tuple[WorldObservationV0, ...]
    candidate_reality: bool = True
    unknowns: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()
    provenance_refs: tuple[str, ...] = ()
    readonly: bool = True
    memory_object: bool = False
    cognition_object: bool = False
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.world_state_id:
            raise ValueError("world_state_id is required")
        if not self.valid_at:
            raise ValueError("valid_at is required")
        if not self.observations:
            raise ValueError("WorldStateV0 requires at least one observation")
        if not self.readonly or self.memory_object or self.cognition_object:
            raise ValueError("WorldStateV0 must remain readonly and distinct from memory/cognition")
        if self.decision_authority != "KX108_ONLY":
            raise ValueError("decision authority must remain KX108_ONLY")
        if self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("MMonde V0 cannot decide or act")
