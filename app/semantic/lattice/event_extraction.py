"""Conservative PredicateUnit -> EventRef extraction bridge.

This module is intentionally downstream of the parser. It reads an
UtteranceFrame and creates at most one frame-local EventRef candidate per
PredicateUnit. It does not mutate parser output, resolve truth, write memory,
or claim physical occurrence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Mapping

from app.semantic.lattice.events import EVENT_ID_SCOPE, EventKind, EventRef
from app.semantic.lattice.primitives import RelationKind, UtteranceFrame, PredicateUnit

EXTRACTION_VERSION = "event_extraction_v0"
_SOURCE = "semantic_event_extraction"

_ACTION_CLASSES = frozenset({
    "world_action",
    "preparatory",
    "inspection",
    "generic_action",
})


class OccurrenceStatus(str, Enum):
    ASSERTED_OCCURRED = "ASSERTED_OCCURRED"
    NEGATED = "NEGATED"
    HYPOTHETICAL = "HYPOTHETICAL"
    CONDITIONAL = "CONDITIONAL"
    FUTURE = "FUTURE"
    UNCERTAIN = "UNCERTAIN"
    REPORTED = "REPORTED"
    UNKNOWN = "UNKNOWN"


class ExtractionStatus(str, Enum):
    EXTRACTED = "EXTRACTED"
    UNSUPPORTED = "UNSUPPORTED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class EventCandidate:
    """Extraction metadata around an EventRef identity.

    The EventRef is the event identity. This record only explains how the
    candidate was derived from a PredicateUnit and how cautiously occurrence is
    represented.
    """

    event_ref: EventRef
    predicate_ref: str
    occurrence_status: OccurrenceStatus | str
    extraction_status: ExtractionStatus | str = ExtractionStatus.EXTRACTED
    provenance: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        occurrence = self.occurrence_status if isinstance(self.occurrence_status, OccurrenceStatus) else OccurrenceStatus(str(self.occurrence_status))
        extraction = self.extraction_status if isinstance(self.extraction_status, ExtractionStatus) else ExtractionStatus(str(self.extraction_status))
        object.__setattr__(self, "occurrence_status", occurrence)
        object.__setattr__(self, "extraction_status", extraction)
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_ref": self.event_ref.to_dict(),
            "predicate_ref": self.predicate_ref,
            "occurrence_status": self.occurrence_status.value,
            "extraction_status": self.extraction_status.value,
            "provenance": dict(self.provenance),
            "metadata": dict(self.metadata),
        }


def extract_event_candidates(
    frame: UtteranceFrame,
    *,
    extraction_version: str = EXTRACTION_VERSION,
) -> tuple[EventCandidate, ...]:
    """Return conservative EventRef candidates for parser-backed predicates."""

    conditional_sources = {
        relation.source
        for relation in frame.relations
        if relation.kind == RelationKind.CONDITIONS.value
    }
    frame_ref = _frame_ref(frame)
    units_by_id = {unit.id: unit for unit in frame.units}
    candidates: list[EventCandidate] = []
    for unit in frame.units:
        event_kind = _event_kind(unit)
        if event_kind is None:
            continue
        occurrence = _occurrence_status(unit, conditional_sources, units_by_id)
        event_id = _event_id(frame_ref, unit.id, extraction_version)
        event = EventRef(
            event_id=event_id,
            predicate_ref=unit.id,
            event_kind=event_kind,
            source_frame=frame_ref,
            provenance={
                "source": _SOURCE,
                "predicate_ref": unit.id,
                "extraction_version": extraction_version,
            },
            confidence={"value": unit.confidence, "calibrated": False},
            status="candidate",
            metadata={
                "event_id_scope": EVENT_ID_SCOPE,
                "extraction_version": extraction_version,
            },
        )
        candidates.append(EventCandidate(
            event_ref=event,
            predicate_ref=unit.id,
            occurrence_status=occurrence,
            extraction_status=ExtractionStatus.EXTRACTED,
            provenance={
                "source": _SOURCE,
                "predicate_ref": unit.id,
                "parser": unit.provenance,
                "span": unit.span,
            },
            metadata={
                "cardinality": "zero_or_one_event_ref_per_predicate",
                "event_id_scope": EVENT_ID_SCOPE,
                "event_occurred_claim": occurrence is OccurrenceStatus.ASSERTED_OCCURRED,
            },
        ))
    return tuple(candidates)


def _event_kind(unit: PredicateUnit) -> EventKind | None:
    if unit.predicate == "SAY" or unit.predicate_class == "embedding_say":
        return EventKind.REPORT
    if unit.predicate == "BELIEVE" or unit.predicate_class == "embedding_believe":
        return EventKind.BELIEF
    if unit.predicate_class in _ACTION_CLASSES:
        return EventKind.ACTION
    return None


def _occurrence_status(
    unit: PredicateUnit,
    conditional_sources: set[str],
    units_by_id: Mapping[str, PredicateUnit],
) -> OccurrenceStatus:
    if unit.id in conditional_sources:
        return OccurrenceStatus.CONDITIONAL
    if unit.polarity == "negative" or unit.role == "NEGATED":
        return OccurrenceStatus.NEGATED
    if unit.pragmatic == "HYPOTHETICAL" or unit.epistemic == "HYPOTHETICAL" or unit.role == "HYPOTHETICAL":
        return OccurrenceStatus.HYPOTHETICAL
    if unit.tense_aspect == "FUTURE":
        return OccurrenceStatus.FUTURE
    if unit.modality in {"ABILITY_OR_PERMISSION", "DESIRE", "OBLIGATION", "KNOW_HOW"}:
        return OccurrenceStatus.UNCERTAIN
    if unit.pragmatic == "REPORTED" or unit.epistemic in {"REPORTED", "HEARSAY"}:
        return OccurrenceStatus.REPORTED
    # Belief is epistemic, not occurrence: believed content is never presented
    # as occurred, but the stronger signals above are kept.
    if _under_belief(unit, units_by_id):
        return OccurrenceStatus.UNKNOWN
    if unit.realized is True and unit.polarity == "positive":
        return OccurrenceStatus.ASSERTED_OCCURRED
    if unit.predicate in {"SAY", "BELIEVE"} and unit.pragmatic == "ASSERTED":
        return OccurrenceStatus.ASSERTED_OCCURRED
    return OccurrenceStatus.UNKNOWN


def _under_belief(unit: PredicateUnit, units_by_id: Mapping[str, PredicateUnit]) -> bool:
    if unit.pragmatic == "BELIEVED" or unit.epistemic == "BELIEF" or unit.role == "BELIEVED":
        return True
    seen = {unit.id}
    parent_id = unit.embedded_under
    while parent_id is not None and parent_id not in seen:
        parent = units_by_id.get(parent_id)
        if parent is None:
            return False
        if parent.predicate == "BELIEVE" or parent.predicate_class == "embedding_believe":
            return True
        seen.add(parent_id)
        parent_id = parent.embedded_under
    return False


def _frame_ref(frame: UtteranceFrame) -> str:
    digest = sha256(frame.raw.encode("utf-8")).hexdigest()[:12]
    return f"frame:{digest}"


def _event_id(frame_ref: str, predicate_ref: str, extraction_version: str) -> str:
    seed = f"{frame_ref}|{predicate_ref}|{extraction_version}"
    digest = sha256(seed.encode("utf-8")).hexdigest()[:16]
    return f"event:{digest}"
