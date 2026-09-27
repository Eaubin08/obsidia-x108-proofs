"""Knowledge acquisition event target extraction.

This layer consumes parser-backed PredicateUnit structures plus existing event
candidates. It does not parse raw text, resolve pronoun event anaphora, create
proof, write memory, or grant authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from app.semantic.lattice.event_coreference import (
    EventTargetReference,
    ResolutionStatus,
    TargetKind,
)
from app.semantic.lattice.event_extraction import EventCandidate, OccurrenceStatus
from app.semantic.lattice.events import EventKind, EventRef, EventReferenceRelation, EventRelationKind
from app.semantic.lattice.primitives import PredicateUnit, RelationKind, UtteranceFrame

_SOURCE = "semantic_knowledge_event_extraction"


@dataclass(frozen=True)
class KnowledgeEventExtraction:
    knowledge_events: tuple[EventCandidate, ...] = ()
    targets: tuple[EventTargetReference, ...] = ()
    relations: tuple[EventReferenceRelation, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "knowledge_events", tuple(self.knowledge_events))
        object.__setattr__(self, "targets", tuple(self.targets))
        object.__setattr__(self, "relations", tuple(self.relations))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "knowledge_events": [event.to_dict() for event in self.knowledge_events],
            "targets": [target.to_dict() for target in self.targets],
            "relations": [relation.to_dict() for relation in self.relations],
            "metadata": dict(self.metadata),
        }


def extract_knowledge_event_targets(
    frame: UtteranceFrame,
    candidates: Sequence[EventCandidate],
) -> KnowledgeEventExtraction:
    by_predicate = {candidate.predicate_ref: candidate for candidate in candidates}
    learn_candidates: list[EventCandidate] = []
    targets: list[EventTargetReference] = []
    relations: list[EventReferenceRelation] = []

    for unit in frame.units:
        if unit.predicate != "LEARN":
            continue
        candidate = _knowledge_candidate(frame, unit, by_predicate)
        learn_candidates.append(candidate)
        target_unit_id = _explicit_embedded_target(frame, unit.id)
        if target_unit_id is None:
            targets.append(_unresolved_target(candidate, reason="no_explicit_embedded_target"))
            continue
        target_candidate = by_predicate.get(target_unit_id)
        if target_candidate is None:
            targets.append(EventTargetReference(
                source_event=candidate.event_ref.event_id,
                source_predicate=unit.id,
                target_kind=TargetKind.PROPOSITION_TARGET,
                resolution_status=ResolutionStatus.RESOLVED_EXPLICIT,
                target_predicate=target_unit_id,
                target_event=None,
                provenance={
                    "source": _SOURCE,
                    "parser_relation": RelationKind.EMBEDS.value,
                    "target_predicate": target_unit_id,
                },
                confidence={"value": None, "calibrated": False},
                metadata=_target_metadata(),
            ))
            continue
        target = EventTargetReference(
            source_event=candidate.event_ref.event_id,
            source_predicate=unit.id,
            target_kind=TargetKind.EVENT_TARGET,
            resolution_status=ResolutionStatus.RESOLVED_EXPLICIT,
            target_predicate=target_unit_id,
            target_event=target_candidate.event_ref.event_id,
            provenance={
                "source": _SOURCE,
                "parser_relation": RelationKind.EMBEDS.value,
                "target_predicate": target_unit_id,
            },
            confidence={"value": None, "calibrated": False},
            metadata=_target_metadata(),
        )
        targets.append(target)
        relations.append(EventReferenceRelation(
            relation_kind=EventRelationKind.LEARNS_ABOUT,
            source_event=candidate.event_ref.event_id,
            target_event=target_candidate.event_ref.event_id,
            provenance={
                "source": _SOURCE,
                "target_predicate": target_unit_id,
                "parser_relation": RelationKind.EMBEDS.value,
            },
            confidence={"value": None, "calibrated": False},
            metadata={
                "validated_evidence": False,
                "truth": None,
                "target_occurrence_promoted": False,
            },
        ))

    return KnowledgeEventExtraction(
        knowledge_events=tuple(learn_candidates),
        targets=tuple(targets),
        relations=tuple(relations),
        metadata={
            "VERIFIED_FLOW_CREATED": 0,
            "VALIDATED_EVIDENCE_CREATED": 0,
            "PHYSICAL_PROOF_CREATED": 0,
            "MEMORY_FLOW_CREATED": 0,
            "MEMORY_WRITE": 0,
            "AUTHORIZED_FLOW_CREATED": 0,
            "EXECUTED_FLOW_CREATED": 0,
            "KX108_CALLED": 0,
            "TARGET_OCCURRENCE_PROMOTIONS": 0,
        },
    )


def _knowledge_candidate(
    frame: UtteranceFrame,
    unit: PredicateUnit,
    existing: Mapping[str, EventCandidate],
) -> EventCandidate:
    base = existing.get(unit.id)
    occurrence = base.occurrence_status if base is not None else _learn_occurrence_status(unit)
    frame_ref = base.event_ref.source_frame if base is not None else _frame_ref(frame)
    event_id = base.event_ref.event_id if base is not None else _event_id(frame_ref or _frame_ref(frame), unit.id)
    event = EventRef(
        event_id=event_id,
        predicate_ref=unit.id,
        event_kind=EventKind.KNOWLEDGE_ACQUISITION,
        source_frame=frame_ref,
        provenance={
            "source": _SOURCE,
            "predicate_ref": unit.id,
            "extraction_version": "knowledge_event_extraction_v0",
        },
        confidence={"value": unit.confidence, "calibrated": False},
        status="candidate",
        metadata={"event_id_scope": "frame_local"},
    )
    return EventCandidate(
        event_ref=event,
        predicate_ref=unit.id,
        occurrence_status=occurrence,
        provenance={
            "source": _SOURCE,
            "predicate_ref": unit.id,
            "parser": unit.provenance,
            "span": unit.span,
        },
        metadata={
            "knowledge_acquisition": True,
            "event_occurred_claim": occurrence is OccurrenceStatus.ASSERTED_OCCURRED,
        },
    )


def _explicit_embedded_target(frame: UtteranceFrame, learn_unit_id: str) -> str | None:
    for relation in frame.relations:
        if relation.source == learn_unit_id and relation.kind == RelationKind.EMBEDS.value:
            return relation.target
    for unit in frame.units:
        if unit.embedded_under == learn_unit_id:
            return unit.id
    return None


def _unresolved_target(candidate: EventCandidate, *, reason: str) -> EventTargetReference:
    return EventTargetReference(
        source_event=candidate.event_ref.event_id,
        source_predicate=candidate.predicate_ref,
        target_kind=TargetKind.UNKNOWN_TARGET,
        resolution_status=ResolutionStatus.UNRESOLVED,
        target_predicate=None,
        target_event=None,
        provenance={"source": _SOURCE, "reason": reason},
        confidence={"value": None, "calibrated": False},
        metadata=_target_metadata(),
    )


def _target_metadata() -> dict[str, Any]:
    return {
        "event_coreference_heuristic": False,
        "nearest_event_fallback": False,
        "temporal_attachment": "not_resolved_here",
    }


def _learn_occurrence_status(unit: PredicateUnit) -> OccurrenceStatus:
    if unit.polarity == "negative" or unit.role == "NEGATED":
        return OccurrenceStatus.NEGATED
    if unit.pragmatic == "HYPOTHETICAL" or unit.epistemic == "HYPOTHETICAL" or unit.role == "HYPOTHETICAL":
        return OccurrenceStatus.HYPOTHETICAL
    if unit.tense_aspect == "FUTURE":
        return OccurrenceStatus.FUTURE
    if unit.realized is True and unit.polarity == "positive":
        return OccurrenceStatus.ASSERTED_OCCURRED
    if unit.pragmatic == "ASSERTED":
        return OccurrenceStatus.ASSERTED_OCCURRED
    return OccurrenceStatus.UNKNOWN


def _frame_ref(frame: UtteranceFrame) -> str:
    digest = sha256(frame.raw.encode("utf-8")).hexdigest()[:12]
    return f"frame:{digest}"


def _event_id(frame_ref: str, predicate_ref: str) -> str:
    seed = f"{frame_ref}|{predicate_ref}|knowledge_event_extraction_v0"
    digest = sha256(seed.encode("utf-8")).hexdigest()[:16]
    return f"event:{digest}"
