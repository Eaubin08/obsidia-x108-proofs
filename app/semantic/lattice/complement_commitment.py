"""Complement commitment profiles and status derivation (M8-C, V0).

A ComplementCommitmentProfile describes, for one governor family AND one
construction type, how the construction presents its complement X (linguistic
commitment) and how that commitment survives each scope operator. It is
descriptive semantic doctrine, not action authority, and is not wired into the
parser, events, ReviewJoin or runtime.

Hard invariants:
  commitment != occurrence   (no OccurrenceStatus is read or produced here)
  commitment != truth        (PRESUPPOSED / ENTAILED never mean true)
  commitment != evidence
  commitment != verification (never VERIFIED / PROVED)
  commitment != authority    (no action, no KX108, no memory write)

Fail closed: an unknown family / construction, an open doctrine cell or an
operator composition the doctrine does not specify resolves to UNRESOLVED,
never to ASSERTED / PRESUPPOSED / ENTAILED. Every resolution carries a
StatusDerivation that says why the value exists.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import AbstractSet, Any, Mapping

_SOURCE = "complement_commitment_v0"


class ComplementCommitment(str, Enum):
    """How the construction presents X. None of these values means true, false,
    verified, proved, occurred or authorized."""

    ASSERTED = "ASSERTED"          # the speaker puts X forward
    PRESUPPOSED = "PRESUPPOSED"    # X is backgrounded as given by the construction
    ENTAILED = "ENTAILED"          # X holds if the governing clause holds (no projection)
    ATTRIBUTED = "ATTRIBUTED"      # X is the content of a holder's attitude, not the speaker's
    MENTIONED = "MENTIONED"        # X is evoked; nobody is committed to it
    ENTERTAINED = "ENTERTAINED"    # X is considered under a conditional / hypothetical frame
    QUESTIONED = "QUESTIONED"      # X is the issue of a question
    UNRESOLVED = "UNRESOLVED"      # doctrine, sense or governor not established


class ProjectionRule(str, Enum):
    PROJECT = "PROJECT"        # the base commitment survives the operator
    BLOCK = "BLOCK"            # it does not survive: X is only MENTIONED
    CHANGE = "CHANGE"          # it becomes the explicit target commitment
    UNRESOLVED = "UNRESOLVED"  # doctrine open: X is UNRESOLVED


class ProjectionOperator(str, Enum):
    NEGATION = "NEGATION"
    QUESTION = "QUESTION"
    FUTURE = "FUTURE"
    MODAL = "MODAL"
    CONDITION = "CONDITION"
    COUNTERFACTUAL = "COUNTERFACTUAL"


class ConstructionType(str, Enum):
    QUE_PROPOSITION = "QUE_PROPOSITION"                            # G que X
    INTERROGATIVE_COMPLEMENT = "INTERROGATIVE_COMPLEMENT"          # G wh X
    DIRECT_INFINITIVE_PERCEPTION = "DIRECT_INFINITIVE_PERCEPTION"  # voir Y faire


class PerspectiveKind(str, Enum):
    """Holder -> X relation kind (not EventRelationKind: KNOWS / REMEMBERS have no event relation)."""

    SAYS = "SAYS"
    BELIEVES = "BELIEVES"
    KNOWS = "KNOWS"
    LEARNS = "LEARNS"
    REMEMBERS = "REMEMBERS"
    PERCEIVES_EVENT = "PERCEIVES_EVENT"
    PERCEIVES_THAT = "PERCEIVES_THAT"


class PerspectiveStance(str, Enum):
    NEUTRAL = "NEUTRAL"
    ADHERE = "ADHERE"
    REJECT = "REJECT"
    EMOTIVE = "EMOTIVE"
    UNRESOLVED = "UNRESOLVED"


class DoctrineStatus(str, Enum):
    CLOSED_V0 = "CLOSED_V0"
    PARTIAL_V0 = "PARTIAL_V0"
    UNRESOLVED = "UNRESOLVED"
    EXTERNAL_VALIDATION_NEEDED = "EXTERNAL_VALIDATION_NEEDED"


@dataclass(frozen=True)
class OperatorCell:
    """Behaviour of the complement commitment under one operator."""

    rule: ProjectionRule
    target: ComplementCommitment | None = None
    status: DoctrineStatus = DoctrineStatus.UNRESOLVED
    cancellable: bool = False  # a projected presupposition that context may cancel

    def __post_init__(self) -> None:
        if (self.rule is ProjectionRule.CHANGE) != (self.target is not None):
            raise ValueError("CHANGE requires an explicit target commitment, other rules none")


_OPEN = OperatorCell(ProjectionRule.UNRESOLVED, None, DoctrineStatus.UNRESOLVED)
_EXT = OperatorCell(ProjectionRule.UNRESOLVED, None, DoctrineStatus.EXTERNAL_VALIDATION_NEEDED)


@dataclass(frozen=True)
class ComplementCommitmentProfile:
    governor_family: str
    construction_type: ConstructionType
    base_commitment: ComplementCommitment
    base_status: DoctrineStatus
    perspective_kind: PerspectiveKind
    stance: PerspectiveStance
    negation_projection: OperatorCell = _OPEN
    question_projection: OperatorCell = _OPEN
    future_projection: OperatorCell = _OPEN
    modal_projection: OperatorCell = _OPEN
    conditional_projection: OperatorCell = _OPEN
    counterfactual_projection: OperatorCell = _OPEN

    @property
    def key(self) -> str:
        return f"{self.governor_family}/{self.construction_type.value}"

    def cell(self, operator: ProjectionOperator) -> OperatorCell:
        return {
            ProjectionOperator.NEGATION: self.negation_projection,
            ProjectionOperator.QUESTION: self.question_projection,
            ProjectionOperator.FUTURE: self.future_projection,
            ProjectionOperator.MODAL: self.modal_projection,
            ProjectionOperator.CONDITION: self.conditional_projection,
            ProjectionOperator.COUNTERFACTUAL: self.counterfactual_projection,
        }[operator]


@dataclass(frozen=True)
class StatusDerivation:
    """Why a semantic status value exists. Provenance of a rule, never evidence of truth."""

    dimension: str
    value: str
    rule: str
    source_object_ref: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.dimension or not self.rule:
            raise ValueError("dimension and rule are required")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "value": self.value,
            "rule": self.rule,
            "source_object_ref": self.source_object_ref,
            "provenance": dict(self.provenance),
        }


@dataclass(frozen=True)
class CommitmentResolution:
    commitment: ComplementCommitment
    derivation: StatusDerivation

    def to_dict(self) -> dict[str, Any]:
        return {"commitment": self.commitment.value, "derivation": self.derivation.to_dict()}


def _closed(rule: ProjectionRule, target: ComplementCommitment | None = None, *,
            cancellable: bool = False) -> OperatorCell:
    return OperatorCell(rule, target, DoctrineStatus.CLOSED_V0, cancellable)


_C, _R, _Q = ComplementCommitment, ProjectionRule, ConstructionType.QUE_PROPOSITION
_WH = ConstructionType.INTERROGATIVE_COMPLEMENT


def _attribution(family: str, kind: PerspectiveKind) -> ComplementCommitmentProfile:
    # REPORT / BELIEF (M8-B CLOSED): X attributed to the holder; a negated holder
    # relation leaves X merely mentioned ("ne croit pas que X" != "croit que non-X").
    return ComplementCommitmentProfile(
        family, _Q, _C.ATTRIBUTED, DoctrineStatus.CLOSED_V0, kind, PerspectiveStance.ADHERE,
        negation_projection=_closed(_R.CHANGE, _C.MENTIONED),
        question_projection=_closed(_R.PROJECT),
        future_projection=_closed(_R.PROJECT),
        modal_projection=_closed(_R.PROJECT),
        conditional_projection=_closed(_R.PROJECT),  # the condition stays on the perspective / scope
        counterfactual_projection=_EXT,
    )


def _base_only(family: str, kind: PerspectiveKind) -> ComplementCommitmentProfile:
    # M8-B: only the base cell is safe; every operator stays open in V0.
    return ComplementCommitmentProfile(
        family, _Q, _C.PRESUPPOSED, DoctrineStatus.PARTIAL_V0, kind, PerspectiveStance.UNRESOLVED,
        negation_projection=_EXT, question_projection=_EXT, future_projection=_EXT,
        modal_projection=_EXT, conditional_projection=_OPEN, counterfactual_projection=_EXT,
    )


_PROFILES = (
    _attribution("REPORT", PerspectiveKind.SAYS),
    _attribution("BELIEF", PerspectiveKind.BELIEVES),
    ComplementCommitmentProfile(
        "KNOW", _Q, _C.PRESUPPOSED, DoctrineStatus.CLOSED_V0, PerspectiveKind.KNOWS, PerspectiveStance.ADHERE,
        negation_projection=_closed(_R.PROJECT, cancellable=True),
        question_projection=_closed(_R.PROJECT),
        future_projection=_EXT, modal_projection=_EXT,
        conditional_projection=_OPEN,  # no escape from the protasis in V0
        counterfactual_projection=_EXT,
    ),
    ComplementCommitmentProfile(
        "KNOW", _WH, _C.QUESTIONED, DoctrineStatus.CLOSED_V0, PerspectiveKind.KNOWS, PerspectiveStance.ADHERE,
        negation_projection=_closed(_R.PROJECT),
        question_projection=_closed(_R.PROJECT),
        future_projection=_EXT, modal_projection=_EXT,
        conditional_projection=_OPEN,
        counterfactual_projection=_EXT,
    ),
    _base_only("LEARN", PerspectiveKind.LEARNS),
    _base_only("REMEMBER", PerspectiveKind.REMEMBERS),
    _base_only("PERCEPTION", PerspectiveKind.PERCEIVES_THAT),
    ComplementCommitmentProfile(
        # Linguistic entailment of the perceived event, not world / sensor verification.
        "PERCEPTION", ConstructionType.DIRECT_INFINITIVE_PERCEPTION, _C.ENTAILED, DoctrineStatus.CLOSED_V0,
        PerspectiveKind.PERCEIVES_EVENT, PerspectiveStance.NEUTRAL,
        negation_projection=_closed(_R.BLOCK),
        question_projection=_closed(_R.BLOCK),
        future_projection=_closed(_R.PROJECT),
        modal_projection=_closed(_R.PROJECT),
        conditional_projection=_closed(_R.CHANGE, _C.ENTERTAINED),
        counterfactual_projection=_EXT,
    ),
)

# Closed world: (governor family, construction type) -> profile. No fallback.
SAFE_PROFILES: Mapping[tuple[str, str], ComplementCommitmentProfile] = MappingProxyType(
    {(p.governor_family, p.construction_type.value): p for p in _PROFILES})


def profile_for(governor_family: Any, construction_type: Any) -> ComplementCommitmentProfile | None:
    """Exact registry lookup; anything unknown (family, sense, construction) -> None."""
    construction = construction_type.value if isinstance(construction_type, ConstructionType) else construction_type
    if not isinstance(governor_family, str) or not isinstance(construction, str):
        return None
    return SAFE_PROFILES.get((governor_family, construction))


def resolve_commitment(
    profile: ComplementCommitmentProfile | None,
    operators: AbstractSet[ProjectionOperator],
    *,
    source_object_ref: str | None = None,
) -> CommitmentResolution:
    """Apply a profile to the operators scoping its governor. Pure and deterministic."""
    ops = sorted(ProjectionOperator(o) for o in operators)
    names = [o.value for o in ops]

    def done(value: ComplementCommitment, rule: str, **extra: Any) -> CommitmentResolution:
        provenance = {"source": _SOURCE, "profile": profile.key if profile else None, "operators": names, **extra}
        return CommitmentResolution(value, StatusDerivation("commitment", value.value, rule, source_object_ref,
                                                            provenance))

    if profile is None:
        return done(ComplementCommitment.UNRESOLVED, "no_profile", doctrine_status=DoctrineStatus.UNRESOLVED.value)
    if not ops:
        return done(profile.base_commitment, f"{profile.key}:base", doctrine_status=profile.base_status.value)
    if len(ops) > 1:
        # The doctrine specifies single operators only: no composition algebra is invented.
        return done(ComplementCommitment.UNRESOLVED, f"{profile.key}:operator_composition_unspecified",
                    doctrine_status=DoctrineStatus.UNRESOLVED.value)
    operator = ops[0]
    cell = profile.cell(operator)
    rule = f"{profile.key}:{operator.value}:{cell.rule.value}"
    if cell.rule is ProjectionRule.PROJECT:
        value = profile.base_commitment
    elif cell.rule is ProjectionRule.BLOCK:
        value = ComplementCommitment.MENTIONED
    elif cell.rule is ProjectionRule.CHANGE:
        value = cell.target
    else:
        value = ComplementCommitment.UNRESOLVED
    return done(value, rule, doctrine_status=cell.status.value, cancellable=cell.cancellable)
