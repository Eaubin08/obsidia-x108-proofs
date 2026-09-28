"""Observation event target extraction.

This layer consumes parser-backed PredicateUnit structures plus existing event
candidates. It does not parse raw text, resolve generic event anaphora, validate
truth, write memory, infer authority, or create causal proof.
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
    occurrence_claim_for,
    occurrence_status_for,
)
from app.semantic.lattice.events import EventKind, EventRef, EventReferenceRelation, EventRelationKind
from app.semantic.lattice.primitives import Argument, PredicateUnit, RelationKind, UtteranceFrame

_SOURCE = "semantic_observation_event_extraction"
# Immediate structural complement of an OBSERVE predicate (shared selector contract).
_TARGET_RELATIONS = frozenset({RelationKind.EMBEDS.value})


@dataclass(frozen=True)
class ObservationEventResult:
    observation_events: tuple[EventCandidate, ...] = ()
    targets: tuple[EventTargetReference, ...] = ()
    relations: tuple[EventReferenceRelation, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "observation_events", tuple(self.observation_events))
        object.__setattr__(self, "targets", tuple(self.targets))
        object.__setattr__(self, "relations", tuple(self.relations))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_events": [event.to_dict() for event in self.observation_events],
            "targets": [target.to_dict() for target in self.targets],
            "relations": [relation.to_dict() for relation in self.relations],
            "metadata": dict(self.metadata),
        }


def discover_observation_events(frame: UtteranceFrame) -> tuple[EventCandidate, ...]:
    """Phase A: mint the frame's OBSERVATION EventRefs (ids, occurrence) without binding targets."""
    return tuple(_observation_candidate(frame, unit) for unit in frame.units if unit.predicate == "OBSERVE")


def extract_observation_event_targets(
    frame: UtteranceFrame,
    candidates: Sequence[EventCandidate],
) -> ObservationEventResult:
    """Discover, index the whole frame, then bind (public wrapper).

    Targets are bound against the full frame identity set: the canonical base
    (extract_event_candidates(frame)), every discovered OBSERVATION and
    KNOWLEDGE_ACQUISITION event, plus the caller `candidates`. The canonical
    set is always present, so the result does not depend on caller
    completeness; `candidates` may be empty, partial, complete, duplicated,
    conflicting or foreign -- they are proposals only (identical -> merged,
    incompatible -> EventIndex conflict, foreign frame -> rejected).
    """
    # Imported at call time: event_index imports this module.
    from app.semantic.lattice.event_extraction import extract_event_candidates
    from app.semantic.lattice.event_index import build_event_index
    from app.semantic.lattice.knowledge_event_extraction import discover_knowledge_events

    # Identities come from the frame itself (canonical base + meta discovery),
    # never from caller-supplied candidates: a differing proposal conflicts
    # instead of overriding, and an omitted one does not hide the event.
    canonical_base = extract_event_candidates(frame)
    observations = discover_observation_events(frame)
    learns = discover_knowledge_events(frame, canonical_base)
    index = build_event_index(frame, canonical_base, candidates, observations, learns)
    targets, relations = bind_observation_targets(frame, observations, index)
    return ObservationEventResult(
        observation_events=observations,
        targets=targets,
        relations=relations,
        metadata={
            "VERIFIED_FLOW_CREATED": 0,
            "SUPPORTED_FLOW_CREATED": 0,
            "PHYSICAL_PROOF_CREATED": 0,
            "VALIDATED_EVIDENCE_CREATED": 0,
            "MEMORY_FLOW_CREATED": 0,
            "MEMORY_WRITE": 0,
            "AUTHORIZED_FLOW_CREATED": 0,
            "EXECUTED_FLOW_CREATED": 0,
            "KX108_CALLED": 0,
            "CAUSAL_FLOW_FROM_OBSERVATION": 0,
            "TARGET_OCCURRENCE_PROMOTIONS": 0,
            "LATEST_EVENT_FALLBACK": 0,
            "INDEX_VIEW": "full_frame",
        },
    )



