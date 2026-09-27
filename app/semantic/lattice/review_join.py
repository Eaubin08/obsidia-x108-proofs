"""ReviewJoin V0: read-only review envelope around a caller-chosen center event.

The envelope gathers the frame-local connected component of the center event
over the typed meta-event relations (OBSERVES, LEARNS_ABOUT, REPORTS_ABOUT,
BELIEVES_ABOUT) and copies, per event, its predicate, occurrence status and
projected epistemic states. Unresolved, ambiguous and non-event targets are
kept as they are.

It is NOT a verdict: no truth scalar, no conflict resolution, no temporal
enrichment, no coreference between distinct events, no center selection
heuristic (the caller names the center), no memory, no authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from app.semantic.lattice.event_coreference import EventTargetReference, ResolutionStatus, TargetKind
from app.semantic.lattice.event_extraction import extract_event_candidates
from app.semantic.lattice.event_index import EventIndex, EventIndexConflict, build_frame_event_index
from app.semantic.lattice.events import EventReferenceRelation
from app.semantic.lattice.knowledge_event_extraction import extract_knowledge_event_targets
from app.semantic.lattice.language_flow_projection import project_epistemic_flows
from app.semantic.lattice.meta_event_relations import (
    extract_belief_event_relations,
    extract_report_event_relations,
)
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets
from app.semantic.lattice.primitives import UtteranceFrame

REVIEW_JOIN_VERSION = "review_join_v0"


@dataclass(frozen=True)
class ReviewEnvelope:
    center_event: str
    frame_ref: str
    events: tuple[Mapping[str, Any], ...] = ()
    relations: tuple[EventReferenceRelation, ...] = ()
    unresolved: tuple[EventTargetReference, ...] = ()
    non_event_targets: tuple[EventTargetReference, ...] = ()
    conflicts: tuple[EventIndexConflict, ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "events", tuple(MappingProxyType(dict(e)) for e in self.events))
        for name in ("relations", "unresolved", "non_event_targets", "conflicts"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "center_event": self.center_event,
            "frame_ref": self.frame_ref,
            "events": [dict(e) for e in self.events],
            "relations": [r.to_dict() for r in self.relations],
            "unresolved": [t.to_dict() for t in self.unresolved],
            "non_event_targets": [t.to_dict() for t in self.non_event_targets],
            "conflicts": [c.to_dict() for c in self.conflicts],
            "provenance": dict(self.provenance),
            "metadata": dict(self.metadata),
        }


def build_review_envelope(
    frame: UtteranceFrame,
    center_event: str,
    event_index: EventIndex | None = None,
) -> ReviewEnvelope:
    index = event_index if event_index is not None else build_frame_event_index(frame)
    if index.by_event_id(center_event) is None:
        raise ValueError(f"center event {center_event!r} is not indexed in this frame")

    base = extract_event_candidates(frame)
    observation = extract_observation_event_targets(frame, base)
    knowledge = extract_knowledge_event_targets(frame, base)
    reports = extract_report_event_relations(frame, index)
    beliefs = extract_belief_event_relations(frame, index)
    relations = [
        r for r in (*observation.relations, *knowledge.relations, *reports.relations, *beliefs.relations)
        if index.by_event_id(r.source_event) is not None and index.by_event_id(r.target_event) is not None
    ]
    targets = (*observation.targets, *knowledge.targets, *reports.targets, *beliefs.targets)

    neighbours: dict[str, set[str]] = {}
    for r in relations:
        neighbours.setdefault(r.source_event, set()).add(r.target_event)
        neighbours.setdefault(r.target_event, set()).add(r.source_event)
    component, frontier = {center_event}, [center_event]
    while frontier:
        for other in neighbours.get(frontier.pop(), ()):
            if other not in component:
                component.add(other)
                frontier.append(other)

    units = {unit.id: unit for unit in frame.units}
    states: dict[str, list[str]] = {}
    for flow in project_epistemic_flows(frame):
        if flow.source_object is not None and flow.state is not None:
            states.setdefault(flow.source_object, [])
            if flow.state not in states[flow.source_object]:
                states[flow.source_object].append(flow.state)

    events = []
    for candidate in index.events():
        if candidate.event_ref.event_id not in component:
            continue
        unit = units[candidate.predicate_ref]
        events.append({
            "event_id": candidate.event_ref.event_id,
            "predicate_ref": candidate.predicate_ref,
            "predicate": unit.predicate,
            "event_kind": candidate.event_ref.event_kind.value,
            "occurrence_status": candidate.occurrence_status.value,
            "epistemic_states": tuple(states.get(candidate.predicate_ref, ())),
            "span": unit.span,
            "is_center": candidate.event_ref.event_id == center_event,
        })

    component_predicates = {index.by_event_id(e).predicate_ref for e in component}
    order = {unit.id: i for i, unit in enumerate(frame.units)}
    in_component = [t for t in targets if t.source_event in component]
    kept_relations = sorted(
        (r for r in relations if r.source_event in component),
        key=lambda r: (order[index.by_event_id(r.source_event).predicate_ref], r.relation_kind.value),
    )
    return ReviewEnvelope(
        center_event=center_event,
        frame_ref=index.frame_ref,
        events=tuple(events),
        relations=tuple(kept_relations),
        unresolved=tuple(t for t in in_component
                         if t.resolution_status in {ResolutionStatus.UNRESOLVED, ResolutionStatus.AMBIGUOUS}),
        non_event_targets=tuple(t for t in in_component
                                if t.target_kind in {TargetKind.PROPOSITION_TARGET, TargetKind.ENTITY_TARGET}
                                and t.resolution_status not in {ResolutionStatus.UNRESOLVED, ResolutionStatus.AMBIGUOUS}),
        conflicts=tuple(c for c in index.conflicts if c.predicate_ref in component_predicates),
        provenance={
            "source": REVIEW_JOIN_VERSION,
            "frame_ref": index.frame_ref,
            "relation_producers": ["observation_event_extraction", "knowledge_event_extraction",
                                   "meta_event_relations.report", "meta_event_relations.belief"],
            "center_selected_by": "caller",
            "nominal_reference_adapter": "not_wired",
        },
        metadata={
            "truth": None,
            "conflict_resolution": "none",
            "temporal_enrichment": "none",
            "cross_event_coreference": "none",
            "MEMORY_WRITE": 0,
            "AUTHORIZED_FLOW_CREATED": 0,
            "EXECUTED_FLOW_CREATED": 0,
            "VERIFIED_FLOW_CREATED": 0,
            "KX108_CALLED": 0,
        },
    )
