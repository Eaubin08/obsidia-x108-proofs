"""Meta-event target selection and relations over an EventIndex.

A meta-event (REPORT, BELIEF, ...) targets exactly its IMMEDIATE structural
complement, read from typed parser relations. Zero relations leave the target
UNKNOWN; several are AMBIGUOUS (MULTIPLE_TARGETS_UNSUPPORTED). The selector
never falls back to the first, nearest or deepest candidate, never mints an
EventRef, and never touches target occurrence, truth, evidence or authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import AbstractSet, Any, Iterable, Mapping

from app.semantic.lattice.event_coreference import EventTargetReference, ResolutionStatus, TargetKind
from app.semantic.lattice.event_extraction import extract_event_candidates
from app.semantic.lattice.event_index import EventIndex, target_index_violation
from app.semantic.lattice.event_reference_resolution import resolve_explicit_event_references
from app.semantic.lattice.knowledge_event_extraction import extract_knowledge_event_targets
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets
from app.semantic.lattice.events import EventKind, EventReferenceRelation, EventRelationKind
from app.semantic.lattice.primitives import RelationKind, UtteranceFrame

_SOURCE = "semantic_meta_event_relations"
MULTIPLE_TARGETS_UNSUPPORTED = "MULTIPLE_TARGETS_UNSUPPORTED"


@dataclass(frozen=True)
class MetaEventRelationResult:
    targets: tuple[EventTargetReference, ...] = ()
    relations: tuple[EventReferenceRelation, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "targets", tuple(self.targets))
        object.__setattr__(self, "relations", tuple(self.relations))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "targets": [target.to_dict() for target in self.targets],
            "relations": [relation.to_dict() for relation in self.relations],
            "metadata": dict(self.metadata),
        }


def extract_report_event_relations(frame: UtteranceFrame, event_index: EventIndex) -> MetaEventRelationResult:
    """REPORT EventRef -REPORTS_ABOUT-> immediate target EventRef (parser REPORTS relation)."""
    return _extract_meta_relations(
        frame, event_index, EventKind.REPORT, frozenset({RelationKind.REPORTS.value}),
        EventRelationKind.REPORTS_ABOUT,
    )


def extract_belief_event_relations(frame: UtteranceFrame, event_index: EventIndex) -> MetaEventRelationResult:
    """BELIEF EventRef -BELIEVES_ABOUT-> immediate target EventRef (parser BELIEVES relation)."""
    return _extract_meta_relations(
        frame, event_index, EventKind.BELIEF, frozenset({RelationKind.BELIEVES.value}),
        EventRelationKind.BELIEVES_ABOUT,
    )


_NOMINAL_RELATION_BY_KIND: Mapping[EventKind, EventRelationKind] = MappingProxyType({
    EventKind.OBSERVATION: EventRelationKind.OBSERVES,
    EventKind.KNOWLEDGE_ACQUISITION: EventRelationKind.LEARNS_ABOUT,
    EventKind.REPORT: EventRelationKind.REPORTS_ABOUT,
    EventKind.BELIEF: EventRelationKind.BELIEVES_ABOUT,
})


def extract_nominal_reference_relations(
    frame: UtteranceFrame,
    event_index: EventIndex,
    *,
    structural_relations: Iterable[EventReferenceRelation] | None = None,
) -> MetaEventRelationResult:
    """Adapter: explicit nominal event reference -> typed meta-event relation.

    Consumes the pure resolver output over the indexed events. Only a
    RESOLVED_STRUCTURAL reference whose governing predicate is an indexed
    meta-event (observation, knowledge acquisition, report, belief) becomes a
    relation; a structural target of the same meta-event takes precedence.
    """
    if structural_relations is None:
        base = extract_event_candidates(frame)
        structural_relations = (
            *extract_observation_event_targets(frame, base).relations,
            *extract_knowledge_event_targets(frame, base).relations,
            *extract_report_event_relations(frame, event_index).relations,
            *extract_belief_event_relations(frame, event_index).relations,
        )
    structural_sources = {relation.source_event for relation in structural_relations}
    resolution = resolve_explicit_event_references(frame, event_index.events())

    targets: list[EventTargetReference] = []
    relations: list[EventReferenceRelation] = []
    skipped: dict[str, int] = {}
    for reference in resolution.references:
        governor_id = reference.provenance.get("governing_predicate_id")
        governor = event_index.event_for(governor_id) if governor_id else None
        target = event_index.by_event_id(reference.target_event) if reference.target_event else None
        if reference.resolution_status is not ResolutionStatus.RESOLVED_STRUCTURAL or target is None:
            reason = "reference_not_resolved"
        elif governor is None:
            reason = "no_governing_event"
        elif governor.event_ref.event_kind not in _NOMINAL_RELATION_BY_KIND:
            reason = "governor_not_meta_event"
        elif governor.event_ref.event_id in structural_sources:
            reason = "structural_target_precedence"
        else:
            reason = None
        if reason is not None:
            skipped[reason] = skipped.get(reason, 0) + 1
            continue
        provenance = dict(reference.provenance, source_predicate=governor.predicate_ref,
                          target_rule="explicit_nominal_reference")
        metadata = {
            "target_rule": "explicit_nominal_reference",
            "coreference_confidence": reference.metadata.get("coreference_confidence"),
            "coreference_calibrated": False,
            "source_occurrence_status": governor.occurrence_status.value,  # legacy, compatibility only
            "target_occurrence_status": target.occurrence_status.value,
            "source_occurrence_claim": _claim(governor),
            "target_occurrence_claim": _claim(target),
            "target_occurrence_promoted": False,
            "validated_evidence": False,
            "verified": False,
            "truth": None,
        }
        record = EventTargetReference(
            source_event=governor.event_ref.event_id,
            source_predicate=governor.predicate_ref,
            target_kind=TargetKind.EVENT_TARGET,
            resolution_status=ResolutionStatus.RESOLVED_STRUCTURAL,
            target_predicate=target.predicate_ref,
            target_event=target.event_ref.event_id,
            provenance=provenance,
            confidence=dict(reference.confidence),
            metadata=metadata,
        )
        if target_index_violation(record, event_index) is not None:
            skipped["target_index_inconsistent"] = skipped.get("target_index_inconsistent", 0) + 1
            continue
        targets.append(record)
        relations.append(EventReferenceRelation(
            relation_kind=_NOMINAL_RELATION_BY_KIND[governor.event_ref.event_kind],
            source_event=governor.event_ref.event_id,
            target_event=target.event_ref.event_id,
            provenance=provenance,
            confidence=dict(reference.confidence),
            status="nominal_reference",
            metadata=metadata,
        ))
    return MetaEventRelationResult(
        targets=tuple(targets),
        relations=tuple(relations),
        metadata={
            "SKIPPED": dict(sorted(skipped.items())),
            "VERIFIED_FLOW_CREATED": 0,
            "MEMORY_WRITE": 0,
            "AUTHORIZED_FLOW_CREATED": 0,
            "TARGET_OCCURRENCE_PROMOTIONS": 0,
            "CROSS_MESSAGE_BINDINGS": 0,
            "LATEST_EVENT_BINDINGS": 0,
            "KX108_CALLED": 0,
        },
    )


def _extract_meta_relations(
    frame: UtteranceFrame,
    event_index: EventIndex,
    source_kind: EventKind,
    relation_kinds: AbstractSet[str],
    relation_kind: EventRelationKind,
) -> MetaEventRelationResult:
    targets: list[EventTargetReference] = []
    relations: list[EventReferenceRelation] = []
    for source in event_index.events():
        if source.event_ref.event_kind is not source_kind:
            continue
        target = select_immediate_meta_target(frame, source.predicate_ref, relation_kinds, event_index)
        targets.append(target)
        if target.target_kind is not TargetKind.EVENT_TARGET or target.target_event is None:
            continue
        relations.append(EventReferenceRelation(
            relation_kind=relation_kind,
            source_event=target.source_event,
            target_event=target.target_event,
            provenance=dict(target.provenance, source_predicate=source.predicate_ref),
            confidence={"value": None, "calibrated": False},
            status="structural",
            metadata={
                "source_occurrence_status": source.occurrence_status.value,  # legacy, compatibility only
                "target_occurrence_status": target.metadata["target_occurrence_status"],
                "source_occurrence_claim": _claim(source),
                "target_occurrence_claim": target.metadata["target_occurrence_claim"],
                "target_occurrence_promoted": False,
                "validated_evidence": False,
                "verified": False,
                "supported": False,
                "observed": False,
                "truth": None,
            },
        ))
    return MetaEventRelationResult(
        targets=tuple(targets),
        relations=tuple(relations),
        metadata={
            "SOURCE_EVENT_KIND": source_kind.value,
            "RELATION_KIND": relation_kind.value,
            "VERIFIED_FLOW_CREATED": 0,
            "SUPPORTED_FLOW_CREATED": 0,
            "OBSERVED_FLOW_CREATED": 0,
            "VALIDATED_EVIDENCE_CREATED": 0,
            "MEMORY_WRITE": 0,
            "AUTHORIZED_FLOW_CREATED": 0,
            "EXECUTED_FLOW_CREATED": 0,
            "TARGET_OCCURRENCE_PROMOTIONS": 0,
            "KX108_CALLED": 0,
        },
    )


def select_immediate_meta_target(
    frame: UtteranceFrame,
    source_predicate: str,
    relation_kinds: AbstractSet[str],
    event_index: EventIndex,
) -> EventTargetReference:
    """Resolve the immediate target of `source_predicate` through `relation_kinds`."""
    source = event_index.event_for(source_predicate)
    if source is None:
        raise ValueError(f"source predicate {source_predicate!r} has no indexed EventRef")
    units = {unit.id: unit for unit in frame.units}
    relations = [r for r in frame.relations if r.source == source_predicate and r.kind in relation_kinds]
    targets = list(dict.fromkeys(r.target for r in relations))
    base = {
        "source": _SOURCE,
        "source_frame": event_index.frame_ref,
        "source_span": units[source_predicate].span if source_predicate in units else None,
        "relation_kinds": sorted(relation_kinds),
        "target_rule": "immediate_structural",
    }

    if not targets:
        return _unresolved(source, source_predicate, base, ResolutionStatus.UNRESOLVED, "no_immediate_relation")
    if len(targets) > 1:
        base["candidate_predicate_ids"] = targets
        return _unresolved(source, source_predicate, base, ResolutionStatus.AMBIGUOUS, MULTIPLE_TARGETS_UNSUPPORTED)

    target_predicate = targets[0]
    relation = next(r for r in relations if r.target == target_predicate)
    base.update({
        "parser_relation": relation.kind,
        "parser_evidence": relation.evidence,
        "target_predicate": target_predicate,
        "target_span": units[target_predicate].span if target_predicate in units else None,
    })
    if target_predicate not in units:
        return _unresolved(source, source_predicate, base, ResolutionStatus.UNRESOLVED, "target_not_in_frame")
    # A frame_mismatch conflict is about a foreign / unscoped proposal that merely
    # reuses a local unit id; it says nothing about this frame's target identity.
    if any(conflict.predicate_ref == target_predicate and conflict.reason != "frame_mismatch"
           for conflict in event_index.conflicts):
        return _unresolved(source, source_predicate, base, ResolutionStatus.UNRESOLVED, "target_event_conflict")

    target = event_index.event_for(target_predicate)
    if target is None:
        base["resolution_status"] = ResolutionStatus.RESOLVED_STRUCTURAL.value
        return _checked(source, source_predicate, base, event_index, EventTargetReference(
            source_event=source.event_ref.event_id,
            source_predicate=source_predicate,
            target_kind=TargetKind.PROPOSITION_TARGET,
            resolution_status=ResolutionStatus.RESOLVED_STRUCTURAL,
            target_predicate=target_predicate,
            target_event=None,
            provenance=base,
            confidence={"value": None, "calibrated": False},
            metadata=_metadata(None),
        ))
    base["resolution_status"] = ResolutionStatus.RESOLVED_STRUCTURAL.value
    return _checked(source, source_predicate, base, event_index, EventTargetReference(
        source_event=source.event_ref.event_id,
        source_predicate=source_predicate,
        target_kind=TargetKind.EVENT_TARGET,
        resolution_status=ResolutionStatus.RESOLVED_STRUCTURAL,
        target_predicate=target_predicate,
        target_event=target.event_ref.event_id,
        provenance=base,
        confidence={"value": None, "calibrated": False},
        metadata=_metadata(target.occurrence_status.value, _claim(target)),
    ))


def _checked(source, source_predicate: str, provenance: dict[str, Any], event_index: EventIndex,
             reference: EventTargetReference) -> EventTargetReference:
    violation = target_index_violation(reference, event_index)
    if violation is None:
        return reference
    return _unresolved(source, source_predicate, provenance, ResolutionStatus.UNRESOLVED, violation)


def _unresolved(source, source_predicate: str, provenance: dict[str, Any], status: ResolutionStatus,
                reason: str) -> EventTargetReference:
    provenance = dict(provenance, reason=reason, resolution_status=status.value)
    return EventTargetReference(
        source_event=source.event_ref.event_id,
        source_predicate=source_predicate,
        target_kind=TargetKind.UNKNOWN_TARGET,
        resolution_status=status,
        target_predicate=None,
        target_event=None,
        provenance=provenance,
        confidence={"value": None, "calibrated": False},
        metadata=_metadata(None),
    )


def _claim(candidate) -> str | None:
    """Canonical OccurrenceClaim of an event candidate (a claim, not a truth value)."""
    claim = getattr(candidate, "occurrence_claim", None)
    return claim.value if claim is not None else None


def _metadata(target_occurrence: str | None, target_claim: str | None = None) -> Mapping[str, Any]:
    return {
        "target_rule": "immediate_structural",
        "target_occurrence_status": target_occurrence,  # legacy, compatibility only
        "target_occurrence_claim": target_claim,
        "target_occurrence_promoted": False,
        "nearest_event_fallback": False,
        "first_candidate_fallback": False,
        "evidence_validated": False,
        "truth": None,
    }
