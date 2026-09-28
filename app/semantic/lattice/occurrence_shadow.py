"""Read-only shadow comparison: legacy OccurrenceStatus vs OccurrenceClaim (M8-D1).

Reads the parser frame and the legacy EventIndex, builds one OccurrenceInput
per event unit (complements go through their ComplementCommitmentProfile),
derives the new claim and classifies the difference with the frozen M8-D0
vocabulary. It mutates nothing, is not imported by any runtime layer, and the
legacy status is comparison evidence only, never authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.semantic.lattice.complement_commitment import (
    ComplementCommitment,
    ConstructionType,
    ProjectionOperator,
    profile_for,
    resolve_commitment,
)
from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.occurrence_derivation import (
    OccurrenceClaim,
    OccurrenceDerivation,
    OccurrenceInput,
    derive_occurrence,
)
from app.semantic.lattice.primitives import PredicateUnit, RelationKind, UtteranceFrame

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


_FAMILY = {"SAY": "REPORT", "BELIEVE": "BELIEF", "KNOW": "KNOW", "LEARN": "LEARN", "OBSERVE": "PERCEPTION"}
_CONSTRUCTION = {"que": ConstructionType.QUE_PROPOSITION,
                 "que_unresolved_governance": ConstructionType.QUE_PROPOSITION,
                 "observation+inf": ConstructionType.DIRECT_INFINITIVE_PERCEPTION}
_COMPLEMENT_EVIDENCE = frozenset({*_CONSTRUCTION, "que_governor_lost", "modal+inf"})
_COMPLEMENT_KINDS = frozenset({RelationKind.REPORTS.value, RelationKind.BELIEVES.value, RelationKind.FEARS.value,
                               RelationKind.WANTS.value, RelationKind.PREVENTS.value})
_RELATIVE_EVIDENCE = frozenset({"rel", "comparative"})
_IMPLICATIVE_GOVERNORS = frozenset({"FORGET", "HESITATE"})
_DIRECTIVE_PRAGMATICS = frozenset({"REQUESTED", "INDIRECT_REQUEST", "FORBIDDEN"})
_MENTION_ROLES = frozenset({"MENTION", "PURPOSE", "TEMPORAL_CONTEXT", "EXPLANATION_CONTENT"})
_META = frozenset({"SAY", "BELIEVE", "OBSERVE", "LEARN"})
_PERFECTIVE_TENSES = frozenset({"PAST", "PLUPERFECT", "RECENT_PAST"})


@dataclass(frozen=True)
class _Context:
    non_assertive: bool = False
    unresolved: bool = False
    condition: bool = False
    question: bool = False


class _FrameShadow:
    def __init__(self, frame: UtteranceFrame):
        self.frame = frame
        self.units = {u.id: u for u in frame.units}
        self.edges = {(r.source, r.target): r for r in frame.relations}
        self.cond_sources = {r.source for r in frame.relations if r.kind == RelationKind.CONDITIONS.value}
        self.cond_targets = {r.target for r in frame.relations if r.kind == RelationKind.CONDITIONS.value}
        self.temporal = {r.target for r in frame.relations
                         if r.kind == RelationKind.PRECEDES.value and r.evidence == "avant que"}
        self.claims: dict[str, tuple[OccurrenceDerivation, str | None]] = {}
        self.contexts: dict[str, _Context] = {}
        self.visiting: set[str] = set()

    # -- structure ---------------------------------------------------------
    def _edge(self, u: PredicateUnit):
        parent = self.units.get(u.embedded_under) if u.embedded_under else None
        relation = self.edges.get((u.embedded_under, u.id)) if parent else None
        if parent is None:
            return None, None, "root" if u.embedded_under is None else "malformed"
        if relation is None:
            return parent, None, "unknown_edge"
        if relation.evidence in _RELATIVE_EVIDENCE:
            return parent, relation, "relative"
        if relation.evidence == "prep+inf":
            return parent, relation, "prep"
        if relation.evidence in _COMPLEMENT_EVIDENCE or relation.kind in _COMPLEMENT_KINDS:
            return parent, relation, "complement"
        return parent, relation, "unknown_edge"

    def _conditional_role(self, u: PredicateUnit) -> str | None:
        if u.id in self.cond_sources:
            return "source"
        if u.id in self.cond_targets:
            return "target"
        return None

    def _hypothetical(self, u: PredicateUnit) -> bool:
        return u.pragmatic == "HYPOTHETICAL" and u.id not in self.temporal

    def _governor_operators(self, g: PredicateUnit) -> frozenset[ProjectionOperator]:
        ops = set()
        if g.polarity == "negative" or g.role == "NEGATED":
            ops.add(ProjectionOperator.NEGATION)
        if g.pragmatic == "ASKED":
            ops.add(ProjectionOperator.QUESTION)
        if g.tense_aspect in {"FUTURE", "NEAR_FUTURE"}:
            ops.add(ProjectionOperator.FUTURE)
        if g.modality is not None or g.tense_aspect == "CONDITIONAL":
            ops.add(ProjectionOperator.MODAL)
        if self._conditional_role(g) or self._hypothetical(g) or self.context(g).condition:
            ops.add(ProjectionOperator.CONDITION)
        if self.context(g).question:
            ops.add(ProjectionOperator.QUESTION)
        return frozenset(ops)

    def _commitment(self, u: PredicateUnit, parent: PredicateUnit, relation):
        family = _FAMILY.get(parent.predicate)
        construction = _CONSTRUCTION.get(relation.evidence) if relation is not None else None
        profile = profile_for(family, construction) if family and construction else None
        return resolve_commitment(profile, self._governor_operators(parent), source_object_ref=u.id)

    def context(self, u: PredicateUnit) -> _Context:
        """Scope facts inherited by u's descendants (condition, question, attribution, unresolved)."""
        if u.id in self.contexts:
            return self.contexts[u.id]
        if u.id in self.visiting:
            return _Context(unresolved=True)
        self.visiting.add(u.id)
        parent, relation, kind = self._edge(u)
        if parent is None:
            ctx = _Context(unresolved=kind == "malformed")
        else:
            base = self.context(parent)
            non_assertive, unresolved = base.non_assertive, base.unresolved or kind == "unknown_edge"
            if kind == "complement":
                c = self._commitment(u, parent, relation).commitment
                non_assertive = non_assertive or c in {ComplementCommitment.PRESUPPOSED, ComplementCommitment.ATTRIBUTED,
                                                       ComplementCommitment.MENTIONED, ComplementCommitment.QUESTIONED}
                unresolved = unresolved or c is ComplementCommitment.UNRESOLVED
            ctx = _Context(
                non_assertive=non_assertive, unresolved=unresolved,
                condition=base.condition or bool(self._conditional_role(parent)) or self._hypothetical(parent),
                question=base.question or parent.pragmatic == "ASKED")
        self.visiting.discard(u.id)
        self.contexts[u.id] = ctx
        return ctx

    # -- derivation --------------------------------------------------------
    def claim(self, u: PredicateUnit) -> tuple[OccurrenceDerivation, str | None]:
        if u.id in self.claims:
            return self.claims[u.id]
        if u.id in self.visiting:
            res = derive_occurrence(OccurrenceInput(u.id, malformed_ancestry=True))
            return res, None
        self.visiting.add(u.id)
        parent, relation, kind = self._edge(u)
        ctx = self.context(parent) if parent is not None else _Context()
        commitment = None
        parent_claim = None
        if kind == "complement":
            commitment = self._commitment(u, parent, relation)
            if commitment.commitment is ComplementCommitment.ENTAILED:
                parent_claim = self.claim(parent)[0].claim
        directive = u.pragmatic in _DIRECTIVE_PRAGMATICS or u.role in {"REQUEST", "AMBIGUOUS_REQUEST"}
        # "oublier de X" is an implicative without a profile, unless the parser already
        # resolved it as a reminder directive ("n'oublie pas de lancer").
        implicative = kind == "prep" and parent.predicate in _IMPLICATIVE_GOVERNORS and not directive
        role = self._conditional_role(u) or ("ancestry" if parent is not None and (
            ctx.condition or self._conditional_role(parent) or self._hypothetical(parent)) else None)
        inp = OccurrenceInput(
            u.id,
            polarity="negative" if (u.polarity == "negative" or u.role == "NEGATED") else "positive",
            tense_aspect=u.tense_aspect, modality=u.modality, verb_form=u.verb_form,
            directive=directive,
            question=u.pragmatic == "ASKED",
            conditional_role=role, hypothetical=self._hypothetical(u),
            temporal_subordinate=u.id in self.temporal,
            interrogative_ancestry=parent is not None and (ctx.question or parent.pragmatic == "ASKED"),
            attribution_boundary=ctx.non_assertive,
            unresolved_governance=(ctx.unresolved or kind == "unknown_edge" or implicative
                                   # the parser's B2c marker only counts where no profile decides
                                   or (u.epistemic == "UNRESOLVED_GOVERNANCE" and commitment is None)),
            # purpose / mention / temporal-context infinitives and "après avoir X"
            governed_mention=(kind == "prep" and parent.predicate not in _IMPLICATIVE_GOVERNORS)
            or (u.pragmatic == "EMBEDDED" and u.role in _MENTION_ROLES),
            malformed_ancestry=kind == "malformed",
            realization_signal=("PERFECTIVE" if u.tense_aspect in _PERFECTIVE_TENSES else
                                "META_EVENT_PRESENT" if (u.predicate in _META and u.pragmatic == "ASSERTED"
                                                         and u.tense_aspect in {"PRESENT", "PROGRESSIVE"}) else None),
            commitment=commitment, parent_claim=parent_claim,
            provenance={"edge": kind, "governor": parent.predicate if parent is not None else None},
        )
        result = (derive_occurrence(inp), commitment.commitment.value if commitment is not None else None)
        self.visiting.discard(u.id)
        self.claims[u.id] = result
        return result


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
    shadow = _FrameShadow(frame)
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
