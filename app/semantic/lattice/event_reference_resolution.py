"""Explicit nominal event reference resolution.

This module is intentionally narrow: it resolves only explicit event-nominal
references inside a single utterance/frame when compatible EventRef candidates
are already available. It does not resolve generic pronouns, cross-message
references, memory-backed references, or graph traversal paths.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from app.semantic.lattice.event_coreference import EventTargetReference, ResolutionStatus, TargetKind
from app.semantic.lattice.event_extraction import EventCandidate
from app.semantic.lattice.events import EventKind
from app.semantic.lattice.primitives import PredicateUnit, UtteranceFrame

_SOURCE = "semantic_event_reference_resolution"

_REFERENCE_TERMS: Mapping[str, str] = MappingProxyType({
    "événement": "generic_event",
    "evenement": "generic_event",
    "fait": "generic_fact",
    "échec": "failure",
    "echec": "failure",
    "réussite": "success",
    "reussite": "success",
    "lancement": "launch",
    "arrêt": "stop",
    "arret": "stop",
    "erreur": "failure",
    "crash": "failure",
    "incident": "failure",
    "action": "generic_event",
    "opération": "generic_event",
    "operation": "generic_event",
    "observation": "observation",
    "rapport": "report",
    "décision": "generic_event",
    "decision": "generic_event",
    "changement": "change",
})

_EXPLICIT_MARKERS = frozenset({
    "ce",
    "cet",
    "cette",
    "ces",
    "l'",
    "le",
    "la",
})

_PRONOUNS = frozenset({"ça", "ca", "cela", "ceci", "l'", "le", "la", "en", "y"})


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
    source_clause: int | None


def resolve_explicit_event_references(
    frame: UtteranceFrame,
    candidates: Sequence[EventCandidate],
) -> ExplicitEventReferenceResult:
    frame_ref = _frame_ref(frame)
    units_by_id = {unit.id: unit for unit in frame.units}
    local_candidates = tuple(
        candidate for candidate in candidates
        if _is_frame_local(candidate, frame_ref)
    )
    references: list[EventTargetReference] = []

    for mention in _mentions(frame):
        compatible = tuple(
            candidate for candidate in local_candidates
            if _compatible(mention, candidate, units_by_id)
        )
        if len(compatible) == 1:
            references.append(_resolved_reference(frame, mention, compatible[0], units_by_id))
        elif len(compatible) > 1:
            references.append(_ambiguous_reference(frame, mention, compatible, reason="multiple_compatible_antecedents"))
        else:
            references.append(_unresolved_reference(frame, mention, reason="no_compatible_antecedent"))

    return ExplicitEventReferenceResult(
        references=tuple(references),
        metadata={
            "EXPLICIT_REFERENCES": len(references),
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


def _mentions(frame: UtteranceFrame) -> tuple[_ReferenceMention, ...]:
    raw = frame.raw
    refs: list[_ReferenceMention] = []
    seen: set[tuple[int, int]] = set()
    for match in re.finditer(r"\b(ce|cet|cette|ces|le|la|l')\s+([A-Za-zÀ-ÿ']+)", raw, flags=re.IGNORECASE):
        marker = match.group(1).lower()
        noun = match.group(2).lower()
        if marker not in _EXPLICIT_MARKERS:
            continue
        semantic_class = _REFERENCE_TERMS.get(noun)
        if semantic_class is None:
            continue
        span = match.span()
        seen.add(span)
        refs.append(_ReferenceMention(
            surface=match.group(0).lower(),
            noun=noun,
            semantic_class=semantic_class,
            span=span,
            source_clause=_source_clause(frame, span),
        ))
    # Bare generic pronouns are intentionally ignored rather than converted into
    # references. They stay for a later, explicitly scoped resolver.
    for match in re.finditer(r"\b(ça|ca|cela|ceci|en|y)\b", raw, flags=re.IGNORECASE):
        _ = match
    return tuple(ref for ref in refs if ref.span in seen)


def _is_frame_local(candidate: EventCandidate, frame_ref: str) -> bool:
    source_frame = candidate.event_ref.source_frame
    return source_frame in {None, frame_ref}


def _compatible(
    mention: _ReferenceMention,
    candidate: EventCandidate,
    units_by_id: Mapping[str, PredicateUnit],
) -> bool:
    unit = units_by_id.get(candidate.predicate_ref)
    if mention.semantic_class in {"generic_event", "generic_fact"}:
        return True
    if mention.semantic_class == "observation":
        return candidate.event_ref.event_kind is EventKind.OBSERVATION
    if mention.semantic_class == "report":
        return candidate.event_ref.event_kind is EventKind.REPORT
    if unit is None:
        text = f"{candidate.predicate_ref} {candidate.event_ref.event_id}".lower()
        if mention.semantic_class == "failure":
            return any(token in text for token in ("fail", "failure", "échec", "echec", "crash", "erreur"))
        if mention.semantic_class == "stop":
            return any(token in text for token in ("stop", "arrêt", "arret"))
        if mention.semantic_class == "launch":
            return any(token in text for token in ("launch", "lancement", "execute", "run"))
        if mention.semantic_class == "success":
            return any(token in text for token in ("success", "réussite", "reussite"))
        if mention.semantic_class == "change":
            return any(token in text for token in ("change", "changement"))
        return False
    if mention.semantic_class == "failure":
        return unit.predicate in {"FAIL"} or unit.lemma in {"échouer", "casser"} or unit.object_head in {"erreur", "crash"}
    if mention.semantic_class == "launch":
        return unit.predicate in {"EXECUTE", "PUSH", "DEPLOY"} or unit.predicate_class == "world_action"
    if mention.semantic_class == "stop":
        return unit.predicate == "STOP" or unit.lemma == "arrêter"
    if mention.semantic_class == "success":
        return unit.predicate in {"SUCCEED", "PASS"}
    if mention.semantic_class == "change":
        return unit.predicate == "CHANGE"
    return False


def _resolved_reference(
    frame: UtteranceFrame,
    mention: _ReferenceMention,
    candidate: EventCandidate,
    units_by_id: Mapping[str, PredicateUnit],
) -> EventTargetReference:
    antecedent_unit = units_by_id.get(candidate.predicate_ref)
    return EventTargetReference(
        source_event=f"reference:{mention.span[0]}:{mention.span[1]}",
        source_predicate=f"reference:{mention.span[0]}:{mention.span[1]}",
        target_kind=TargetKind.EVENT_TARGET,
        resolution_status=ResolutionStatus.RESOLVED_STRUCTURAL,
        target_predicate=candidate.predicate_ref,
        target_event=candidate.event_ref.event_id,
        provenance=_provenance(frame, mention, candidate, antecedent_unit, "explicit_nominal_event_reference"),
        confidence={"coreference_confidence": _confidence(mention), "calibrated": False},
        metadata={
            "coreference_confidence": _confidence(mention),
            "semantic_class": mention.semantic_class,
            "latest_event_fallback": False,
            "nearest_event_fallback": False,
            "cross_message": False,
        },
    )


def _ambiguous_reference(
    frame: UtteranceFrame,
    mention: _ReferenceMention,
    candidates: Sequence[EventCandidate],
    *,
    reason: str,
) -> EventTargetReference:
    return EventTargetReference(
        source_event=f"reference:{mention.span[0]}:{mention.span[1]}",
        source_predicate=f"reference:{mention.span[0]}:{mention.span[1]}",
        target_kind=TargetKind.UNKNOWN_TARGET,
        resolution_status=ResolutionStatus.AMBIGUOUS,
        target_predicate=None,
        target_event=None,
        provenance={
            "source": _SOURCE,
            "surface_reference": mention.surface,
            "reference_span": mention.span,
            "source_clause": mention.source_clause,
            "resolution_rule": "explicit_nominal_event_reference",
            "resolution_status": ResolutionStatus.AMBIGUOUS.value,
            "reason": reason,
            "candidate_event_ids": [candidate.event_ref.event_id for candidate in candidates],
            "candidate_predicate_ids": [candidate.predicate_ref for candidate in candidates],
        },
        confidence={"coreference_confidence": 0.0, "calibrated": False},
        metadata={
            "coreference_confidence": 0.0,
            "semantic_class": mention.semantic_class,
            "latest_event_fallback": False,
            "nearest_event_fallback": False,
        },
    )


def _unresolved_reference(
    frame: UtteranceFrame,
    mention: _ReferenceMention,
    *,
    reason: str,
) -> EventTargetReference:
    return EventTargetReference(
        source_event=f"reference:{mention.span[0]}:{mention.span[1]}",
        source_predicate=f"reference:{mention.span[0]}:{mention.span[1]}",
        target_kind=TargetKind.UNKNOWN_TARGET,
        resolution_status=ResolutionStatus.UNRESOLVED,
        target_predicate=None,
        target_event=None,
        provenance={
            "source": _SOURCE,
            "surface_reference": mention.surface,
            "reference_span": mention.span,
            "source_clause": mention.source_clause,
            "resolution_rule": "explicit_nominal_event_reference",
            "resolution_status": ResolutionStatus.UNRESOLVED.value,
            "reason": reason,
            "frame_ref": _frame_ref(frame),
        },
        confidence={"coreference_confidence": 0.0, "calibrated": False},
        metadata={
            "coreference_confidence": 0.0,
            "semantic_class": mention.semantic_class,
            "latest_event_fallback": False,
            "nearest_event_fallback": False,
        },
    )


def _provenance(
    frame: UtteranceFrame,
    mention: _ReferenceMention,
    candidate: EventCandidate,
    antecedent_unit: PredicateUnit | None,
    rule: str,
) -> dict[str, Any]:
    antecedent_span = antecedent_unit.span if antecedent_unit is not None else candidate.event_ref.provenance.get("span")
    return {
        "source": _SOURCE,
        "surface_reference": mention.surface,
        "reference_span": mention.span,
        "source_clause": mention.source_clause,
        "antecedent_span": antecedent_span,
        "antecedent_predicate_id": candidate.predicate_ref,
        "antecedent_event_id": candidate.event_ref.event_id,
        "resolution_rule": rule,
        "resolution_status": ResolutionStatus.RESOLVED_STRUCTURAL.value,
        "coreference_confidence": _confidence(mention),
        "frame_ref": _frame_ref(frame),
    }


def _confidence(mention: _ReferenceMention) -> float:
    if mention.semantic_class in {"generic_event", "generic_fact"}:
        return 0.72
    return 0.86


def _source_clause(frame: UtteranceFrame, span: tuple[int, int]) -> int | None:
    for unit in frame.units:
        if unit.span[0] <= span[0] <= unit.span[1]:
            return unit.clause
        for arg in unit.objects:
            if arg.span is not None and arg.span[0] <= span[0] <= arg.span[1]:
                return unit.clause
    if "." in frame.raw[:span[0]]:
        return frame.raw[:span[0]].count(".")
    return None


def _frame_ref(frame: UtteranceFrame) -> str:
    from hashlib import sha256

    digest = sha256(frame.raw.encode("utf-8")).hexdigest()[:12]
    return f"frame:{digest}"
