from periphery.science_constraints.contracts_v0 import (
    ConstraintAssessmentV0,
    ConstraintStatusV0,
    PossibilityStatusV0,
    ScientificConstraintV0,
    ScientificEquationRefV0,
    ScientificInvariantV0,
    ScientificModelRefV0,
    ScientificPredictionCandidateV0,
    assess_constraint_v0,
)


def test_non_assumed_invariant_requires_proof():
    try:
        ScientificInvariantV0(
            invariant_id="inv:1",
            statement="energy conserved in declared closed-system model",
        )
    except ValueError as exc:
        assert "requires proof_refs" in str(exc)
    else:
        raise AssertionError("unproved non-assumed invariant must fail closed")


def test_assumed_invariant_remains_explicitly_assumed():
    inv = ScientificInvariantV0(
        invariant_id="inv:assumed",
        statement="candidate simplifying assumption",
        assumed=True,
    )
    assert inv.assumed is True
    assert inv.proof_refs == ()


def test_prediction_is_candidate_and_requires_observables():
    try:
        ScientificPredictionCandidateV0(
            prediction_id="pred:bad",
            statement="x increases",
            model_ref="model:1",
            expected_observable_refs=(),
        )
    except ValueError as exc:
        assert "requires expected observable refs" in str(exc)
    else:
        raise AssertionError("prediction without observables must fail closed")

    pred = ScientificPredictionCandidateV0(
        prediction_id="pred:1",
        statement="candidate observable changes",
        model_ref="model:1",
        expected_observable_refs=("measurement:x",),
    )
    assert pred.candidate_only is True


def test_resolved_constraint_requires_evidence():
    constraint = ScientificConstraintV0(
        constraint_id="constraint:1",
        statement="value remains within declared model envelope",
        model_ref="model:1",
    )
    try:
        assess_constraint_v0(
            assessment_id="assessment:1",
            constraint=constraint,
            status=ConstraintStatusV0.VIOLATED,
        )
    except ValueError as exc:
        assert "requires explicit evidence_refs" in str(exc)
    else:
        raise AssertionError("resolved assessment without evidence must fail closed")


def test_unknown_constraint_can_remain_unknown_without_fake_evidence():
    constraint = ScientificConstraintV0(
        constraint_id="constraint:2",
        statement="compatibility not yet established",
    )
    assessment = assess_constraint_v0(
        assessment_id="assessment:2",
        constraint=constraint,
        status=ConstraintStatusV0.UNKNOWN,
    )
    assert assessment.status == ConstraintStatusV0.UNKNOWN
    assert assessment.possibility == PossibilityStatusV0.UNKNOWN
    assert assessment.evidence_refs == ()


def test_impossible_requires_evidence_and_remains_non_sovereign():
    constraint = ScientificConstraintV0(
        constraint_id="constraint:3",
        statement="candidate state outside declared model envelope",
        model_ref="model:3",
        equation_refs=("eq:3",),
    )
    assessment = assess_constraint_v0(
        assessment_id="assessment:3",
        constraint=constraint,
        status=ConstraintStatusV0.VIOLATED,
        possibility=PossibilityStatusV0.IMPOSSIBLE,
        evidence_refs=("evidence:3",),
    )
    assert isinstance(assessment, ConstraintAssessmentV0)
    assert assessment.possibility == PossibilityStatusV0.IMPOSSIBLE
    assert assessment.decision_authority == "KX108_ONLY"
    assert assessment.allowed_to_decide is False
    assert assessment.allowed_to_act is False


def test_model_and_equation_are_references_not_executors():
    model = ScientificModelRefV0(
        model_ref="model:newton-v0",
        domain="mechanics",
        source_refs=("source:mechanics",),
    )
    eq = ScientificEquationRefV0(
        equation_ref="eq:fma",
        model_ref=model.model_ref,
        symbol_refs=("F", "m", "a"),
        unit_constraints=("N", "kg", "m/s2"),
    )
    assert model.domain == "mechanics"
    assert eq.model_ref == "model:newton-v0"
