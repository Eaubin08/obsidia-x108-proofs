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
from typing import AbstractSet, Any, Mapping

from app.semantic.lattice.event_coreference import EventTargetReference, ResolutionStatus, TargetKind
from app.semantic.lattice.event_index import EventIndex
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
            metadata={
                "source_occurrence_status": source.occurrence_status.value,
                "target_occurrence_status": target.metadata["target_occurrence_status"],
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
    if any(conflict.predicate_ref == target_predicate for conflict in event_index.conflicts):
        return _unresolved(source, source_predicate, base, ResolutionStatus.UNRESOLVED, "target_event_conflict")

    target = event_index.event_for(target_predicate)
    if target is None:
        base["resolution_status"] = ResolutionStatus.RESOLVED_STRUCTURAL.value
        return EventTargetReference(
            source_event=source.event_ref.event_id,
            source_predicate=source_predicate,
            target_kind=TargetKind.PROPOSITION_TARGET,
            resolution_status=ResolutionStatus.RESOLVED_STRUCTURAL,
            target_predicate=target_predicate,
            target_event=None,
            provenance=base,
            confidence={"value": None, "calibrated": False},
            metadata=_metadata(None),
        )
    base["resolution_status"] = ResolutionStatus.RESOLVED_STRUCTURAL.value
    return EventTargetReference(
        source_event=source.event_ref.event_id,
        source_predicate=source_predicate,
        target_kind=TargetKind.EVENT_TARGET,
        resolution_status=ResolutionStatus.RESOLVED_STRUCTURAL,
        target_predicate=target_predicate,
        target_event=target.event_ref.event_id,
        provenance=base,
        confidence={"value": None, "calibrated": False},
        metadata=_metadata(target.occurrence_status.value),
    )


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


def _metadata(target_occurrence: str | None) -> Mapping[str, Any]:
    return {
        "target_rule": "immediate_structural",
        "target_occurrence_status": target_occurrence,
        "target_occurrence_promoted": False,
        "nearest_event_fallback": False,
        "first_candidate_fallback": False,
        "evidence_validated": False,
        "truth": None,
    }
