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
from typing import AbstractSet, Any, Mapping

from app.semantic.lattice.complement_commitment import StatusDerivation
from app.semantic.lattice.events import EVENT_ID_SCOPE, EventKind, EventRef
from app.semantic.lattice.occurrence_derivation import OccurrenceClaim, OccurrenceDerivation
from app.semantic.lattice.occurrence_projection import FrameOccurrenceProjection
from app.semantic.lattice.primitives import RelationKind, UtteranceFrame, PredicateUnit

EXTRACTION_VERSION = "event_extraction_v0"
_SOURCE = "semantic_event_extraction"

_ACTION_CLASSES = frozenset({
    "world_action",
    "preparatory",
    "inspection",
    "generic_action",
})


# Parser class for a lexicon-unknown verb governing "que + clause"; its
# complement is neither asserted nor classified (fail closed).
_UNRESOLVED_GOVERNOR_CLASS = "unresolved_complement_governor"
# Parser epistemic marker of a complement under a known governor without an
# embedding contract (confirmer / expliquer / savoir + que): fail closed too.
_UNRESOLVED_GOVERNANCE = "UNRESOLVED_GOVERNANCE"

# Speech/cognition acts whose own occurrence the speaker asserts when the
# predicate itself is asserted in a tense presenting it as occurring. Past
# tenses are covered by `realized`; conditional, near-future and averted
# meta-events are not asserted occurrences.
_META_EVENT_PREDICATES = frozenset({"SAY", "BELIEVE", "OBSERVE", "LEARN"})
_OCCURRING_META_TENSES = frozenset({"PRESENT", "PROGRESSIVE"})


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

    `occurrence_status` is the legacy status (compatibility, EventIndex identity
    signature). `occurrence_claim` + `occurrence_derivation` are the canonical
    semantic occurrence projection (M8-D2): a claim about realization at this
    level, never truth, evidence or verification.
    """

    event_ref: EventRef
    predicate_ref: str
    occurrence_status: OccurrenceStatus | str
    extraction_status: ExtractionStatus | str = ExtractionStatus.EXTRACTED
    provenance: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    occurrence_claim: OccurrenceClaim | str | None = None
    occurrence_derivation: StatusDerivation | None = None

    def __post_init__(self) -> None:
        occurrence = self.occurrence_status if isinstance(self.occurrence_status, OccurrenceStatus) else OccurrenceStatus(str(self.occurrence_status))
        extraction = self.extraction_status if isinstance(self.extraction_status, ExtractionStatus) else ExtractionStatus(str(self.extraction_status))
        object.__setattr__(self, "occurrence_status", occurrence)
        object.__setattr__(self, "extraction_status", extraction)
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        if self.occurrence_claim is not None and not isinstance(self.occurrence_claim, OccurrenceClaim):
            object.__setattr__(self, "occurrence_claim", OccurrenceClaim(str(self.occurrence_claim)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_ref": self.event_ref.to_dict(),
            "predicate_ref": self.predicate_ref,
            "occurrence_status": self.occurrence_status.value,
            "extraction_status": self.extraction_status.value,
            "provenance": dict(self.provenance),
            "metadata": dict(self.metadata),
            "occurrence_claim": self.occurrence_claim.value if self.occurrence_claim is not None else None,
            "occurrence_derivation": (self.occurrence_derivation.to_dict()
                                      if self.occurrence_derivation is not None else None),
        }


def extract_event_candidates(
    frame: UtteranceFrame,
    *,
    extraction_version: str = EXTRACTION_VERSION,
) -> tuple[EventCandidate, ...]:
    """Return conservative EventRef candidates for parser-backed predicates."""

    conditional_sources = _conditional_sources(frame)
    conditional_targets = _conditional_targets(frame)
    frame_ref = _frame_ref(frame)
    units_by_id = {unit.id: unit for unit in frame.units}
    projection = FrameOccurrenceProjection(frame)
    candidates: list[EventCandidate] = []
    for unit in frame.units:
        event_kind = _event_kind(unit)
        if event_kind is None:
            continue
        occurrence = _occurrence_status(unit, conditional_sources, units_by_id, conditional_targets)
        claim = projection.claim(unit)[0]
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
            occurrence_claim=claim.claim,
            occurrence_derivation=claim.derivation,
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


def occurrence_claim_for(frame: UtteranceFrame, unit: PredicateUnit) -> OccurrenceDerivation:
    """Canonical OccurrenceClaim of a unit (single adapter: occurrence_projection)."""
    return FrameOccurrenceProjection(frame).claim(unit)[0]


def occurrence_status_for(frame: UtteranceFrame, unit: PredicateUnit) -> OccurrenceStatus:
    """Canonical occurrence classification for any parser-backed PredicateUnit.

    Shared by base, observation and knowledge event extraction so that every
    EventRef built from the same predicate gets the same occurrence status.
    """
    units_by_id = {candidate.id: candidate for candidate in frame.units}
    return _occurrence_status(unit, _conditional_sources(frame), units_by_id, _conditional_targets(frame))


def resolve_epistemic_ancestor_occurrence(
    unit: PredicateUnit,
    units_by_id: Mapping[str, PredicateUnit],
    local_status: OccurrenceStatus,
) -> OccurrenceStatus:
    """Apply the REPORT/BELIEF boundary to a locally derived occurrence status.

    Only a status that would present the event as occurred is affected:
    stronger local signals (conditional, negated, hypothetical, future,
    uncertain, reported, unknown) are returned unchanged. Believed content
    becomes UNKNOWN and reported content REPORTED; the nearest REPORT/BELIEF
    ancestor governs, while LEARN/OBSERVE ancestors are walked through. An
    unresolved complement governor (unknown verb + que), or a complement marked
    UNRESOLVED_GOVERNANCE (known verb without embedding contract), bounds to
    UNKNOWN.
    Malformed ancestry (missing parent, cycle) fails closed to UNKNOWN.
    """
    if local_status is not OccurrenceStatus.ASSERTED_OCCURRED:
        return local_status
    if unit.pragmatic == "BELIEVED" or unit.epistemic in {"BELIEF", _UNRESOLVED_GOVERNANCE}             or unit.role == "BELIEVED":
        return OccurrenceStatus.UNKNOWN
    seen = {unit.id}
    parent_id = unit.embedded_under
    while parent_id is not None:
        parent = units_by_id.get(parent_id)
        if parent_id in seen or parent is None:
            return OccurrenceStatus.UNKNOWN
        kind = _event_kind(parent)
        if kind is EventKind.REPORT:
            return OccurrenceStatus.REPORTED
        if kind is EventKind.BELIEF or parent.predicate_class == _UNRESOLVED_GOVERNOR_CLASS                 or parent.epistemic == _UNRESOLVED_GOVERNANCE:
            return OccurrenceStatus.UNKNOWN
        seen.add(parent_id)
        parent_id = parent.embedded_under
    return local_status


def _occurrence_status(
    unit: PredicateUnit,
    conditional_sources: set[str],
    units_by_id: Mapping[str, PredicateUnit],
    conditional_targets: AbstractSet[str] = frozenset(),
) -> OccurrenceStatus:
    local = _local_occurrence_status(unit, conditional_sources)
    # Consequent of a parser CONDITIONS relation ("si A, B", "B à moins que A"):
    # B only holds under the condition. Stronger local signals (negated,
    # hypothetical, future, uncertain, reported) are kept; only an asserted or
    # unqualified occurrence becomes CONDITIONAL.
    if unit.id in conditional_targets and local in {OccurrenceStatus.ASSERTED_OCCURRED, OccurrenceStatus.UNKNOWN}:
        local = OccurrenceStatus.CONDITIONAL
    return resolve_epistemic_ancestor_occurrence(unit, units_by_id, local)


def _local_occurrence_status(unit: PredicateUnit, conditional_sources: set[str]) -> OccurrenceStatus:
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
    if unit.realized is True and unit.polarity == "positive":
        return OccurrenceStatus.ASSERTED_OCCURRED
    if (unit.predicate in _META_EVENT_PREDICATES and unit.pragmatic == "ASSERTED"
            and unit.tense_aspect in _OCCURRING_META_TENSES and unit.realized is not False):
        return OccurrenceStatus.ASSERTED_OCCURRED
    return OccurrenceStatus.UNKNOWN


def _conditional_sources(frame: UtteranceFrame) -> set[str]:
    return {
        member
        for relation in frame.relations
        if relation.kind == RelationKind.CONDITIONS.value
        for member in frame.relation_members(relation.source)
    }


def _conditional_targets(frame: UtteranceFrame) -> set[str]:
    return {
        member
        for relation in frame.relations
        if relation.kind == RelationKind.CONDITIONS.value
        for member in frame.relation_members(relation.target)
    }


def _frame_ref(frame: UtteranceFrame) -> str:
    digest = sha256(frame.raw.encode("utf-8")).hexdigest()[:12]
    return f"frame:{digest}"


def _event_id(frame_ref: str, predicate_ref: str, extraction_version: str) -> str:
    seed = f"{frame_ref}|{predicate_ref}|{extraction_version}"
    digest = sha256(seed.encode("utf-8")).hexdigest()[:16]
    return f"event:{digest}"
