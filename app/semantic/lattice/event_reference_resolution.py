"""Explicit nominal event reference resolution.

This module is intentionally narrow: it resolves only demonstrative
event-nominal references ("ce lancement", "cette observation") inside a single
parser frame. It does not resolve generic pronouns, definite descriptions,
cross-message references, memory-backed references, or graph traversal paths,
and it is not wired into OBSERVES / LEARNS_ABOUT relations.

Candidate admissibility contract (applied before any compatibility or
cardinality check):

- the candidate's EventRef carries a non-null source_frame equal to this
  frame's ref (frame refs are parser-local raw-text hashes, not message ids);
- its predicate_ref names a PredicateUnit of this frame, and any span it
  records matches that unit;
- it is not the event of the predicate governing the reference;
- the antecedent unit ends before the reference starts, and lies in an earlier
  sentence, or in an earlier clause of the same sentence when the governing
  predicate is known.

Compatibility is decided from parser-backed canonical predicates only; event
and predicate identifiers never carry meaning. Generic nominals are never
resolved from cardinality alone, and antecedents whose occurrence status is not
asserted/reported are flagged as occurrence conflicts instead of bound.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from app.semantic.lattice.event_coreference import EventTargetReference, ResolutionStatus, TargetKind
from app.semantic.lattice.event_extraction import EventCandidate
from app.semantic.lattice.events import EventKind
from app.semantic.lattice.occurrence_derivation import OccurrenceClaim
from app.semantic.lattice.occurrence_projection import FrameOccurrenceProjection
from app.semantic.lattice.primitives import PredicateUnit, UtteranceFrame

_SOURCE = "semantic_event_reference_resolution"
_RULE = "explicit_nominal_event_reference"
FRAME_IDENTITY_SCOPE = "parser_local_raw_text_hash"

_GENERIC_EVENT = "generic_event"
_GENERIC_FACT = "generic_fact"
_GENERIC_CLASSES = frozenset({_GENERIC_EVENT, _GENERIC_FACT})

_REFERENCE_TERMS: Mapping[str, str] = MappingProxyType({
    "événement": _GENERIC_EVENT,
    "evenement": _GENERIC_EVENT,
    "action": _GENERIC_EVENT,
    "opération": _GENERIC_EVENT,
    "operation": _GENERIC_EVENT,
    "décision": _GENERIC_EVENT,
    "decision": _GENERIC_EVENT,
    "fait": _GENERIC_FACT,
    "échec": "failure",
    "echec": "failure",
    "réussite": "success",
    "reussite": "success",
    "lancement": "launch",
    "arrêt": "stop",
    "arret": "stop",
    "changement": "change",
    "observation": "observation",
    "rapport": "report",
})

# Bounded canonical-predicate compatibility. A class with no parser-backed
# EventRef today (e.g. failure, stop) simply stays unresolved.
_COMPATIBLE_PREDICATES: Mapping[str, frozenset[str]] = MappingProxyType({
    "failure": frozenset({"FAIL"}),
    "success": frozenset({"SUCCEED"}),
    "launch": frozenset({"EXECUTE"}),
    "stop": frozenset({"STOP"}),
    "change": frozenset({"CHANGE"}),
    "observation": frozenset({"OBSERVE"}),
    "report": frozenset({"SAY"}),
})

_REQUIRED_EVENT_KIND: Mapping[str, EventKind] = MappingProxyType({
    "observation": EventKind.OBSERVATION,
    "report": EventKind.REPORT,
})

# M8-D2: an antecedent is bindable for its semantic reason, not for the legacy
# ASSERTED_OCCURRED / REPORTED overload: either its OccurrenceClaim presents it
# as realized, or an explicit referable perspective (report, learning,
# propositional perception) introduces it as realized inside that perspective.
_BINDABLE_CLAIMS = frozenset({OccurrenceClaim.ASSERTED_REALIZED})


def is_event_reference_bindable(
    candidate: EventCandidate,
    frame: UtteranceFrame,
    projection: FrameOccurrenceProjection | None = None,
) -> tuple[bool, str]:
    """(bindable, reason). Never reads the legacy OccurrenceStatus."""
    claim = candidate.occurrence_claim
    if claim in _BINDABLE_CLAIMS:
        return True, f"occurrence:{claim.value}"
    unit = next((u for u in frame.units if u.id == candidate.predicate_ref), None)
    if unit is not None:
        projection = projection or FrameOccurrenceProjection(frame)
        family = projection.referable_perspective(unit)
        if family is not None and projection.holder_level_claim(unit).claim in _BINDABLE_CLAIMS:
            return True, f"perspective:{family}"
    return False, f"occurrence:{claim.value if claim is not None else 'MISSING'}"

# Only singular demonstratives mark an explicit nominal reference. Definite
# articles (le/la/l') and plurals are not treated as event anaphors.
_MENTION = re.compile(r"\b(ce|cet|cette)\s+([A-Za-zÀ-ÿ]+)(?![A-Za-zÀ-ÿ'])", re.IGNORECASE)
_COMPLEMENTIZER_AFTER = re.compile(r"\s+qu(?:e\b|')", re.IGNORECASE)
_SENTENCE_BREAK = re.compile(r"[.!?](?=\s|$)")


@dataclass(frozen=True)
class ExplicitEventReferenceResult:
    references: tuple[EventTargetReference, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "references", tuple(self.references))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "references": [reference.to_dict() for reference in self.references],
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class _ReferenceMention:
    surface: str
    noun: str
    semantic_class: str
    span: tuple[int, int]
    sentence: int
    governor: PredicateUnit | None

    @property
    def source_clause(self) -> int | None:
        return self.governor.clause if self.governor is not None else None


def resolve_explicit_event_references(
    frame: UtteranceFrame,
    candidates: Sequence[EventCandidate],
) -> ExplicitEventReferenceResult:
    frame_ref = _frame_ref(frame)
    units_by_id = {unit.id: unit for unit in frame.units}
    projection = FrameOccurrenceProjection(frame)
    sentence_breaks = tuple(match.start() for match in _SENTENCE_BREAK.finditer(frame.raw))
    references: list[EventTargetReference] = []
    rejections: dict[str, int] = {}

    for mention in _mentions(frame, sentence_breaks):
        admissible: list[tuple[EventCandidate, PredicateUnit]] = []
        for candidate in candidates:
            unit, reason = _admit(mention, candidate, frame_ref, units_by_id, sentence_breaks)
            if unit is None:
                rejections[reason] = rejections.get(reason, 0) + 1
                continue
            admissible.append((candidate, unit))

        if mention.semantic_class in _GENERIC_CLASSES:
            references.append(_generic_reference(frame_ref, mention, admissible))
            continue

        compatible = [(c, u) for c, u in admissible if _compatible(mention, c, u)]
        if not compatible:
            references.append(_unresolved(frame_ref, mention, reason="no_compatible_antecedent"))
        elif len(compatible) > 1:
            references.append(_ambiguous(frame_ref, mention, compatible, reason="multiple_compatible_antecedents"))
        elif not is_event_reference_bindable(compatible[0][0], frame, projection)[0]:
            references.append(_ambiguous(frame_ref, mention, compatible, reason="antecedent_occurrence_conflict"))
        else:
            references.append(_resolved(frame_ref, mention, *compatible[0]))

    return ExplicitEventReferenceResult(
        references=tuple(references),
        metadata={
            "EXPLICIT_REFERENCES": len(references),
            "REJECTED_CANDIDATES": dict(sorted(rejections.items())),
            "FRAME_IDENTITY_SCOPE": FRAME_IDENTITY_SCOPE,
            "LATEST_EVENT_BINDINGS": 0,
            "NEAREST_EVENT_BINDINGS": 0,
            "PRONOUN_EVENT_BINDINGS": 0,
            "GENERIC_PRONOUN_EVENT_RESOLUTION": 0,
            "META_EVENT_FLATTENING": 0,
            "CROSS_MESSAGE_BINDINGS": 0,
            "MEMORY_WRITE": 0,
            "KX108_CALLED": 0,
        },
    )


def _mentions(frame: UtteranceFrame, sentence_breaks: tuple[int, ...]) -> tuple[_ReferenceMention, ...]:
    raw = frame.raw
    refs: list[_ReferenceMention] = []
    for match in _MENTION.finditer(raw):
        noun = match.group(2).lower()
        semantic_class = _REFERENCE_TERMS.get(noun)
        if semantic_class is None:
            continue
        # "ce fait que X" is a complement construction, not a nominal anaphor.
        if semantic_class == _GENERIC_FACT and _COMPLEMENTIZER_AFTER.match(raw, match.end()):
            continue
        span = match.span()
        refs.append(_ReferenceMention(
            surface=match.group(0).lower(),
            noun=noun,
            semantic_class=semantic_class,
            span=span,
            sentence=_sentence_index(sentence_breaks, span[0]),
            governor=_governor(frame, span),
        ))
    return tuple(refs)


def _governor(frame: UtteranceFrame, span: tuple[int, int]) -> PredicateUnit | None:
    for unit in frame.units:
        for arg in unit.objects:
            if arg.span is not None and arg.span[0] <= span[0] < arg.span[1]:
                return unit
    return None


def _admit(
    mention: _ReferenceMention,
    candidate: EventCandidate,
    frame_ref: str,
    units_by_id: Mapping[str, PredicateUnit],
    sentence_breaks: tuple[int, ...],
) -> tuple[PredicateUnit | None, str]:
    source_frame = candidate.event_ref.source_frame
    if source_frame is None:
        return None, "frame_scope_unknown"
    if source_frame != frame_ref:
        return None, "frame_mismatch"
    if candidate.event_ref.predicate_ref != candidate.predicate_ref:
        return None, "predicate_ref_mismatch"
    unit = units_by_id.get(candidate.predicate_ref)
    if unit is None:
        return None, "predicate_unit_unavailable"
    recorded_span = candidate.provenance.get("span")
    if recorded_span is not None and tuple(recorded_span) != tuple(unit.span):
        return None, "span_mismatch"
    if mention.governor is not None and unit.id == mention.governor.id:
        return None, "governing_event"
    if not unit.span[1] < mention.span[0]:
        return None, "not_prior"
    if _sentence_index(sentence_breaks, unit.span[0]) < mention.sentence:
        return unit, ""
    if mention.governor is not None and unit.clause < mention.governor.clause:
        return unit, ""
    return None, "not_prior_clause"


def _compatible(mention: _ReferenceMention, candidate: EventCandidate, unit: PredicateUnit) -> bool:
    required_kind = _REQUIRED_EVENT_KIND.get(mention.semantic_class)
    if required_kind is not None and candidate.event_ref.event_kind is not required_kind:
        return False
    return unit.predicate in _COMPATIBLE_PREDICATES.get(mention.semantic_class, frozenset())


def _generic_reference(
    frame_ref: str,
    mention: _ReferenceMention,
    admissible: Sequence[tuple[EventCandidate, PredicateUnit]],
) -> EventTargetReference:
    if len(admissible) > 1:
        return _ambiguous(frame_ref, mention, admissible, reason="multiple_admissible_antecedents")
    if admissible:
        return _unresolved(frame_ref, mention, reason="generic_nominal_requires_structural_evidence", candidates=admissible)
    return _unresolved(frame_ref, mention, reason="no_admissible_antecedent")


def _unresolved_target_kind(mention: _ReferenceMention) -> TargetKind:
    if mention.semantic_class == _GENERIC_FACT:
        return TargetKind.PROPOSITION_TARGET
    return TargetKind.UNKNOWN_TARGET


def _base_provenance(frame_ref: str, mention: _ReferenceMention, status: ResolutionStatus) -> dict[str, Any]:
    return {
        "source": _SOURCE,
        "surface_reference": mention.surface,
        "reference_span": mention.span,
        "source_clause": mention.source_clause,
        "governing_predicate_id": mention.governor.id if mention.governor is not None else None,
        "resolution_rule": _RULE,
        "resolution_status": status.value,
        "frame_ref": frame_ref,
        "frame_identity_scope": FRAME_IDENTITY_SCOPE,
    }


def _base_metadata(mention: _ReferenceMention) -> dict[str, Any]:
    return {
        "semantic_class": mention.semantic_class,
        "latest_event_fallback": False,
        "nearest_event_fallback": False,
        "cross_message": False,
    }


def _resolved(
    frame_ref: str,
    mention: _ReferenceMention,
    candidate: EventCandidate,
    unit: PredicateUnit,
) -> EventTargetReference:
    confidence = 0.86
    provenance = _base_provenance(frame_ref, mention, ResolutionStatus.RESOLVED_STRUCTURAL)
    provenance.update({
        "antecedent_span": unit.span,
        "antecedent_predicate_id": candidate.predicate_ref,
        "antecedent_event_id": candidate.event_ref.event_id,
        "antecedent_canonical_predicate": unit.predicate,
        "coreference_confidence": confidence,
    })
    metadata = _base_metadata(mention)
    metadata.update({
        "coreference_confidence": confidence,
        "antecedent_occurrence_status": candidate.occurrence_status.value,  # legacy, compatibility only
        "antecedent_occurrence_claim": _claim_value(candidate),
        "occurrence_conflict": False,
        "occurrence_promoted": False,
    })
    return EventTargetReference(
        source_event=f"reference:{mention.span[0]}:{mention.span[1]}",
        source_predicate=f"reference:{mention.span[0]}:{mention.span[1]}",
        target_kind=TargetKind.EVENT_TARGET,
        resolution_status=ResolutionStatus.RESOLVED_STRUCTURAL,
        target_predicate=candidate.predicate_ref,
        target_event=candidate.event_ref.event_id,
        provenance=provenance,
        confidence={"coreference_confidence": confidence, "calibrated": False},
        metadata=metadata,
    )


def _ambiguous(
    frame_ref: str,
    mention: _ReferenceMention,
    candidates: Sequence[tuple[EventCandidate, PredicateUnit]],
    *,
    reason: str,
) -> EventTargetReference:
    return _unbound(frame_ref, mention, ResolutionStatus.AMBIGUOUS, reason, candidates)


def _unresolved(
    frame_ref: str,
    mention: _ReferenceMention,
    *,
    reason: str,
    candidates: Sequence[tuple[EventCandidate, PredicateUnit]] = (),
) -> EventTargetReference:
    return _unbound(frame_ref, mention, ResolutionStatus.UNRESOLVED, reason, candidates)


def _unbound(
    frame_ref: str,
    mention: _ReferenceMention,
    status: ResolutionStatus,
    reason: str,
    candidates: Sequence[tuple[EventCandidate, PredicateUnit]],
) -> EventTargetReference:
    provenance = _base_provenance(frame_ref, mention, status)
    provenance.update({
        "reason": reason,
        "candidate_event_ids": [candidate.event_ref.event_id for candidate, _ in candidates],
        "candidate_predicate_ids": [candidate.predicate_ref for candidate, _ in candidates],
    })
    metadata = _base_metadata(mention)
    metadata["coreference_confidence"] = 0.0
    if reason == "antecedent_occurrence_conflict":
        metadata["occurrence_conflict"] = True
        metadata["antecedent_occurrence_status"] = candidates[0][0].occurrence_status.value
        metadata["antecedent_occurrence_claim"] = _claim_value(candidates[0][0])
    return EventTargetReference(
        source_event=f"reference:{mention.span[0]}:{mention.span[1]}",
        source_predicate=f"reference:{mention.span[0]}:{mention.span[1]}",
        target_kind=_unresolved_target_kind(mention),
        resolution_status=status,
        target_predicate=None,
        target_event=None,
        provenance=provenance,
        confidence={"coreference_confidence": 0.0, "calibrated": False},
        metadata=metadata,
    )


def _claim_value(candidate: EventCandidate) -> str | None:
    return candidate.occurrence_claim.value if candidate.occurrence_claim is not None else None


def _sentence_index(sentence_breaks: tuple[int, ...], offset: int) -> int:
    return sum(1 for position in sentence_breaks if position < offset)


def _frame_ref(frame: UtteranceFrame) -> str:
    # Must match event_extraction._frame_ref. Parser-local only: identical raw
    # text yields the same ref, so this is not a message identity.
    digest = sha256(frame.raw.encode("utf-8")).hexdigest()[:12]
    return f"frame:{digest}"
