"""Pure occurrence claim derivation (M8-D1, shadow only).

OccurrenceClaim answers one question: what does the current semantic / speaker
level claim about the realization of an event? It is not world truth,
verification, evidence, proof, authority or memory truth. This module is pure:
it reads an OccurrenceInput (built elsewhere, read-only) and returns a claim
with its StatusDerivation. It is not imported by the parser, event
extraction, EventIndex, anaphora resolution, ReviewJoin or runtime, and it
never reads or writes the legacy OccurrenceStatus.

Frozen M8-D0 rules:
  * a non-assertive commitment (PRESUPPOSED, ATTRIBUTED, MENTIONED, QUESTIONED)
    makes NO_ASSERTION; an UNRESOLVED commitment is UNRESOLVED;
  * ENTAILED inherits the governor's claim (none -> UNRESOLVED; a negated
    governor does not entail non-realization -> NO_ASSERTION);
  * unresolved governance / malformed ancestry dominate everything (fail closed);
  * dominance: question > non-assertive boundary > condition / hypothesis >
    {negation + future -> PROJECTED_FUTURE}; any other composition involving
    a modal -> UNRESOLVED; no other algebra;
  * NO_ASSERTION (no claim intended) != UNRESOLVED (claim not determinable).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from app.semantic.lattice.complement_commitment import (
    CommitmentResolution,
    ComplementCommitment,
    StatusDerivation,
)

_SOURCE = "occurrence_derivation_v0"


class OccurrenceClaim(str, Enum):
    ASSERTED_REALIZED = "ASSERTED_REALIZED"          # presented as realized; not verified
    ASSERTED_NOT_REALIZED = "ASSERTED_NOT_REALIZED"  # non-realization explicitly posed on X itself
    PROJECTED_FUTURE = "PROJECTED_FUTURE"            # realization presented as still to come (local future)
    CONTINGENT = "CONTINGENT"                        # realization suspended on a condition / hypothesis
    POSSIBLE = "POSSIBLE"                            # presented as possible under an explicit possibility modal
    NO_ASSERTION = "NO_ASSERTION"                    # the level deliberately makes no realization claim
    UNRESOLVED = "UNRESOLVED"                        # a claim is at stake but cannot be safely determined


_PERFECTIVE = "PERFECTIVE"                  # past-family tense on an asserted clause
_META_EVENT_PRESENT = "META_EVENT_PRESENT"  # legacy rule: SAY/BELIEVE/OBSERVE/LEARN in the present occur
_REALIZATION_SIGNALS = frozenset({_PERFECTIVE, _META_EVENT_PRESENT})
_FUTURE_TENSES = frozenset({"FUTURE", "NEAR_FUTURE"})
_NON_ASSERTIVE = frozenset({ComplementCommitment.PRESUPPOSED, ComplementCommitment.ATTRIBUTED,
                            ComplementCommitment.MENTIONED, ComplementCommitment.QUESTIONED})
# Modal flavour -> claim (legacy UNCERTAIN split, M8-D0).
_MODAL_CLAIM = {
    "ABILITY_OR_PERMISSION": OccurrenceClaim.POSSIBLE,
    "OBLIGATION": OccurrenceClaim.UNRESOLVED,   # deontic vs epistemic "devoir"
    "DESIRE": OccurrenceClaim.NO_ASSERTION,
    "KNOW_HOW": OccurrenceClaim.NO_ASSERTION,
}


@dataclass(frozen=True)
class OccurrenceInput:
    """Minimal semantic signals for one event (M8-D0 input contract). No frame, no candidate."""

    source_object_ref: str | None
    # local signals
    polarity: str = "positive"
    tense_aspect: str = "NONE"
    modality: str | None = None
    verb_form: str = "FINITE"
    directive: bool = False
    question: bool = False
    # scope / context
    conditional_role: str | None = None     # "source" | "target" | "ancestry"
    hypothetical: bool = False
    alternative: bool = False               # a branch of "P ou Q": the disjunction is posed, not X
    temporal_subordinate: bool = False      # "avant que X": temporal anchor, not a hypothesis
    interrogative_ancestry: bool = False
    attribution_boundary: bool = False      # inside ATTRIBUTED / MENTIONED / PRESUPPOSED content
    unresolved_governance: bool = False     # unknown / unprofiled governor, implicative, lost governor
    governed_mention: bool = False          # purpose / mention infinitive
    malformed_ancestry: bool = False
    realization_signal: str | None = None
    # semantic projections
    commitment: CommitmentResolution | None = None
    parent_claim: OccurrenceClaim | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.realization_signal is not None and self.realization_signal not in _REALIZATION_SIGNALS:
            raise ValueError(f"unknown realization signal {self.realization_signal!r}")
        if self.parent_claim is not None and not isinstance(self.parent_claim, OccurrenceClaim):
            object.__setattr__(self, "parent_claim", OccurrenceClaim(self.parent_claim))
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))


@dataclass(frozen=True)
class OccurrenceDerivation:
    claim: OccurrenceClaim
    derivation: StatusDerivation

    def to_dict(self) -> dict[str, Any]:
        return {"claim": self.claim.value, "derivation": self.derivation.to_dict()}


def derive_occurrence(inp: OccurrenceInput) -> OccurrenceDerivation:
    """Pure, deterministic: OccurrenceInput -> OccurrenceClaim + StatusDerivation."""
    claim, rule = _derive(inp)
    provenance = {"source": _SOURCE, **dict(inp.provenance)}
    if inp.commitment is not None:
        provenance["commitment"] = inp.commitment.commitment.value
        provenance["commitment_rule"] = inp.commitment.derivation.rule
    return OccurrenceDerivation(claim, StatusDerivation("occurrence", claim.value, rule, inp.source_object_ref,
                                                        provenance))


def _derive(inp: OccurrenceInput) -> tuple[OccurrenceClaim, str]:
    if inp.malformed_ancestry:
        return OccurrenceClaim.UNRESOLVED, "malformed_ancestry"
    if inp.unresolved_governance:
        # Fail closed first: nothing (not even an entailment) resolves under it.
        return OccurrenceClaim.UNRESOLVED, "unresolved_governance"

    if inp.commitment is not None:
        commitment = inp.commitment.commitment
        if commitment is ComplementCommitment.UNRESOLVED:
            return OccurrenceClaim.UNRESOLVED, "commitment:UNRESOLVED"
        if commitment in _NON_ASSERTIVE:
            return OccurrenceClaim.NO_ASSERTION, f"commitment:{commitment.value}"
        if commitment is ComplementCommitment.ENTERTAINED:
            operators = inp.commitment.derivation.provenance.get("operators", [])
            if "CONDITION" in operators:
                return OccurrenceClaim.CONTINGENT, "entertained:condition"
            return OccurrenceClaim.UNRESOLVED, "entertained:unsupported_source"
        if commitment is ComplementCommitment.ENTAILED:
            parent = inp.parent_claim
            if parent is None:
                return OccurrenceClaim.UNRESOLVED, "entailed:no_parent_claim"
            if (inp.modality is not None or inp.polarity == "negative"
                    or inp.tense_aspect in _FUTURE_TENSES | {"AVERTED"}):
                # "voit Paul pouvoir lancer": the entailed event carries its own
                # operator; composing it with the governor's claim is not specified.
                return OccurrenceClaim.UNRESOLVED, "entailed:local_operator_composition"
            if parent is OccurrenceClaim.ASSERTED_NOT_REALIZED:
                # Not perceiving an event does not entail that it did not happen.
                return OccurrenceClaim.NO_ASSERTION, "entailed:parent_not_realized"
            return parent, f"entailed:inherit:{parent.value}"
        # ASSERTED: fall through to the local signals.

    if inp.question or inp.interrogative_ancestry:
        return OccurrenceClaim.NO_ASSERTION, "question"
    if inp.attribution_boundary:
        return OccurrenceClaim.NO_ASSERTION, "attribution_boundary"
    if inp.directive:
        return OccurrenceClaim.NO_ASSERTION, "directive"
    if inp.governed_mention:
        return OccurrenceClaim.NO_ASSERTION, "governed_mention"
    if inp.temporal_subordinate:
        return OccurrenceClaim.NO_ASSERTION, "temporal_subordinate"
    if inp.conditional_role is not None:
        return OccurrenceClaim.CONTINGENT, f"conditional:{inp.conditional_role}"
    if inp.hypothetical:
        return OccurrenceClaim.CONTINGENT, "hypothetical"
    if inp.alternative:
        # ALTERNATIVE != OCCURRENCE: no claim on a branch (nor its local operators);
        # a branch that already makes no claim keeps it
        local = _derive(replace(inp, alternative=False))
        if local[0] is OccurrenceClaim.NO_ASSERTION:
            return local
        return OccurrenceClaim.UNRESOLVED, "alternative"

    negated = inp.polarity == "negative"
    future = inp.tense_aspect in _FUTURE_TENSES
    averted = inp.tense_aspect == "AVERTED"
    if inp.modality is not None:
        others = [name for name, on in (("negation", negated), ("future", future), ("averted", averted)) if on]
        if others:
            return OccurrenceClaim.UNRESOLVED, "multi_operator:modal+" + "+".join(others)
        return _MODAL_CLAIM.get(inp.modality, OccurrenceClaim.UNRESOLVED), f"modal:{inp.modality}"
    if future:
        return OccurrenceClaim.PROJECTED_FUTURE, "negation+future" if negated else "future"
    if averted:
        if negated:
            return OccurrenceClaim.UNRESOLVED, "multi_operator:negation+averted"
        return OccurrenceClaim.ASSERTED_NOT_REALIZED, "averted"
    if negated:
        return OccurrenceClaim.ASSERTED_NOT_REALIZED, "negation"
    if inp.realization_signal == _PERFECTIVE:
        return OccurrenceClaim.ASSERTED_REALIZED, "perfective"
    if inp.realization_signal == _META_EVENT_PRESENT:
        return OccurrenceClaim.ASSERTED_REALIZED, "meta_event_present"
    if inp.tense_aspect == "CONDITIONAL":
        return OccurrenceClaim.UNRESOLVED, "conditional_mood_without_condition"
    return OccurrenceClaim.UNRESOLVED, "no_realization_signal"
