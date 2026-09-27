"""Typed target references for event/proposition linking.

V0 deliberately does not perform broad event anaphora. It only provides an
immutable record that can preserve explicit parser-backed targets and unresolved
references without guessing nearest events.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class TargetKind(str, Enum):
    PROPOSITION_TARGET = "PROPOSITION_TARGET"
    EVENT_TARGET = "EVENT_TARGET"
    ENTITY_TARGET = "ENTITY_TARGET"
    UNKNOWN_TARGET = "UNKNOWN_TARGET"


class ResolutionStatus(str, Enum):
    RESOLVED_EXPLICIT = "RESOLVED_EXPLICIT"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class EventTargetReference:
    """A typed reference from a meta-event to a target identity.

    Target semantics and target identity stay separate: a resolved target may
    carry a predicate id, an event id, both, or neither when unresolved.
    """

    source_event: str
    source_predicate: str
    target_kind: TargetKind | str
    resolution_status: ResolutionStatus | str
    target_predicate: str | None = None
    target_event: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    confidence: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source_event:
            raise ValueError("source_event is required")
        if not self.source_predicate:
            raise ValueError("source_predicate is required")
        kind = self.target_kind if isinstance(self.target_kind, TargetKind) else TargetKind(str(self.target_kind))
        status = self.resolution_status if isinstance(self.resolution_status, ResolutionStatus) else ResolutionStatus(str(self.resolution_status))
        object.__setattr__(self, "target_kind", kind)
        object.__setattr__(self, "resolution_status", status)
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))
        object.__setattr__(self, "confidence", MappingProxyType(dict(self.confidence)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_event": self.source_event,
            "source_predicate": self.source_predicate,
            "target_kind": self.target_kind.value,
            "resolution_status": self.resolution_status.value,
            "target_predicate": self.target_predicate,
            "target_event": self.target_event,
            "provenance": dict(self.provenance),
            "confidence": dict(self.confidence),
            "metadata": dict(self.metadata),
        }
