"""F12 Situated World Dynamics V0.

Typed time, spatial-frame and N->N+1 trajectory contracts for MMonde.
Representation only: no domain law, physical truth promotion, cognition or authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RelationStatusV0(str, Enum):
    TEMPORAL = "TEMPORAL"
    CORRELATED = "CORRELATED"
    DERIVED = "DERIVED"
    CAUSAL_ASSERTED = "CAUSAL_ASSERTED"
    CAUSAL_PROVEN = "CAUSAL_PROVEN"
    UNKNOWN = "UNKNOWN"


class ContinuityStatusV0(str, Enum):
    CONTINUOUS = "CONTINUOUS"
    DRIFT = "DRIFT"
    RUPTURE = "RUPTURE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class TimeEnvelopeV0:
    observed_at: str
    received_at: str | None = None
    processed_at: str | None = None
    decided_at: str | None = None
    executed_at: str | None = None
    verified_at: str | None = None
    valid_from: str | None = None
    valid_until: str | None = None

    def __post_init__(self) -> None:
        if not self.observed_at:
            raise ValueError("observed_at is required")
        # Missing clocks remain missing. This contract never synthesizes them.


@dataclass(frozen=True)
class SpatialFrameRefV0:
    frame_ref: str
    parent_frame_ref: str | None = None
    transform_refs: tuple[str, ...] = ()
    frame_unknown: bool = False

    def __post_init__(self) -> None:
        if not self.frame_ref:
            raise ValueError("frame_ref is required")
        if self.frame_unknown and self.parent_frame_ref is not None:
            raise ValueError("unknown frame cannot claim a parent frame")


@dataclass(frozen=True)
class TypedRelationV0:
    relation_id: str
    subject_ref: str
    object_ref: str
    status: RelationStatusV0 = RelationStatusV0.UNKNOWN
    evidence_refs: tuple[str, ...] = ()
    provenance_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.relation_id or not self.subject_ref or not self.object_ref:
            raise ValueError("typed relation requires id, subject and object")
        if self.status == RelationStatusV0.CAUSAL_PROVEN and not self.evidence_refs:
            raise ValueError("CAUSAL_PROVEN requires evidence_refs")


@dataclass(frozen=True)
class TransitionV0:
    transition_id: str
    entity_ref: str
    from_state_ref: str
    to_state_ref: str
    time: TimeEnvelopeV0
    spatial_frame: SpatialFrameRefV0 | None = None
    relation_refs: tuple[str, ...] = ()
    continuity: ContinuityStatusV0 = ContinuityStatusV0.UNKNOWN
    uncertainty: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    provenance_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    readonly: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not all((self.transition_id, self.entity_ref, self.from_state_ref, self.to_state_ref)):
            raise ValueError("transition requires identity, entity and state refs")
        if not self.readonly:
            raise ValueError("Situated World Dynamics is readonly representation")
        if self.decision_authority != "KX108_ONLY":
            raise ValueError("decision authority must remain KX108_ONLY")
        if self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("Situated World Dynamics cannot decide or act")


@dataclass(frozen=True)
class TrajectoryV0:
    trajectory_id: str
    entity_ref: str
    transitions: tuple[TransitionV0, ...]
    continuity: ContinuityStatusV0 = ContinuityStatusV0.UNKNOWN
    unknowns: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    readonly: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.trajectory_id or not self.entity_ref:
            raise ValueError("trajectory requires identity and entity")
        if not self.transitions:
            raise ValueError("trajectory requires at least one transition")
        if any(t.entity_ref != self.entity_ref for t in self.transitions):
            raise ValueError("all transitions must refer to the same entity")
        for left, right in zip(self.transitions, self.transitions[1:]):
            if left.to_state_ref != right.from_state_ref:
                raise ValueError("trajectory state chain is discontinuous")
        if not self.readonly:
            raise ValueError("Situated World Dynamics is readonly representation")
        if self.decision_authority != "KX108_ONLY":
            raise ValueError("decision authority must remain KX108_ONLY")
        if self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("Situated World Dynamics cannot decide or act")
