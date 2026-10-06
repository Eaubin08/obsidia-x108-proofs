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
# scope, held temporal subordinate, possible positive / negative occurrence conflict, open
# scope of a postposed condition over a coordination): they block semantic closure. Speech-act readings kept by fail-closed doctrine
# (ability_permission_or_request, desire_or_request, question_or_request) do not, nor
# (H09 / H10) the open act of a negated question operator (negated_speech_act_open): a
# speech-act ambiguity alone never blocks closure; the possible request keeps its gate.
# Nor (H12 option B) modal_past_occurrence_open: "a voulu / a pu / a dû P" leaves the
# occurrence of P canonically UNRESOLVED; that is the final reading, not an incompleteness.
# Nor (H16 option A) deontic_scope_open: "Tu n'as pas à lancer P" keeps both readings
# (absence of obligation / no right) canonically; never NOT_REQUIRED, never FORBIDDEN.
STRUCTURAL_AMBIGUITIES = frozenset({
    "ambiguous_antecedent", "coordination_attachment_ambiguous", "complement_governor_lost",
    "complement_structure_lost", "complement_under_unresolved_governor", "unresolved_complement_governance",
    "infinitive_under_unrecognized_governor", "bare_ne", "negated_scope_open",
    "temporal_subordinate_open", "know_how_scope_open",
    "coordinated_subject_unrepresented", "subject_unresolved",
    "occurrence_conflict_open", "condition_scope_ambiguous",
    "exception_condition_open",
    "temporal_scope_ambiguous",
})

BOUNDARY = {
    "readonly": True,
    "non_sovereign": True,
    "decision_authority": "KX108_ONLY",
    "emits_act": False,
    "memory_write": False,
    "kernel_mutation": False,
}


class SourceClass(str, Enum):
    """Kind of source a content is attributed to (H03). A source class is never an
    epistemic state: none of these means true, verified, supported or observed."""
    HUMAN = "HUMAN"                    # "Selon Marie, P"
    EVIDENCE_TRACE = "EVIDENCE_TRACE"  # "Selon les logs, P": a trace, not a verification
    INFERENCE = "INFERENCE"            # "Apparemment, P" (its epistemic policy is held)
    SPEAKER = "SPEAKER"                # "Selon moi, P"


# parser evidential markers (detached sources) -> source class; nothing else is stamped
_EVIDENTIAL_SOURCE_CLASS = {"HUMAN_SOURCE": SourceClass.HUMAN, "EVIDENCE_SOURCE": SourceClass.EVIDENCE_TRACE,
                            "INFERRED": SourceClass.INFERENCE, "SPEAKER_BELIEF": SourceClass.SPEAKER}


