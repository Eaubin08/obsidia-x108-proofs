"""Canonical occurrence adapter: parser frame -> OccurrenceClaim per unit (M8-D2).

The ONLY place that turns current semantic structures (PredicateUnit,
LatticeRelation, ComplementCommitmentProfile) into an OccurrenceInput and
calls derive_occurrence(). Event extraction wires its result into
EventCandidate; the shadow comparison and anaphora reuse it. Read-only: it
never mutates the frame nor reads the legacy OccurrenceStatus.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.semantic.lattice.complement_commitment import (
    ComplementCommitment,
    ConstructionType,
    ProjectionOperator,
    profile_for,
    resolve_commitment,
)
from app.semantic.lattice.occurrence_derivation import (
    OccurrenceClaim,
    OccurrenceDerivation,
    OccurrenceInput,
    derive_occurrence,
)
from app.semantic.lattice.primitives import PredicateUnit, RelationKind, UtteranceFrame

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


class FrameOccurrenceProjection:
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

    # -- consumer helpers --------------------------------------------------
    def holder_level_claim(self, u: PredicateUnit) -> OccurrenceDerivation:
        """Claim from u's own local signals only, i.e. inside its holder's perspective."""
        return derive_occurrence(OccurrenceInput(
            u.id,
            polarity="negative" if (u.polarity == "negative" or u.role == "NEGATED") else "positive",
            tense_aspect=u.tense_aspect, modality=u.modality, verb_form=u.verb_form,
            directive=u.pragmatic in _DIRECTIVE_PRAGMATICS or u.role in {"REQUEST", "AMBIGUOUS_REQUEST"},
            question=u.pragmatic == "ASKED", conditional_role=self._conditional_role(u),
            hypothetical=self._hypothetical(u), temporal_subordinate=u.id in self.temporal,
            realization_signal="PERFECTIVE" if u.tense_aspect in _PERFECTIVE_TENSES else None,
            provenance={"level": "holder"}))

    def referable_perspective(self, u: PredicateUnit) -> str | None:
        """Family of the perspective that introduces u as a referable object, if any.

        Walks up relative / infinitive edges to the first complement edge; only a
        report, a learning or a propositional perception introduces its content as
        a referable object (beliefs and unknown governors do not).
        """
        seen = set()
        while u.id not in seen:
            seen.add(u.id)
            parent, relation, kind = self._edge(u)
            if parent is None or kind == "unknown_edge":
                return None
            if kind == "complement":
                family = _FAMILY.get(parent.predicate)
                construction = _CONSTRUCTION.get(relation.evidence) if relation is not None else None
                if family == "REPORT" or (family in {"LEARN", "PERCEPTION"}
                                          and construction is ConstructionType.QUE_PROPOSITION):
                    return family
                return None
            u = parent
        return None


def occurrence_projection(frame: UtteranceFrame) -> FrameOccurrenceProjection:
    return FrameOccurrenceProjection(frame)
