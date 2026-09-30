"""Cognitive-lattice primitives — immutable, descriptive, non-sovereign.

Names deliberately differ from app.semantic.frame (SemanticFrame /
SemanticRelation are the solver-facing structures and keep their meaning).

One PredicateUnit is ONE cognitive object. Grammatical, semantic, temporal,
causal, epistemic, pragmatic, provenance, world, authority and confidence
positions are projections of that same object (see projections.py), not
copies.

decision_authority: KX108_ONLY · emits_act: false · memory_write: false
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

# Parser ambiguity markers that leave the meaning structure itself unresolved
# (antecedent, attachment, governor, lost structure, bare "ne", unshared negated
# scope, held temporal subordinate, held compound-modal occurrence, open act of a
# negated question operator, possible positive / negative occurrence conflict, open
# scope of a postposed condition over a coordination): they block semantic closure. Speech-act readings kept by fail-closed doctrine
# (ability_permission_or_request, desire_or_request, question_or_request) do not.
STRUCTURAL_AMBIGUITIES = frozenset({
    "ambiguous_antecedent", "coordination_attachment_ambiguous", "complement_governor_lost",
    "complement_structure_lost", "complement_under_unresolved_governor", "unresolved_complement_governance",
    "infinitive_under_unrecognized_governor", "bare_ne", "negated_scope_open",
    "temporal_subordinate_open", "modal_past_occurrence_open", "know_how_scope_open",
    "coordinated_subject_unrepresented", "subject_unresolved", "negated_speech_act_open",
    "occurrence_conflict_open", "condition_scope_ambiguous",
    "deontic_scope_open", "exception_condition_open",
})

BOUNDARY = {
    "readonly": True,
    "non_sovereign": True,
    "decision_authority": "KX108_ONLY",
    "emits_act": False,
    "memory_write": False,
    "kernel_mutation": False,
}


class RelationKind(str, Enum):
    CONTRASTS = "CONTRASTS"
    PRECEDES = "PRECEDES"
    COORDINATES = "COORDINATES"
    ALTERNATIVE = "ALTERNATIVE"
    CAUSES = "CAUSES"
    CONDITIONS = "CONDITIONS"
    FORBIDS = "FORBIDS"
    REPORTS = "REPORTS"
    FEARS = "FEARS"
    PREVENTS = "PREVENTS"
    BELIEVES = "BELIEVES"
    WANTS = "WANTS"
    EMBEDS = "EMBEDS"
    REFERS_TO = "REFERS_TO"


TEMPORAL_KINDS = frozenset({RelationKind.PRECEDES})
PROVENANCE_KINDS = frozenset({RelationKind.REPORTS})
EMBEDDING_KINDS = frozenset({
    RelationKind.REPORTS, RelationKind.FEARS, RelationKind.PREVENTS,
    RelationKind.BELIEVES, RelationKind.WANTS, RelationKind.EMBEDS,
    RelationKind.CONDITIONS,
})


class ConnectionKind(str, Enum):
    """How two objects of the lattice are (or are not) connected."""

    DIRECT_RELATION = "DIRECT_RELATION"
    TEMPORAL_RELATION = "TEMPORAL_RELATION"
    PROVENANCE_RELATION = "PROVENANCE_RELATION"
    SHARED_CAUSE = "SHARED_CAUSE"
    SHARED_ANCESTOR = "SHARED_ANCESTOR"
    INDIRECT_PATH = "INDIRECT_PATH"
    SEMANTIC_SIMILARITY = "SEMANTIC_SIMILARITY"
    NO_PROVEN_CONNECTION = "NO_PROVEN_CONNECTION"


@dataclass(frozen=True)
class Argument:
    text: str                      # folded surface of the argument
    head: str                      # content head ("script", "tests unitaires", "*")
    kind: str                      # NP | PRONOUN | DEMONSTRATIVE | NEGATIVE_QUANTIFIER
    reference: str                 # LITERAL | PRESUPPOSED | DEICTIC | RESOLVED_INTRA | UNRESOLVED
    antecedent: str | None = None  # head of the antecedent when RESOLVED_INTRA
    antecedent_unit: str | None = None
    span: tuple[int, int] | None = None


@dataclass(frozen=True)
class PredicateUnit:
    id: str
    predicate: str                 # canonical, language independent (EXECUTE, PREPARE...)
    lemma: str
    surface: str                   # folded surface of the lexical verb
    span: tuple[int, int]          # character span in the RAW input
    clause: int
    predicate_class: str           # world_action | preparatory | embedding | ...
    verb_form: str                 # FINITE | IMPERATIVE | INFINITIVE | PARTICIPLE | GERUND
    polarity: str = "positive"
    negator: str | None = None
    negation_confirmed: bool = False
    ne_omitted: bool = False
    ne_expletive: bool = False
    restriction: str | None = None         # ONLY | NOT_ONLY
    modality: str | None = None            # ABILITY_OR_PERMISSION | OBLIGATION | DESIRE | KNOW_HOW
    politeness: bool = False
    pragmatic: str = "UNKNOWN"
    tense_aspect: str = "NONE"
    realized: bool | None = None
    epistemic: str = "NOT_APPLICABLE"
    subject: str | None = None
    action_agent: str = "UNKNOWN"
    request_target: str = "NONE"
    role: str = "OTHER"
    objects: tuple[Argument, ...] = ()
    embedded_under: str | None = None
    confidence: float = 1.0
    provenance: str = "builtin_french_grammar_v0"

    @property
    def object(self) -> Argument | None:
        return self.objects[0] if self.objects else None

    @property
    def object_head(self) -> str | None:
        arg = self.object
        if arg is None:
            return None
        if arg.reference == "RESOLVED_INTRA" and arg.antecedent:
            return arg.antecedent
        return arg.head

    def describe(self) -> str:
        bits = [f"{self.id}:{self.predicate}({self.object_head or ''})",
                self.polarity, self.pragmatic]
        for name in ("negator", "restriction", "modality", "tense_aspect"):
            value = getattr(self, name)
            if value and value != "NONE":
                bits.append(f"{name}={value}")
        for name in ("action_agent", "request_target", "role"):
            value = getattr(self, name)
            if value and value not in {"UNKNOWN", "NONE", "OTHER"}:
                bits.append(f"{name}={value}")
        if self.ne_expletive:
            bits.append("ne_expletive")
        if self.ne_omitted:
            bits.append("ne_omitted")
        return " ".join(bits)


@dataclass(frozen=True)
class LatticeRelation:
    kind: str
    source: str
    target: str
    confidence: float = 1.0
    evidence: str = ""

    def describe(self) -> str:
        return f"{self.kind}({self.source}->{self.target})[{self.evidence}]"


@dataclass(frozen=True)
class CoordinationRef:
    """Structural grouping of semantic units ("si P et Q": AND over P, Q).

    Not an event, not an EventCandidate, no occurrence claim: it only states
    that its members are coordinated, so that a relation (e.g. CONDITIONS)
    can take the group as one endpoint without making any member sufficient.
    """
    id: str
    kind: str                       # "AND" | "OR"
    members: tuple[str, ...]        # unit ids, surface order
    construction: str               # e.g. "conditional_protasis"
    evidence: tuple[str, ...] = ()  # connective surface between members
    span: tuple[int, int] | None = None


@dataclass(frozen=True)
class OperatorScopeRef:
    """One written operator scoping over a coordination ("Peux-tu lancer P et exécuter Q ?").

    Not an event, not a coordination, no occurrence claim, no authority: it
    states that one operator scopes over a CoordinationRef, and the speech act
    that operator carries in its context (one act, shared by every member).
    """
    id: str
    kind: str                       # "ABILITY_OR_PERMISSION"
    source: str                     # operator surface ("peux", "pourrais")
    scope: str                      # CoordinationRef id
    speech_act: str                 # "INDIRECT_REQUEST" | "QUESTION" | "NONE"
    target: str = "NONE"            # "ADDRESSEE_OR_POSSIBLE_ADDRESSEE" | "NONE"
    span: tuple[int, int] | None = None


@dataclass(frozen=True)
class UtteranceFrame:
    raw: str
    normalized: str
    units: tuple[PredicateUnit, ...] = ()
    relations: tuple[LatticeRelation, ...] = ()
    constraints: tuple[str, ...] = ()
    surface_act: str = "none"
    unresolved_references: tuple[str, ...] = ()
    presupposed_referents: tuple[str, ...] = ()
    deixis: tuple[str, ...] = ()
    ambiguities: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    evidence_needs: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()
    disfluencies: tuple[str, ...] = ()
    orthography_flags: tuple[str, ...] = ()
    boundary: dict = field(default_factory=lambda: dict(BOUNDARY))
    coordinations: tuple[CoordinationRef, ...] = ()
    operator_scopes: tuple[OperatorScopeRef, ...] = ()

    def coordination(self, ref: str | None) -> CoordinationRef | None:
        return next((c for c in self.coordinations if c.id == ref), None)

    def relation_members(self, ref: str) -> tuple[str, ...]:
        """Unit ids behind a relation endpoint: a CoordinationRef's members, else ref."""
        coordination = self.coordination(ref)
        return coordination.members if coordination is not None else (ref,)

    @property
    def closure_blockers(self) -> tuple[str, ...]:
        """Why the meaning is not resolved yet (empty when it is)."""
        blockers = [f"unresolved_reference:{r}" for r in self.unresolved_references]
        blockers += [f"contradiction:{c}" for c in self.contradictions]
        blockers += [f"missing:{m}" for m in self.missing]
        blockers += [f"ambiguity:{a}" for a in self.ambiguities
                     if a.split(":", 1)[0] in STRUCTURAL_AMBIGUITIES]
        return tuple(blockers)

    @property
    def closure(self) -> bool:
        """Meaning fully resolved from the utterance alone.

        Evidence needs do NOT block semantic closure: "maman est là ?" is
        understood; only its truth value is open.
        """
        return bool(self.units) and not self.closure_blockers

    def unit(self, unit_id: str) -> PredicateUnit:
        for u in self.units:
            if u.id == unit_id:
                return u
        raise KeyError(unit_id)
