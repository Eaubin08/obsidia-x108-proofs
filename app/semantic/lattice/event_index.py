"""Immutable frame-local EventIndex (V0).

Joins the outputs of the existing event extractors into one read-only view:
predicate_ref -> at most one EventCandidate. It never mints event ids; it only
checks that the proposals it receives agree. Incompatible proposals, foreign
frames, unknown predicates and event-id collisions are recorded as explicit
conflicts and excluded -- the index never picks one proposal over another.
No global state, no memory, no authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from app.semantic.lattice.event_coreference import EventTargetReference, ResolutionStatus, TargetKind
from app.semantic.lattice.event_extraction import EventCandidate, _frame_ref, extract_event_candidates
from app.semantic.lattice.knowledge_event_extraction import discover_knowledge_events
from app.semantic.lattice.observation_event_extraction import discover_observation_events
from app.semantic.lattice.primitives import UtteranceFrame


@dataclass(frozen=True)
class EventIndexConflict:
    predicate_ref: str
    reason: str
    event_ids: tuple[str, ...] = ()
    event_kinds: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "predicate_ref": self.predicate_ref,
            "reason": self.reason,
            "event_ids": list(self.event_ids),
            "event_kinds": list(self.event_kinds),
        }


@dataclass(frozen=True)
class EventIndex:
    frame_ref: str
    by_predicate: Mapping[str, EventCandidate] = field(default_factory=dict)
    conflicts: tuple[EventIndexConflict, ...] = ()
    unit_order: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "by_predicate", MappingProxyType(dict(self.by_predicate)))
        object.__setattr__(self, "conflicts", tuple(self.conflicts))
        object.__setattr__(self, "unit_order", tuple(self.unit_order))
        by_event = {candidate.event_ref.event_id: candidate for candidate in self.by_predicate.values()}
        object.__setattr__(self, "_by_event_id", MappingProxyType(by_event))

    def event_for(self, predicate_ref: str) -> EventCandidate | None:
        return self.by_predicate.get(predicate_ref)

    def by_event_id(self, event_id: str) -> EventCandidate | None:
        return self._by_event_id.get(event_id)  # type: ignore[attr-defined]

    def events(self) -> tuple[EventCandidate, ...]:
        """Indexed events in frame unit order."""
        return tuple(self.by_predicate[p] for p in self.unit_order if p in self.by_predicate)

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame_ref": self.frame_ref,
            "events": [candidate.to_dict() for candidate in self.events()],
            "conflicts": [conflict.to_dict() for conflict in self.conflicts],
        }


def build_event_index(frame: UtteranceFrame, *candidate_groups: Iterable[EventCandidate]) -> EventIndex:
    frame_ref = _frame_ref(frame)
    unit_order = tuple(unit.id for unit in frame.units)
    known_units = set(unit_order)
    conflicts: list[EventIndexConflict] = []
    proposals: dict[str, list[EventCandidate]] = {}

    for group in candidate_groups:
        for candidate in group:
            ref = candidate.event_ref
            if ref.source_frame is None or ref.source_frame != frame_ref:
                conflicts.append(_conflict(candidate.predicate_ref, "frame_mismatch", [candidate]))
            elif candidate.predicate_ref not in known_units or ref.predicate_ref != candidate.predicate_ref:
                conflicts.append(_conflict(candidate.predicate_ref, "predicate_not_in_frame", [candidate]))
            else:
                proposals.setdefault(candidate.predicate_ref, []).append(candidate)

    accepted: dict[str, EventCandidate] = {}
    for predicate_ref, candidates in proposals.items():
        signatures = {_signature(candidate) for candidate in candidates}
        if len(signatures) > 1:
            conflicts.append(_conflict(predicate_ref, "incompatible_event_refs", candidates))
            continue
        accepted[predicate_ref] = candidates[0]

    owners: dict[str, list[str]] = {}
    for predicate_ref, candidate in accepted.items():
        owners.setdefault(candidate.event_ref.event_id, []).append(predicate_ref)
    for predicate_refs in owners.values():
        if len(predicate_refs) > 1:
            for predicate_ref in predicate_refs:
                conflicts.append(_conflict(predicate_ref, "event_id_collision", [accepted.pop(predicate_ref)]))

    order = {unit_id: i for i, unit_id in enumerate(unit_order)}
    conflicts.sort(key=lambda c: (order.get(c.predicate_ref, len(order)), c.predicate_ref, c.reason, c.event_ids))
    return EventIndex(frame_ref=frame_ref, by_predicate=accepted, conflicts=tuple(conflicts), unit_order=unit_order)


def build_frame_event_index(frame: UtteranceFrame) -> EventIndex:
    """Full frame identity set: base + discovered OBSERVATION + KNOWLEDGE_ACQUISITION events.

    Discovery only (phase A): no meta-event target is bound here, so building
    the index never depends on, nor recurses into, relation binding (phase B).
    """
    base = extract_event_candidates(frame)
    return build_event_index(frame, base, discover_observation_events(frame), discover_knowledge_events(frame, base))


_RESOLVED = frozenset({ResolutionStatus.RESOLVED_EXPLICIT, ResolutionStatus.RESOLVED_STRUCTURAL})


def target_index_violation(reference: EventTargetReference, event_index: EventIndex) -> str | None:
    """Contextual check of a target record against ONE frame index; None when consistent.

    A resolved EVENT_TARGET must name an indexed predicate whose EventRef is
    exactly target_event; a resolved PROPOSITION_TARGET must name a predicate of
    this frame. Pure: no global state, no cross-frame lookup, no repair.
    """
    if reference.resolution_status not in _RESOLVED:
        return None
    if reference.target_kind is TargetKind.EVENT_TARGET:
        indexed = event_index.event_for(reference.target_predicate)
        if indexed is None:
            return "target_predicate_not_indexed"
        if indexed.event_ref.event_id != reference.target_event:
            return "target_event_mismatch"
        return None
    if reference.target_kind is TargetKind.PROPOSITION_TARGET and reference.target_predicate not in event_index.unit_order:
        return "target_predicate_not_in_frame"
    return None


def _signature(candidate: EventCandidate) -> tuple[str, str, str]:
    return (candidate.event_ref.event_id, candidate.event_ref.event_kind.value, candidate.occurrence_status.value)


def _conflict(predicate_ref: str, reason: str, candidates: list[EventCandidate]) -> EventIndexConflict:
    return EventIndexConflict(
        predicate_ref=predicate_ref,
        reason=reason,
        event_ids=tuple(sorted({c.event_ref.event_id for c in candidates})),
        event_kinds=tuple(sorted({c.event_ref.event_kind.value for c in candidates})),
    )