def bind_observation_targets(
    frame: UtteranceFrame,
    observations: Sequence[EventCandidate],
    event_index,
) -> tuple[tuple[EventTargetReference, ...], tuple[EventReferenceRelation, ...]]:
    """Phase B: bind each OBSERVATION to its immediate target on a full frame EventIndex."""
    # Imported at call time: meta_event_relations imports this module.
    from app.semantic.lattice.meta_event_relations import select_immediate_meta_target

    index = event_index
    targets: list[EventTargetReference] = []
    relations: list[EventReferenceRelation] = []

    for observation in observations:
        unit = frame.unit(observation.predicate_ref)
        if index.event_for(unit.id) is None:
            targets.append(_unknown_target(observation, reason="source_event_conflict"))
            continue
        selection = select_immediate_meta_target(frame, unit.id, _TARGET_RELATIONS, index)
        if selection.resolution_status is ResolutionStatus.AMBIGUOUS:
            targets.append(_ambiguous_target(observation, selection))
            continue
        target_unit_id = selection.target_predicate
        if target_unit_id is not None:
            target_candidate = index.event_for(target_unit_id) if selection.target_event else None
            if target_candidate is None:
                targets.append(_proposition_target(observation, unit.id, target_unit_id))
                continue
            targets.append(_event_target(observation, unit.id, target_candidate))
            relations.append(EventReferenceRelation(
                relation_kind=EventRelationKind.OBSERVES,
                source_event=observation.event_ref.event_id,
                target_event=target_candidate.event_ref.event_id,
                provenance={
                    "source": _SOURCE,
                    "target_predicate": target_unit_id,
                    "parser_relation": RelationKind.EMBEDS.value,
                },
                confidence={"value": None, "calibrated": False},
                metadata={
                    "validated_evidence": False,
                    "physical_truth": False,
                    "target_occurrence_promoted": False,
                    "causal_flow_from_observation": False,
                },
            ))
            continue
        if selection.provenance.get("reason") != "no_immediate_relation":
            targets.append(_unknown_target(observation, reason=selection.provenance["reason"]))
            continue
        entity = _direct_entity_target(unit)
        if entity is not None:
            targets.append(_entity_target(observation, unit.id, entity))
            continue
        targets.append(_unknown_target(observation, reason="no_structural_target"))

    return tuple(targets), tuple(relations)


def _observation_candidate(frame: UtteranceFrame, unit: PredicateUnit) -> EventCandidate:
    frame_ref = _frame_ref(frame)
    event = EventRef(
        event_id=_event_id(frame_ref, unit.id),
        predicate_ref=unit.id,
        event_kind=EventKind.OBSERVATION,
        actor_ref=unit.subject,
        source_frame=frame_ref,
        provenance={
            "source": _SOURCE,
            "predicate_ref": unit.id,
            "parser": unit.provenance,
            "span": unit.span,
            "parser_rule": "observation_predicate",
            "lexical_source_lemma": unit.lemma,
        },
        confidence={"value": unit.confidence, "calibrated": False},
        status="candidate",
        metadata={
            "event_id_scope": "frame_local",
            "source_actor_ref": unit.subject,
            "source_type": "UNKNOWN",
            "evidence_validated": False,
            "physical_truth": False,
        },
    )
    occurrence = occurrence_status_for(frame, unit)
    claim = occurrence_claim_for(frame, unit)
    return EventCandidate(
        event_ref=event,
        predicate_ref=unit.id,
        occurrence_status=occurrence,
        occurrence_claim=claim.claim,
        occurrence_derivation=claim.derivation,
        provenance={
            "source": _SOURCE,
            "predicate_ref": unit.id,
            "parser": unit.provenance,
            "span": unit.span,
        },
        metadata={
            "observation_event": True,
            "event_occurred_claim": occurrence is OccurrenceStatus.ASSERTED_OCCURRED,
            "target_occurrence_promoted": False,
        },
    )