def source_class(unit: "PredicateUnit") -> SourceClass | None:
    """Source class of a unit carrying a detached source marker, else None."""
    return _EVIDENTIAL_SOURCE_CLASS.get(unit.epistemic)


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
    # H05: "quand / lorsque P" temporally anchors its host (no order, condition or cause);
    # "pendant que P" overlaps its host (no exact bounds, no condition or cause)
    TEMPORAL_ANCHOR = "TEMPORAL_ANCHOR"
    OVERLAPS = "OVERLAPS"
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
    # O2: the structurally licensed antecedent Argument of a "qui" relative
    # (reference RESOLVED_INTRA); None when syntax does not prove it
    subject_ref: Argument | None = None
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

    H14 / D5: with member_kind "argument" the members are nominal argument
    mentions of ONE host unit ("Paul et Nadia lancent P", "lance P ou Q"):
    member ids "<host>.s<k>" / "<host>.o<k>", never unit ids. Not a group
    entity and never one event per member; distributivity is UNSPECIFIED
    unless written ("chacun": EXPLICIT).
    """
    id: str
    kind: str                       # "AND" | "OR"
    members: tuple[str, ...]        # unit ids (or argument mention ids), surface order
    construction: str               # e.g. "conditional_protasis"
    evidence: tuple[str, ...] = ()  # connective surface between members
    span: tuple[int, int] | None = None
    member_kind: str = "unit"       # "unit" | "argument"
    host: str | None = None         # argument coordination: the unit whose argument it is
    role: str | None = None         # argument coordination: "subject" | "object"
    member_texts: tuple[str, ...] = ()            # argument coordination: folded surfaces
    member_spans: tuple[tuple[int, int], ...] = ()  # argument coordination: raw spans
    distributivity: str | None = None  # coordinated subject: "UNSPECIFIED" | "EXPLICIT"


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
class ParticipantConfigurationRef:
    """How the participants of ONE predication realize it ("Ils lancent chacun P",
    "Paul et Nadia lancent P ensemble", "Paul lance P tout seul").

    The canonical carrier of participant configuration (CoordinationRef.distributivity
    is only a legacy mirror). Descriptive only: not an event, never one event per
    participant, no group entity, no restriction (ONLY), no authority, no permission.
    """
    id: str
    unit: str                       # the PredicateUnit realized
    role: str                       # "subject"
    kind: str                       # "DISTRIBUTIVE" | "COLLECTIVE" | "SOLO"
    cue: str                        # surface cue ("chacun", "ensemble", "tout seul")
    span: tuple[int, int] | None = None
    group: str | None = None        # coordinated-subject CoordinationRef id, if any


@dataclass(frozen=True)
class MannerRef:
    """A typed adverbial modifier of ONE predication ("Paul lance vite le test", "Paul lance
    le test manuellement").

    Only kinds whose meaning is fixed by the word itself: RATE ("vite / rapidement": FAST,
    "lentement": SLOW; speed in the sense "en peu de temps", which does not fix whether it
    bears on the duration or on the latency of the realization: never a deadline nor a
    temporal anchor) and EXECUTION_MODE ("manuellement": MANUAL, by hand, without
    automation). Modifiers with several readings ("automatiquement": automated mechanism /
    systematically / by reflex; "directement", "indirectement") are not typed: they stay
    reported (unrepresented_modifier_of), frame open. Descriptive only: not an event, no
    occurrence, no request, no permission, no authority.
    """
    id: str
    unit: str                       # the PredicateUnit it modifies
    kind: str                       # "RATE" | "EXECUTION_MODE"
    value: str                      # RATE: "FAST" | "SLOW"; EXECUTION_MODE: "MANUAL"
    cue: str                        # surface cue ("vite", "lentement", "manuellement")
    span: tuple[int, int] | None = None


@dataclass(frozen=True)
class ObliqueArgumentRef:
    """A prepositional (oblique) argument of ONE predication ("Explique Obsidia en utilisant
    ta mémoire", "Lance P sur le serveur").

    The role is licensed by the construction, never by the noun: INSTRUMENT ("en utilisant /
    à l'aide de / au moyen de X"), SOURCE ("à partir de X", X not a temporal cue), else
    UNRESOLVED (structured, not resolved: it blocks closure). A functional source is not an
    epistemic source (SourceClass). Descriptive only: no capability, selection, availability,
    authorization or truth (INSTRUMENT(memory) neither selects nor reads any memory).
    """
    id: str
    unit: str                       # the PredicateUnit it is an argument of
    role: str                       # "SOURCE" | "INSTRUMENT" | "UNRESOLVED"
    marker: str                     # normalized construction ("en utilisant", "à partir de", "avec")
    argument: Argument              # the nominal argument (existing Argument)
    span: tuple[int, int] | None = None  # marker + argument, raw
    group: str | None = None        # argument CoordinationRef id (coordinated_oblique), if any


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
    participant_configurations: tuple[ParticipantConfigurationRef, ...] = ()
    oblique_arguments: tuple[ObliqueArgumentRef, ...] = ()
    manner_modifiers: tuple[MannerRef, ...] = ()

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
        # structured != resolved: an oblique whose role is not licensed keeps the meaning open
        blockers += [f"oblique_role_unresolved:{o.id}" for o in self.oblique_arguments if o.role == "UNRESOLVED"]
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


def request_content_positive(frame: UtteranceFrame, u) -> bool:
    """Whether the possible request of a unit is the positive action: a positive unit, or (H10)
    a negated question operator over a positive content ("Ne peux-tu pas lancer P ?": the
    request reading is "launch P"). A negated content under it stays open (no gate)."""
    return u.polarity == "positive" or (
        u.pragmatic == "INDIRECT_REQUEST"
        and f"negated_speech_act_open:{u.id}" in frame.ambiguities
        and f"negated_scope_open:{u.id}" not in frame.ambiguities)
