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
                 "interrogative_complement": ConstructionType.INTERROGATIVE_COMPLEMENT,
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
# Reportive evidential without a governor unit ("il paraît que P"): the parser
# marks P itself (pragmatic REPORTED at the root; its epistemic HEARSAY may be
# overridden, e.g. COUNTERFACTUAL for "a failli"). It closes the perspective
# like a report; no unit is invented.
_HEARSAY = "HEARSAY"
# Detached source / evidential adverbials marked by the parser on the unit
# itself (B2e); all attributed, speaker opinion through the belief profile.
_SOURCE_EVIDENTIALS = {"HUMAN_SOURCE": "REPORT", "EVIDENCE_SOURCE": "REPORT", "INFERRED": "REPORT",
                       "SPEAKER_BELIEF": "BELIEF"}


@dataclass(frozen=True)
class _Context:
    non_assertive: bool = False
    unresolved: bool = False
    condition: bool = False
    question: bool = False
    # Ancestor unit that introduced each inherited constraint (derivation provenance).
    non_assertive_from: str | None = None
    unresolved_from: str | None = None
    condition_from: str | None = None
    question_from: str | None = None


class FrameOccurrenceProjection:
    def __init__(self, frame: UtteranceFrame):
        self.frame = frame
        self.units = {u.id: u for u in frame.units}
        self.edges = {(r.source, r.target): r for r in frame.relations}
        conditions = [r for r in frame.relations if r.kind == RelationKind.CONDITIONS.value]
        # a coordinated antecedent (CoordinationRef) conditions through its members jointly
        self.cond_sources = {m for r in conditions for m in frame.relation_members(r.source)}
        self.cond_targets = {m for r in conditions for m in frame.relation_members(r.target)}
        self.cond_group = {m: r.source for r in conditions if frame.coordination(r.source) is not None
                           for m in frame.relation_members(r.source)}
        # members negated by a shared "ne ... ni ... ni" coordination
        self.shared_negation = {m: c.id for c in frame.coordinations
                                if c.construction == "ni_negative_coordination" for m in c.members}
        # members whose tense comes from one written, shared auxiliary
        self.shared_tense = {m: c.id for c in frame.coordinations
                             if c.construction in {"shared_auxiliary", "shared_periphrasis"}
                             for m in c.members[1:]}
        self.shared_tense.update({m: c.id for c in frame.coordinations
                                  if c.construction == "ni_negative_coordination" for m in c.members})
        # members whose modality comes from one written, shared modal
        self.shared_modality = {m: c.id for c in frame.coordinations if c.construction == "shared_modality"
                                for m in c.members[1:]}
        self.shared_modality.update({m: c.id for c in frame.coordinations
                                     if c.construction == "ni_negative_coordination" for m in c.members
                                     if self.units[m].modality is not None})
        # members inside the scope of one written directive operator ("veuillez")
        self.shared_directive = {m: c.id for c in frame.coordinations if c.construction == "shared_directive"
                                 for m in c.members}
        # members whose subject comes from one written, shared subject
        self.shared_subject = {m: c.id for c in frame.coordinations if c.construction == "shared_subject"
                               for m in c.members[1:]}
        # members inside the scope of one shared operator ("Peux-tu P et Q ?"): one act
        self.shared_operator = {m: o.id for o in frame.operator_scopes
                                for m in frame.relation_members(o.scope)}
        self.alternative = self._alternative_branches(frame)
        self.modal_past = {a.split(":", 1)[1] for a in frame.ambiguities
                           if a.startswith("modal_past_occurrence_open:")}
        # an exception condition and its possible hosts (held relation, H17): never a claim
        # decided by the missing relation, their occurrence stays unresolved
        self.exception_open = {x for a in frame.ambiguities if a.startswith("exception_condition_open:")
                               for part in a.split(":")[1:] for x in part.removeprefix("host=").split(",")}
        self.temporal = {r.target for r in frame.relations
                         if r.kind == RelationKind.PRECEDES.value and r.evidence == "avant que"}
        # "après que Q": Q is the presupposed temporal anchor (source of PRECEDES), not asserted
        self.temporal |= {r.source for r in frame.relations
                          if r.kind == RelationKind.PRECEDES.value and r.evidence == "après que"}
        # "R et Q avant / après que P" (host held): P keeps its temporal-subordinate status
        self.temporal |= {a.split(":")[1] for a in frame.ambiguities if a.startswith("temporal_scope_ambiguous:")}
        self.claims: dict[str, tuple[OccurrenceDerivation, str | None]] = {}
        self.contexts: dict[str, _Context] = {}
        self.visiting: set[str] = set()

    # -- structure ---------------------------------------------------------
    @staticmethod
    def _alternative_branches(frame: UtteranceFrame) -> dict[str, str]:
        """Branch unit -> OR CoordinationRef id. Units coordinated by "et" with a
        branch are included: the precedence of "ou" over "et" is not decided."""
        links: dict[str, set[str]] = {}
        for r in frame.relations:
            if r.kind == RelationKind.COORDINATES.value:
                for a in frame.relation_members(r.source):
                    for b in frame.relation_members(r.target):
                        links.setdefault(a, set()).add(b)
                        links.setdefault(b, set()).add(a)
        for c in frame.coordinations:
            if c.construction != "disjunction":
                for a in c.members:
                    links.setdefault(a, set()).update(m for m in c.members if m != a)
        out: dict[str, str] = {}
        # the clause-level disjunction names the alternative first; an OR sharing group
        # ("Paul doit lancer P ou exécuter Q") is a root only where no disjunction covers it
        roots = sorted((c for c in frame.coordinations if c.kind == "OR"),
                       key=lambda c: c.construction != "disjunction")
        for c in roots:
            todo = list(c.members)
            while todo:
                m = todo.pop()
                if m not in out:
                    out[m] = c.id
                    todo.extend(links.get(m, ()))
        return out

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

    def _evidential(self, u: PredicateUnit, kind: str) -> str | None:
        if kind == "root" and (u.epistemic == _HEARSAY or u.pragmatic == "REPORTED"):
            return _HEARSAY
        if kind == "root" and u.epistemic in _SOURCE_EVIDENTIALS:
            return u.epistemic
        return None

    def _evidential_commitment(self, u: PredicateUnit):
        profile = profile_for(_SOURCE_EVIDENTIALS.get(u.epistemic, "REPORT"), ConstructionType.QUE_PROPOSITION)
        return resolve_commitment(profile, frozenset(), source_object_ref=u.id)

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

    def complement_commitment(self, u: PredicateUnit, families: set[str] | None = None):
        """Resolved commitment of u as a "que" complement of a profiled governor (optionally
        restricted to governor predicates in families), else None. Read-only."""
        parent, relation, kind = self._edge(u)
        if kind != "complement" or parent is None or (families is not None and parent.predicate not in families):
            return None
        return self._commitment(u, parent, relation)

    def profiled_complement_unresolved(self, u: PredicateUnit, families: set[str] | None = None) -> bool:
        """True when u is a profiled complement whose commitment resolves to UNRESOLVED."""
        resolution = self.complement_commitment(u, families)
        return resolution is not None and resolution.commitment is ComplementCommitment.UNRESOLVED

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
            evidential = self._evidential(u, kind) is not None
            unresolved = kind == "malformed" or u.epistemic == "UNRESOLVED_GOVERNANCE"
            ctx = _Context(unresolved=unresolved, unresolved_from=u.id if unresolved else None,
                           non_assertive=evidential, non_assertive_from=u.id if evidential else None)
        else:
            base = self.context(parent)
            non_assertive, na_from = base.non_assertive, base.non_assertive_from
            unresolved, un_from = base.unresolved, base.unresolved_from
            if kind == "unknown_edge" and not unresolved:
                unresolved, un_from = True, parent.id
            if kind == "complement":
                c = self._commitment(u, parent, relation).commitment
                if not non_assertive and c in {ComplementCommitment.PRESUPPOSED, ComplementCommitment.ATTRIBUTED,
                                               ComplementCommitment.MENTIONED, ComplementCommitment.QUESTIONED}:
                    non_assertive, na_from = True, parent.id
                if not unresolved and c is ComplementCommitment.UNRESOLVED:
                    unresolved, un_from = True, parent.id
            condition_here = bool(self._conditional_role(parent)) or self._hypothetical(parent)
            question_here = parent.pragmatic == "ASKED"
            # the parser's unresolved-governance marker, where no profile decides,
            # scopes over the unit's own descendants
            if not unresolved and kind != "complement" and u.epistemic == "UNRESOLVED_GOVERNANCE":
                unresolved, un_from = True, u.id
            ctx = _Context(
                non_assertive=non_assertive, unresolved=unresolved,
                condition=base.condition or condition_here, question=base.question or question_here,
                non_assertive_from=na_from, unresolved_from=un_from,
                condition_from=base.condition_from or (parent.id if condition_here else None),
                question_from=base.question_from or (parent.id if question_here else None))
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
        evidential = self._evidential(u, kind)
        if kind == "complement":
            commitment = self._commitment(u, parent, relation)
            if commitment.commitment is ComplementCommitment.ENTAILED:
                parent_claim = self.claim(parent)[0].claim
        elif evidential is not None:
            commitment = self._evidential_commitment(u)
        directive = u.pragmatic in _DIRECTIVE_PRAGMATICS or u.role in {"REQUEST", "AMBIGUOUS_REQUEST"}
        # "oublier de X" is an implicative without a profile, unless the parser already
        # resolved it as a reminder directive ("n'oublie pas de lancer").
        implicative = kind == "prep" and parent.predicate in _IMPLICATIVE_GOVERNORS and not directive
        role = self._conditional_role(u) or ("ancestry" if parent is not None and (
            ctx.condition or self._conditional_role(parent) or self._hypothetical(parent)) else None)
        # the parser's B2c marker only counts where no profile decides
        local_unresolved = (kind == "unknown_edge" or implicative or u.id in self.exception_open
                            or (u.epistemic == "UNRESOLVED_GOVERNANCE" and commitment is None))
        interrogative_ancestry = parent is not None and (ctx.question or parent.pragmatic == "ASKED")
        # Name the ancestor behind every inherited value (M8-A derivation contract).
        inherited = {}
        if ctx.unresolved:
            inherited["unresolved_governance"] = ctx.unresolved_from
        elif local_unresolved and parent is not None:
            inherited["unresolved_governance"] = parent.id
        if ctx.non_assertive:
            inherited["attribution_boundary"] = ctx.non_assertive_from
        if interrogative_ancestry:
            inherited["question"] = ctx.question_from or parent.id
        if role == "ancestry":
            inherited["conditional"] = ctx.condition_from or parent.id
        provenance = {"edge": kind, "governor": parent.predicate if parent is not None else None}
        if evidential is not None:
            provenance["evidential"] = evidential
        if u.id in self.cond_group:
            provenance["conditional_group"] = self.cond_group[u.id]
        if u.id in self.shared_negation:
            provenance["shared_negation"] = self.shared_negation[u.id]
        if u.id in self.shared_tense:
            provenance["shared_tense"] = self.shared_tense[u.id]
        if u.id in self.shared_modality:
            provenance["shared_modality"] = self.shared_modality[u.id]
        if u.id in self.shared_directive:
            provenance["shared_directive"] = self.shared_directive[u.id]
        if u.id in self.shared_subject:
            provenance["shared_subject"] = self.shared_subject[u.id]
        if u.id in self.shared_operator:
            provenance["shared_operator"] = self.shared_operator[u.id]
        if u.id in self.alternative:
            provenance["alternative"] = self.alternative[u.id]
        inherited ={k: v for k, v in inherited.items() if v is not None}
        if inherited:
            provenance["inherited_from"] = inherited
        inp = OccurrenceInput(
            u.id,
            polarity="negative" if (u.polarity == "negative" or u.role == "NEGATED") else "positive",
            tense_aspect=u.tense_aspect, modality=u.modality, verb_form=u.verb_form,
            directive=directive,
            question=u.pragmatic == "ASKED",
            conditional_role=role, hypothetical=self._hypothetical(u),
            alternative=u.id in self.alternative,
            temporal_subordinate=u.id in self.temporal, modal_past=u.id in self.modal_past,
            interrogative_ancestry=interrogative_ancestry,
            attribution_boundary=ctx.non_assertive,
            unresolved_governance=ctx.unresolved or local_unresolved,
            # purpose / mention / temporal-context infinitives and "après avoir X"
            governed_mention=(kind == "prep" and parent.predicate not in _IMPLICATIVE_GOVERNORS)
            or (u.pragmatic == "EMBEDDED" and u.role in _MENTION_ROLES)
            # a locally negated infinitive under an unrepresented governor ("Paul aime lancer P
            # et ne pas exécuter Q"): the negation is inside the content, never a root assertion
            or (u.pragmatic == "EMBEDDED" and u.role == "NEGATED" and u.verb_form == "INFINITIVE"
                and u.embedded_under is None),
            malformed_ancestry=kind == "malformed",
            realization_signal=("PERFECTIVE" if u.tense_aspect in _PERFECTIVE_TENSES else
                                "META_EVENT_PRESENT" if (u.predicate in _META and u.pragmatic == "ASSERTED"
                                                         and u.tense_aspect in {"PRESENT", "PROGRESSIVE"}) else None),
            commitment=commitment, parent_claim=parent_claim,
            provenance=provenance,
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
            modal_past=u.id in self.modal_past,
            realization_signal="PERFECTIVE" if u.tense_aspect in _PERFECTIVE_TENSES else None,
            provenance={"level": "holder"}))

    def referable_perspective(self, u: PredicateUnit) -> str | None:
        """Family of the perspective that introduces u as a referable object, if any.

        Only a report, a learning or a propositional perception introduces its
        content as a referable object, and only when the COMPLETE perspective path
        up to the root is referable: any belief, knowledge, unprofiled or unknown
        governor above (or an unknown / malformed edge) closes the path (M8-D2b).
        Relative / infinitive edges are walked through.
        """
        seen = set()
        family = None
        while u.id not in seen:
            seen.add(u.id)
            parent, relation, kind = self._edge(u)
            if parent is None:
                if kind == "root" and self._evidential(u, kind) is not None:
                    return family or "REPORT"
                return family if kind == "root" else None
            if kind == "unknown_edge":
                return None
            if kind == "complement":
                edge_family = _FAMILY.get(parent.predicate)
                construction = _CONSTRUCTION.get(relation.evidence) if relation is not None else None
                if not (edge_family == "REPORT" or (edge_family in {"LEARN", "PERCEPTION"}
                                                    and construction is ConstructionType.QUE_PROPOSITION)):
                    return None
                family = family or edge_family
            u = parent
        return None


def occurrence_projection(frame: UtteranceFrame) -> FrameOccurrenceProjection:
    return FrameOccurrenceProjection(frame)