def _event_target(
    observation: EventCandidate,
    source_predicate: str,
    target_candidate: EventCandidate,
) -> EventTargetReference:
    return EventTargetReference(
        source_event=observation.event_ref.event_id,
        source_predicate=source_predicate,
        target_kind=TargetKind.EVENT_TARGET,
        resolution_status=ResolutionStatus.RESOLVED_STRUCTURAL,
        target_predicate=target_candidate.predicate_ref,
        target_event=target_candidate.event_ref.event_id,
        provenance={
            "source": _SOURCE,
            "parser_relation": RelationKind.EMBEDS.value,
            "target_predicate": target_candidate.predicate_ref,
        },
        confidence={"value": None, "calibrated": False},
        metadata=_target_metadata("embedded_event"),
    )


def _proposition_target(
    observation: EventCandidate,
    source_predicate: str,
    target_predicate: str,
) -> EventTargetReference:
    return EventTargetReference(
        source_event=observation.event_ref.event_id,
        source_predicate=source_predicate,
        target_kind=TargetKind.PROPOSITION_TARGET,
        resolution_status=ResolutionStatus.RESOLVED_STRUCTURAL,
        target_predicate=target_predicate,
        target_event=None,
        provenance={
            "source": _SOURCE,
            "parser_relation": RelationKind.EMBEDS.value,
            "target_predicate": target_predicate,
        },
        confidence={"value": None, "calibrated": False},
        metadata=_target_metadata("embedded_proposition"),
    )


def _entity_target(
    observation: EventCandidate,
    source_predicate: str,
    entity: Argument,
) -> EventTargetReference:
    return EventTargetReference(
        source_event=observation.event_ref.event_id,
        source_predicate=source_predicate,
        target_kind=TargetKind.ENTITY_TARGET,
        resolution_status=ResolutionStatus.RESOLVED_STRUCTURAL,
        target_predicate=None,
        target_event=None,
        provenance={
            "source": _SOURCE,
            "parser_object": entity.text,
            "parser_object_head": entity.head,
            "parser_object_kind": entity.kind,
            "span": entity.span,
        },
        confidence={"value": None, "calibrated": False},
        metadata=_target_metadata("direct_entity"),
    )


def _ambiguous_target(observation: EventCandidate, selection: EventTargetReference) -> EventTargetReference:
    return EventTargetReference(
        source_event=observation.event_ref.event_id,
        source_predicate=observation.predicate_ref,
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
        metadata=_target_metadata("ambiguous"),
    )


def _unknown_target(observation: EventCandidate, *, reason: str) -> EventTargetReference:
    return EventTargetReference(
        source_event=observation.event_ref.event_id,
        source_predicate=observation.predicate_ref,
        target_kind=TargetKind.UNKNOWN_TARGET,
        resolution_status=ResolutionStatus.UNRESOLVED,
        target_predicate=None,
        target_event=None,
        provenance={"source": _SOURCE, "reason": reason},
        confidence={"value": None, "calibrated": False},
        metadata=_target_metadata("unknown"),
    )


def _target_metadata(target_rule: str) -> dict[str, Any]:
    return {
        "target_rule": target_rule,
        "event_coreference_heuristic": False,
        "nearest_event_fallback": False,
        "target_occurrence_promoted": False,
        "evidence_validated": False,
        "physical_truth": False,
    }


def _direct_entity_target(unit: PredicateUnit) -> Argument | None:
    arg = unit.object
    if arg is None:
        return None
    if arg.kind == "PRONOUN" or arg.reference in {"UNRESOLVED", "DEICTIC"}:
        return None
    if arg.kind in {"NP", "NEGATIVE_QUANTIFIER"}:
        return arg
    return None


def _frame_ref(frame: UtteranceFrame) -> str:
    digest = sha256(frame.raw.encode("utf-8")).hexdigest()[:12]
    return f"frame:{digest}"


def _event_id(frame_ref: str, predicate_ref: str) -> str:
    seed = f"{frame_ref}|{predicate_ref}|observation_event_extraction_v0"
    digest = sha256(seed.encode("utf-8")).hexdigest()[:16]
    return f"event:{digest}"
