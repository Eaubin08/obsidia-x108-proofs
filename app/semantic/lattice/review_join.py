"""ReviewJoin V0: read-only review envelope around a caller-chosen center event.

The envelope gathers the frame-local connected component of the center event
over the typed meta-event relations (OBSERVES, LEARNS_ABOUT, REPORTS_ABOUT,
BELIEVES_ABOUT), structural or from explicit nominal references (relation
status "nominal_reference"), and copies, per event, its predicate, occurrence status,
EventRef provenance and EventCandidate provenance (as distinct blocks).

Epistemic information is kept lossless in `epistemic_contributions` (canonical):
one record per upstream epistemic flow (state + source predicate/event + flow
path, with the full flow) and one per typed meta-event relation of the
component (a perspective: source event + relation kind, no state invented).
Each event's `epistemic_states` is only a derived convenience view. Nothing is
deduplicated across sources. Unresolved, ambiguous and non-event targets are
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
    extract_nominal_reference_relations,
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
    epistemic_contributions: tuple[Mapping[str, Any], ...] = ()
    unresolved: tuple[EventTargetReference, ...] = ()
    non_event_targets: tuple[EventTargetReference, ...] = ()
    conflicts: tuple[EventIndexConflict, ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "events", tuple(_freeze(dict(e)) for e in self.events))
        object.__setattr__(self, "epistemic_contributions",
                           tuple(_freeze(dict(c)) for c in self.epistemic_contributions))
        for name in ("relations", "unresolved", "non_event_targets", "conflicts"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "center_event": self.center_event,
            "frame_ref": self.frame_ref,
            "events": [_thaw(e) for e in self.events],
            "relations": [r.to_dict() for r in self.relations],
            "epistemic_contributions": [_thaw(c) for c in self.epistemic_contributions],
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
    structural = (*observation.relations, *knowledge.relations, *reports.relations, *beliefs.relations)
    nominal = extract_nominal_reference_relations(frame, index, structural_relations=structural)
    relations = [
        r for r in (*structural, *nominal.relations)
        if index.by_event_id(r.source_event) is not None and index.by_event_id(r.target_event) is not None
    ]
    targets = (*observation.targets, *knowledge.targets, *reports.targets, *beliefs.targets, *nominal.targets)

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
    component_predicates = {index.by_event_id(e).predicate_ref for e in component}
    order = {unit.id: i for i, unit in enumerate(frame.units)}
    in_component = [t for t in targets if t.source_event in component]
    kept_relations = sorted(
        (r for r in relations if r.source_event in component),
        key=lambda r: (order[index.by_event_id(r.source_event).predicate_ref], r.relation_kind.value, r.status),
    )
    contributions = _epistemic_contributions(frame, index, component_predicates, kept_relations, order)

    events = []
    for candidate in index.events():
        if candidate.event_ref.event_id not in component:
            continue
        unit = units[candidate.predicate_ref]
        ref = candidate.event_ref
        events.append({
            "event_id": ref.event_id,
            "predicate_ref": candidate.predicate_ref,
            "predicate": unit.predicate,
            "event_kind": ref.event_kind.value,
            "occurrence_status": candidate.occurrence_status.value,
            # Derived convenience view; the canonical record is epistemic_contributions.
            "epistemic_states": tuple(dict.fromkeys(
                c["state"] for c in contributions
                if c["origin"] == "epistemic_flow" and c["predicate_ref"] == candidate.predicate_ref)),
            "span": unit.span,
            "is_center": ref.event_id == center_event,
            "event_ref": {
                "source_frame": ref.source_frame,
                "status": ref.status,
                "actor_ref": ref.actor_ref,
                "object_refs": ref.object_refs,
                "provenance": dict(ref.provenance),
                "confidence": dict(ref.confidence),
                "metadata": dict(ref.metadata),
            },
            "candidate": {
                "extraction_status": candidate.extraction_status.value,
                "provenance": dict(candidate.provenance),
                "metadata": dict(candidate.metadata),
            },
        })
    return ReviewEnvelope(
        center_event=center_event,
        frame_ref=index.frame_ref,
        events=tuple(events),
        relations=tuple(kept_relations),
        epistemic_contributions=tuple(contributions),
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
                                   "meta_event_relations.report", "meta_event_relations.belief",
                                   "meta_event_relations.nominal_reference"],
            "center_selected_by": "caller",
            "nominal_reference_adapter": "wired",
            "nominal_references_skipped": dict(nominal.metadata["SKIPPED"]),
            "epistemic_contributions": "canonical_lossless",
            "epistemic_states": "derived_summary",
            "flow_identity": "position_in_project_epistemic_flows (flows carry no id upstream)",
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


def _epistemic_contributions(
    frame: UtteranceFrame,
    index: EventIndex,
    component_predicates: set[str],
    relations: list[EventReferenceRelation],
    order: Mapping[str, int],
) -> list[dict[str, Any]]:
    """Lossless, source-bearing epistemic records for the component (no dedup across sources)."""
    def event_of(predicate: str | None) -> str | None:
        candidate = index.event_for(predicate) if predicate else None
        return candidate.event_ref.event_id if candidate is not None else None

    records: list[tuple[tuple[int, int, int], dict[str, Any]]] = []
    for position, flow in enumerate(project_epistemic_flows(frame)):
        if flow.source_object not in component_predicates or flow.state is None:
            continue
        source_predicate = flow.metadata.get("embedded_under")
        records.append(((order[flow.source_object], 0, position), {
            "origin": "epistemic_flow",
            "predicate_ref": flow.source_object,
            "event_id": event_of(flow.source_object),
            "state": flow.state,
            "source_predicate": source_predicate,
            "source_event": event_of(source_predicate),
            "flow_position": position,
            "flow": flow.to_dict(),
        }))
    for position, relation in enumerate(relations):
        target = index.by_event_id(relation.target_event)
        source = index.by_event_id(relation.source_event)
        records.append(((order[target.predicate_ref], 1, position), {
            "origin": "event_relation",
            "predicate_ref": target.predicate_ref,
            "event_id": relation.target_event,
            "state": None,
            "relation_kind": relation.relation_kind.value,
            "relation_status": relation.status,
            "source_predicate": source.predicate_ref,
            "source_event": relation.source_event,
            "relation_position": position,
        }))
    return [record for _, record in sorted(records, key=lambda item: item[0])]


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value
