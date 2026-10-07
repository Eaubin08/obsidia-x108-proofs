"""F18 Science / Constraint Engine V0.

Minimal scientific constraint grammar for specialized engines.
No monolithic physics brain, no automatic truth promotion, no authority.

This layer can represent models, equations, invariants, constraints, candidate
predictions and bounded assessments against explicit evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConstraintStatusV0(str, Enum):
    SATISFIED = "SATISFIED"
    VIOLATED = "VIOLATED"
    UNKNOWN = "UNKNOWN"


class PossibilityStatusV0(str, Enum):
    POSSIBLE = "POSSIBLE"
    IMPOSSIBLE = "IMPOSSIBLE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ScientificModelRefV0:
    model_ref: str
    domain: str
    version_ref: str | None = None
    source_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.model_ref or not self.domain:
            raise ValueError("scientific model requires model_ref and domain")


@dataclass(frozen=True)
class ScientificEquationRefV0:
    equation_ref: str
    model_ref: str
    symbol_refs: tuple[str, ...] = ()
    unit_constraints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.equation_ref or not self.model_ref:
            raise ValueError("scientific equation requires equation_ref and model_ref")


@dataclass(frozen=True)
class ScientificInvariantV0:
    invariant_id: str
    statement: str
    model_ref: str | None = None
    equation_refs: tuple[str, ...] = ()
    proof_refs: tuple[str, ...] = ()
    assumed: bool = False

    def __post_init__(self) -> None:
        if not self.invariant_id or not self.statement:
            raise ValueError("scientific invariant requires identity and statement")
        if not self.assumed and not self.proof_refs:
            raise ValueError("non-assumed scientific invariant requires proof_refs")


@dataclass(frozen=True)
class ScientificConstraintV0:
    constraint_id: str
    statement: str
    model_ref: str | None = None
    equation_refs: tuple[str, ...] = ()
    invariant_refs: tuple[str, ...] = ()
    scope_refs: tuple[str, ...] = ()
    reversible: bool | None = None

    def __post_init__(self) -> None:
        if not self.constraint_id or not self.statement:
            raise ValueError("scientific constraint requires identity and statement")


@dataclass(frozen=True)
class ScientificPredictionCandidateV0:
    prediction_id: str
    statement: str
    model_ref: str
    expected_observable_refs: tuple[str, ...]
    condition_refs: tuple[str, ...] = ()
    equation_refs: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()
    candidate_only: bool = True

    def __post_init__(self) -> None:
        if not self.prediction_id or not self.statement or not self.model_ref:
            raise ValueError("scientific prediction requires identity, statement and model")
        if not self.expected_observable_refs:
            raise ValueError("scientific prediction requires expected observable refs")
        if not self.candidate_only:
            raise ValueError("scientific prediction must remain candidate until tested")


@dataclass(frozen=True)
class ConstraintAssessmentV0:
    assessment_id: str
    constraint_ref: str
    status: ConstraintStatusV0
    possibility: PossibilityStatusV0 = PossibilityStatusV0.UNKNOWN
    evidence_refs: tuple[str, ...] = ()
    contradiction_refs: tuple[str, ...] = ()
    model_ref: str | None = None
    equation_refs: tuple[str, ...] = ()
    readonly: bool = True
    advisory_only: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.assessment_id or not self.constraint_ref:
            raise ValueError("constraint assessment requires identity and constraint ref")
        if self.status in (ConstraintStatusV0.SATISFIED, ConstraintStatusV0.VIOLATED) and not self.evidence_refs:
            raise ValueError("resolved constraint assessment requires explicit evidence_refs")
        if self.possibility == PossibilityStatusV0.IMPOSSIBLE and not self.evidence_refs:
            raise ValueError("IMPOSSIBLE requires explicit evidence_refs")
        if not self.readonly or not self.advisory_only:
            raise ValueError("constraint assessment must remain readonly/advisory")
        if self.decision_authority != "KX108_ONLY" or self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("constraint assessment cannot decide or act")


def assess_constraint_v0(
    *,
    assessment_id: str,
    constraint: ScientificConstraintV0,
    status: ConstraintStatusV0,
    evidence_refs: tuple[str, ...] = (),
    contradiction_refs: tuple[str, ...] = (),
    possibility: PossibilityStatusV0 = PossibilityStatusV0.UNKNOWN,
) -> ConstraintAssessmentV0:
    """Build an explicit bounded assessment.

    F18 does not solve equations or infer scientific truth. A specialized engine
    must provide the status and evidence; this function only preserves the
    claim/evidence boundary and authority invariants.
    """
    return ConstraintAssessmentV0(
        assessment_id=assessment_id,
        constraint_ref=constraint.constraint_id,
        status=status,
        possibility=possibility,
        evidence_refs=evidence_refs,
        contradiction_refs=contradiction_refs,
        model_ref=constraint.model_ref,
        equation_refs=constraint.equation_refs,
    )
