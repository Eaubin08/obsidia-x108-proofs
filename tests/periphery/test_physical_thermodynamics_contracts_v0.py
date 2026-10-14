from periphery.measurement.contracts_v0 import InstrumentRefV0, MeasurementContextV0, SituatedMeasurementV0
from periphery.physical_thermodynamics.contracts_v0 import (
    PhysicalThermodynamicQuantityV0,
    PhysicalThermodynamicStateCandidateV0,
    ThermodynamicLawBindingV0,
    ThermodynamicSystemRefV0,
    build_physical_thermodynamic_constraint_v0,
)
from periphery.science_constraints.contracts_v0 import (
    ScientificEquationRefV0,
    ScientificInvariantV0,
    ScientificModelRefV0,
)
from periphery.world_dynamics.contracts_v0 import TimeEnvelopeV0


def _measurement(signal_kind: str, unit: str | None = "K", value: object = 293.15):
    return SituatedMeasurementV0(
        measurement_id=f"m:{signal_kind}",
        value=value,
        context=MeasurementContextV0(
            phenomenon_ref="thermo-system:1",
            signal_kind=signal_kind,
            unit=unit,
            precision=0.1,
            time=TimeEnvelopeV0(observed_at="2026-10-07T00:00:00Z"),
            instrument=InstrumentRefV0(
                instrument_ref="sensor:thermo:1",
                instrument_kind="thermometer",
                calibration_ref="cal:thermo:1",
            ),
        ),
        source_refs=("source:thermo:1",),
        evidence_refs=("evidence:thermo:1",),
    )


def test_computational_entropy_score_cannot_be_physical_entropy():
    try:
        PhysicalThermodynamicQuantityV0(
            quantity_kind="entropy",
            measurement=_measurement("entropy_score", unit="J/K", value=0.42),
        )
    except ValueError as exc:
        assert "computational thermodynamics signal" in str(exc)
    else:
        raise AssertionError("computational entropy_score must not become physical entropy")


def test_physical_quantity_requires_explicit_unit():
    try:
        PhysicalThermodynamicQuantityV0(
            quantity_kind="temperature",
            measurement=_measurement("temperature", unit=None),
        )
    except ValueError as exc:
        assert "requires an explicit unit" in str(exc)
    else:
        raise AssertionError("unitless physical thermo quantity must fail closed")


def test_physical_state_cannot_self_promote_truth():
    quantity = PhysicalThermodynamicQuantityV0(
        quantity_kind="temperature",
        measurement=_measurement("temperature"),
    )
    system = ThermodynamicSystemRefV0(
        system_ref="system:1",
        boundary_ref="boundary:1",
        system_kind="closed_candidate",
    )
    try:
        PhysicalThermodynamicStateCandidateV0(
            state_id="thermo-state:1",
            system=system,
            quantities=(quantity,),
            physical_truth_proven=True,
        )
    except ValueError as exc:
        assert "cannot self-promote" in str(exc)
    else:
        raise AssertionError("F19 cannot self-promote physical truth")


def test_law_binding_requires_same_model():
    model = ScientificModelRefV0(model_ref="model:thermo:1", domain="thermodynamics")
    equation = ScientificEquationRefV0(
        equation_ref="eq:other",
        model_ref="model:other",
    )
    try:
        ThermodynamicLawBindingV0(
            binding_id="binding:bad",
            model=model,
            equation_refs=(equation,),
        )
    except ValueError as exc:
        assert "equation/model binding mismatch" in str(exc)
    else:
        raise AssertionError("mismatched equation/model must fail closed")


def test_physical_thermo_constraint_reuses_f18_science_grammar():
    model = ScientificModelRefV0(
        model_ref="model:thermo:1",
        domain="thermodynamics",
        source_refs=("source:thermo-law",),
    )
    equation = ScientificEquationRefV0(
        equation_ref="eq:thermo:1",
        model_ref=model.model_ref,
        symbol_refs=("U", "Q", "W"),
        unit_constraints=("J",),
    )
    invariant = ScientificInvariantV0(
        invariant_id="inv:thermo:1",
        statement="bounded invariant under declared system assumptions",
        model_ref=model.model_ref,
        proof_refs=("proof:thermo:1",),
    )
    binding = ThermodynamicLawBindingV0(
        binding_id="binding:1",
        model=model,
        equation_refs=(equation,),
        invariant_refs=(invariant,),
        applicability_condition_refs=("condition:closed-system",),
    )
    constraint = build_physical_thermodynamic_constraint_v0(
        constraint_id="constraint:thermo:1",
        statement="candidate state must satisfy declared thermodynamic model",
        law_binding=binding,
        scope_refs=("system:1",),
    )
    assert constraint.model_ref == "model:thermo:1"
    assert constraint.equation_refs == ("eq:thermo:1",)
    assert constraint.invariant_refs == ("inv:thermo:1",)


def test_physical_thermo_state_remains_non_sovereign():
    quantity = PhysicalThermodynamicQuantityV0(
        quantity_kind="temperature",
        measurement=_measurement("temperature"),
    )
    state = PhysicalThermodynamicStateCandidateV0(
        state_id="thermo-state:2",
        system=ThermodynamicSystemRefV0(
            system_ref="system:1",
            boundary_ref="boundary:1",
            system_kind="closed_candidate",
        ),
        quantities=(quantity,),
        evidence_refs=("evidence:thermo:1",),
    )
    assert state.candidate_only is True
    assert state.physical_truth_proven is False
    assert state.decision_authority == "KX108_ONLY"
    assert state.allowed_to_decide is False
    assert state.allowed_to_act is False
