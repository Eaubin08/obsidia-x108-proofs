"""Read-only shadow comparison: legacy OccurrenceStatus vs OccurrenceClaim (M8-D1).

Reads the legacy EventIndex, takes each event's claim from the canonical
occurrence adapter (occurrence_projection) and classifies the difference with
the frozen M8-D0 vocabulary. It mutates nothing, and the legacy status is
comparison evidence only, never authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.occurrence_derivation import OccurrenceClaim
from app.semantic.lattice.occurrence_projection import FrameOccurrenceProjection
from app.semantic.lattice.primitives import UtteranceFrame

O = OccurrenceClaim


class ShadowClass(str, Enum):
    SAME_SEMANTIC_MEANING = "SAME_SEMANTIC_MEANING"
    EXPECTED_WEAKENING = "EXPECTED_WEAKENING"
    EXPECTED_DIMENSION_MOVE = "EXPECTED_DIMENSION_MOVE"
    LEGACY_UNRESOLVED_NEW_MODEL_EXPLICIT = "LEGACY_UNRESOLVED_NEW_MODEL_EXPLICIT"
    NEW_MODEL_UNRESOLVED = "NEW_MODEL_UNRESOLVED"
    UNEXPECTED_DIFFERENCE = "UNEXPECTED_DIFFERENCE"


@dataclass(frozen=True)
class ShadowRecord:
    source_ref: str
    predicate: str
    legacy_occurrence: str
    new_commitment: str | None
    new_occurrence_claim: OccurrenceClaim
    classification: ShadowClass
    derivation_rule: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return {"source_ref": self.source_ref, "predicate": self.predicate,
                "legacy_occurrence": self.legacy_occurrence, "new_commitment": self.new_commitment,
                "new_occurrence_claim": self.new_occurrence_claim.value,
                "classification": self.classification.value, "derivation_rule": self.derivation_rule,
                "notes": self.notes}


# (legacy, claim) pairs that mean the same thing at their respective level.
_SAME = frozenset({
    ("ASSERTED_OCCURRED", O.ASSERTED_REALIZED), ("NEGATED", O.ASSERTED_NOT_REALIZED),
    ("FUTURE", O.PROJECTED_FUTURE), ("CONDITIONAL", O.CONTINGENT), ("HYPOTHETICAL", O.CONTINGENT),
    ("UNCERTAIN", O.POSSIBLE), ("UNKNOWN", O.UNRESOLVED), ("UNKNOWN", O.NO_ASSERTION),
})
# Rules whose NO_ASSERTION moves the information to another dimension.
_DIMENSION_MOVE_RULES = ("commitment:ATTRIBUTED", "commitment:MENTIONED", "commitment:QUESTIONED",
                         "attribution_boundary", "directive", "temporal_subordinate", "modal:DESIRE",
                         "modal:KNOW_HOW", "question", "governed_mention")
_WEAKENING_RULES = ("commitment:PRESUPPOSED", "conditional:", "hypothetical", "entertained:condition")
# Legacy gaps the new model may make explicit (legacy UNKNOWN -> explicit claim).
_EXPLICIT_RULES = ("future", "negation+future", "averted", "entailed:inherit:", "modal:ABILITY_OR_PERMISSION",
                   "conditional:", "hypothetical", "entertained:condition")


def classify_shadow(legacy: str, claim: OccurrenceClaim, rule: str) -> tuple[ShadowClass, str]:
    """Classify one legacy/new pair with the rule that produced the new claim."""
    if (legacy, claim) in _SAME:
        return ShadowClass.SAME_SEMANTIC_MEANING, f"legacy {legacy} and {claim.value} agree ({rule})"
    if claim is O.UNRESOLVED:
        return ShadowClass.NEW_MODEL_UNRESOLVED, f"legacy {legacy} not safely derivable: {rule}"
    if legacy == "UNKNOWN":
        if rule.startswith(_EXPLICIT_RULES):
            return ShadowClass.LEGACY_UNRESOLVED_NEW_MODEL_EXPLICIT, f"legacy gap made explicit by {rule}"
        return ShadowClass.UNEXPECTED_DIFFERENCE, f"legacy UNKNOWN strengthened by unlisted rule {rule}"
    if legacy == "REPORTED" and claim is O.NO_ASSERTION:
        return ShadowClass.EXPECTED_DIMENSION_MOVE, f"REPORTED moves to perspective ({rule})"
    if legacy == "NEGATED" and claim is O.PROJECTED_FUTURE and rule == "negation+future":
        return ShadowClass.EXPECTED_DIMENSION_MOVE, "negation kept as polarity under a projected future"
    if claim is O.NO_ASSERTION and rule.startswith(_DIMENSION_MOVE_RULES):
        return ShadowClass.EXPECTED_DIMENSION_MOVE, f"legacy {legacy}: no realization claim at this level ({rule})"
    if claim in {O.NO_ASSERTION, O.CONTINGENT} and rule.startswith(_WEAKENING_RULES):
        return ShadowClass.EXPECTED_WEAKENING, f"legacy {legacy} weakened to {claim.value} by {rule}"
    return ShadowClass.UNEXPECTED_DIFFERENCE, f"legacy {legacy} vs {claim.value} under {rule}"


def shadow_frame(frame: UtteranceFrame) -> tuple[ShadowRecord, ...]:
    """One record per legacy event of the frame, in unit order. Read-only."""
    index = build_frame_event_index(frame)
    shadow = FrameOccurrenceProjection(frame)
    records = []
    for u in frame.units:
        event = index.event_for(u.id)
        if event is None:
            continue
        result, commitment = shadow.claim(u)
        legacy = event.occurrence_status.value
        klass, note = classify_shadow(legacy, result.claim, result.derivation.rule)
        records.append(ShadowRecord(u.id, u.predicate, legacy, commitment, result.claim, klass,
                                    result.derivation.rule, note))
    return tuple(records)
