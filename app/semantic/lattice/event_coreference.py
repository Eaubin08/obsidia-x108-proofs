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
    RESOLVED_STRUCTURAL = "RESOLVED_STRUCTURAL"
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
        _check_target_consistency(kind, status, self.target_predicate, self.target_event)
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


_RESOLVED = frozenset({ResolutionStatus.RESOLVED_EXPLICIT, ResolutionStatus.RESOLVED_STRUCTURAL})


def _check_target_consistency(
    kind: TargetKind,
    status: ResolutionStatus,
    target_predicate: str | None,
    target_event: str | None,
) -> None:
    """Reject target records that contradict themselves (no guessing, no repair)."""
    if status not in _RESOLVED and target_event is not None:
        raise ValueError(f"{status.value} reference cannot carry a target_event")
    if kind is TargetKind.EVENT_TARGET and status in _RESOLVED and not target_event:
        raise ValueError("resolved EVENT_TARGET requires a target_event")
    if kind is TargetKind.EVENT_TARGET and status not in _RESOLVED:
        raise ValueError("EVENT_TARGET must be resolved; use UNKNOWN_TARGET when unresolved")
    if kind is TargetKind.UNKNOWN_TARGET and (status in _RESOLVED or target_predicate or target_event):
        raise ValueError("UNKNOWN_TARGET carries no target and is never resolved")
