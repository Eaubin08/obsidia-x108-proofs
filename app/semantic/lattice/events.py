"""Event identity primitives for the semantic lattice V0.

EventRef separates a predicate's meaning from an occurrence/event identity.
It is descriptive and frame-local only: no parser wiring, no memory identity,
no receipt identity, and no authority or proof semantics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

EVENT_ID_SCOPE = "frame_local"


class EventKind(str, Enum):
    ACTION = "ACTION"
    STATE = "STATE"
    CHANGE = "CHANGE"
    OBSERVATION = "OBSERVATION"
    KNOWLEDGE_ACQUISITION = "KNOWLEDGE_ACQUISITION"
    REPORT = "REPORT"
    BELIEF = "BELIEF"


class EventRelationKind(str, Enum):
    ABOUT = "ABOUT"
    LEARNS_ABOUT = "LEARNS_ABOUT"
    OBSERVES = "OBSERVES"
    REPORTS_ABOUT = "REPORTS_ABOUT"
    BELIEVES_ABOUT = "BELIEVES_ABOUT"


@dataclass(frozen=True)
class EventRef:
    """Frame-local occurrence identity referencing a PredicateUnit id.

    `predicate_ref` is a reference, not a copy of the predicate payload. Future
    stages may attach temporal/epistemic/governance flows to `event_id`.
    """

    event_id: str
    predicate_ref: str
    event_kind: EventKind | str
    actor_ref: str | None = None
    object_refs: tuple[str, ...] = ()
    source_frame: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    confidence: Mapping[str, Any] = field(default_factory=dict)
    status: str = "asserted"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.event_id:
            raise ValueError("event_id is required")
        if not self.predicate_ref:
            raise ValueError("predicate_ref is required")
        kind = self.event_kind if isinstance(self.event_kind, EventKind) else EventKind(str(self.event_kind))
        metadata = dict(self.metadata)
        metadata.setdefault("event_id_scope", EVENT_ID_SCOPE)
        object.__setattr__(self, "event_kind", kind)
        object.__setattr__(self, "object_refs", tuple(self.object_refs))
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))
        object.__setattr__(self, "confidence", MappingProxyType(dict(self.confidence)))
        object.__setattr__(self, "metadata", MappingProxyType(metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "predicate_ref": self.predicate_ref,
            "event_kind": self.event_kind.value,
            "actor_ref": self.actor_ref,
            "object_refs": list(self.object_refs),
            "source_frame": self.source_frame,
            "provenance": dict(self.provenance),
            "confidence": dict(self.confidence),
            "status": self.status,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class EventReferenceRelation:
    """Typed relation between two EventRef ids.

    Relations point to event ids only; they never embed or duplicate the target
    event payload and do not validate truth, evidence, or authority.
    """

    relation_kind: EventRelationKind | str
    source_event: str
    target_event: str
    provenance: Mapping[str, Any] = field(default_factory=dict)
    confidence: Mapping[str, Any] = field(default_factory=dict)
    status: str = "asserted"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source_event:
            raise ValueError("source_event is required")
        if not self.target_event:
            raise ValueError("target_event is required")
        kind = self.relation_kind if isinstance(self.relation_kind, EventRelationKind) else EventRelationKind(str(self.relation_kind))
        object.__setattr__(self, "relation_kind", kind)
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))
        object.__setattr__(self, "confidence", MappingProxyType(dict(self.confidence)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "relation_kind": self.relation_kind.value,
            "source_event": self.source_event,
            "target_event": self.target_event,
            "provenance": dict(self.provenance),
            "confidence": dict(self.confidence),
            "status": self.status,
            "metadata": dict(self.metadata),
        }