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
from app.semantic.lattice.event_extraction import (
    EventCandidate,
    OccurrenceStatus,
    extract_event_candidates,
    occurrence_claim_for,
    occurrence_status_for,
)
from app.semantic.lattice.events import EventKind, EventRef, EventReferenceRelation, EventRelationKind
from app.semantic.lattice.primitives import PredicateUnit, RelationKind, UtteranceFrame

_SOURCE = "semantic_knowledge_event_extraction"
# Immediate structural complement of a LEARN predicate (shared selector contract).
_TARGET_RELATIONS = frozenset({RelationKind.EMBEDS.value})


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


def discover_knowledge_events(
    frame: UtteranceFrame,
    candidates: Sequence[EventCandidate],
) -> tuple[EventCandidate, ...]:
    """Phase A: mint the frame's KNOWLEDGE_ACQUISITION EventRefs without binding targets.

    `candidates` is only consulted to keep an existing base EventRef id for a
    LEARN predicate (unchanged identity rule).
    """
    by_predicate = {candidate.predicate_ref: candidate for candidate in candidates}
    return tuple(_knowledge_candidate(frame, unit, by_predicate) for unit in frame.units if unit.predicate == "LEARN")


def extract_knowledge_event_targets(
    frame: UtteranceFrame,
    candidates: Sequence[EventCandidate],
) -> KnowledgeEventExtraction:
    """Discover, index the whole frame, then bind (public wrapper).

    Targets are bound against the full frame identity set: the canonical base
    (extract_event_candidates(frame)), every discovered OBSERVATION and
    KNOWLEDGE_ACQUISITION event, plus the caller `candidates`, which are
    proposals only (see extract_observation_event_targets).
    """
    # Imported at call time: event_index imports this module.
    from app.semantic.lattice.event_index import build_event_index
    from app.semantic.lattice.observation_event_extraction import discover_observation_events

    # Identities come from the frame itself, never from caller-supplied
    # candidates (see observation extractor).
    canonical_base = extract_event_candidates(frame)
    learn_candidates = discover_knowledge_events(frame, canonical_base)
    index = build_event_index(frame, canonical_base, candidates, discover_observation_events(frame), learn_candidates)
    targets, relations = bind_knowledge_targets(frame, learn_candidates, index)
    return KnowledgeEventExtraction(
        knowledge_events=learn_candidates,
        targets=targets,
        relations=relations,
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
            "INDEX_VIEW": "full_frame",
        },
    )



def bind_knowledge_targets(
    frame: UtteranceFrame,
    learn_candidates: Sequence[EventCandidate],
    event_index,
) -> tuple[tuple[EventTargetReference, ...], tuple[EventReferenceRelation, ...]]:
    """Phase B: bind each KNOWLEDGE_ACQUISITION to its immediate target on a full frame EventIndex."""
    # Imported at call time: meta_event_relations imports this module.
    from app.semantic.lattice.meta_event_relations import select_immediate_meta_target

    index = event_index
    targets: list[EventTargetReference] = []
    relations: list[EventReferenceRelation] = []

    for candidate in learn_candidates:
        unit_id = candidate.predicate_ref
        if index.event_for(unit_id) is None:
            targets.append(_unresolved_target(candidate, reason="source_event_conflict"))
            continue
        selection = select_immediate_meta_target(frame, unit_id, _TARGET_RELATIONS, index)
        if selection.resolution_status is ResolutionStatus.AMBIGUOUS:
            targets.append(EventTargetReference(
                source_event=candidate.event_ref.event_id,
                source_predicate=unit_id,
                target_kind=TargetKind.UNKNOWN_TARGET,
                resolution_status=ResolutionStatus.AMBIGUOUS,
                target_predicate=None,
                target_event=None,
                provenance={
                    "source": _SOURCE,
                    "reason": selection.provenance["reason"],
                    "candidate_predicate_ids": list(selection.provenance["candidate_predicate_ids"]),
                    "parser_relation": RelationKind.EMBEDS.value,
                },
                confidence={"value": None, "calibrated": False},
                metadata=_target_metadata(),
            ))
            continue
        target_unit_id = selection.target_predicate
        if target_unit_id is None:
            reason = selection.provenance.get("reason")
            targets.append(_unresolved_target(
                candidate, reason="no_explicit_embedded_target" if reason == "no_immediate_relation" else reason))
            continue
        target_candidate = index.event_for(target_unit_id) if selection.target_event else None
        if target_candidate is None:
            targets.append(EventTargetReference(
                source_event=candidate.event_ref.event_id,
                source_predicate=unit_id,
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
            source_predicate=unit_id,
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

    return tuple(targets), tuple(relations)


def _knowledge_candidate(
    frame: UtteranceFrame,
    unit: PredicateUnit,
    existing: Mapping[str, EventCandidate],
) -> EventCandidate:
    base = existing.get(unit.id)
    occurrence = base.occurrence_status if base is not None else occurrence_status_for(frame, unit)
    if base is not None and base.occurrence_claim is not None:
        claim, derivation = base.occurrence_claim, base.occurrence_derivation
    else:
        derived = occurrence_claim_for(frame, unit)
        claim, derivation = derived.claim, derived.derivation
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
        occurrence_claim=claim,
        occurrence_derivation=derivation,
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


def _frame_ref(frame: UtteranceFrame) -> str:
    digest = sha256(frame.raw.encode("utf-8")).hexdigest()[:12]
    return f"frame:{digest}"


def _event_id(frame_ref: str, predicate_ref: str) -> str:
    seed = f"{frame_ref}|{predicate_ref}|knowledge_event_extraction_v0"
    digest = sha256(seed.encode("utf-8")).hexdigest()[:16]
    return f"event:{digest}"
