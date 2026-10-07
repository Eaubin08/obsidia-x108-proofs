"""F19 Physical Thermodynamics Adapter V0.

Strictly separates physical thermodynamic measurements/models from Obsidia's
existing computational/cognitive thermodynamics signals.

This layer does not compute thermodynamic truth by itself. It binds situated
physical measurements to F18 scientific models/constraints and preserves
evidence, applicability and authority boundaries.
"""
from __future__ import annotations

from dataclasses import dataclass

from periphery.measurement.contracts_v0 import SituatedMeasurementV0
from periphery.science_constraints.contracts_v0 import (
    ConstraintAssessmentV0,
    ScientificConstraintV0,
    ScientificEquationRefV0,
    ScientificInvariantV0,
    ScientificModelRefV0,
)

_FORBIDDEN_COMPUTATIONAL_SIGNAL_KINDS = {
    "entropy_score",
    "dissipation_score",
    "instability_score",
    "coherence_temperature",
    "pressure_load",
    "mismatch_heat",
    "boundary_heat",
    "memory_friction",
    "projection_cost",
    "thermo_debt",
    "total_debt",
    "compute_cost",
    "attention_cost",
    "recovery_cost",
}

_ALLOWED_PHYSICAL_QUANTITIES = {
    "temperature",
    "pressure",
    "volume",
    "mass",
    "internal_energy",
    "enthalpy",
    "entropy",
    "heat",
    "work",
    "density",
    "specific_heat",
    "heat_flux",
}


@dataclass(frozen=True)
class ThermodynamicSystemRefV0:
    system_ref: str
    boundary_ref: str
    system_kind: str
    environment_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.system_ref or not self.boundary_ref or not self.system_kind:
            raise ValueError("thermodynamic system requires system, boundary and kind refs")


@dataclass(frozen=True)
class PhysicalThermodynamicQuantityV0:
    quantity_kind: str
    measurement: SituatedMeasurementV0

    def __post_init__(self) -> None:
        if self.quantity_kind not in _ALLOWED_PHYSICAL_QUANTITIES:
            raise ValueError(f"unsupported physical thermodynamic quantity: {self.quantity_kind}")
        signal_kind = str(self.measurement.context.signal_kind)
        if signal_kind in _FORBIDDEN_COMPUTATIONAL_SIGNAL_KINDS:
            raise ValueError("computational thermodynamics signal cannot be used as physical measurement")
        if self.measurement.context.unit is None:
            raise ValueError("physical thermodynamic quantity requires an explicit unit")


@dataclass(frozen=True)
class ThermodynamicLawBindingV0:
    binding_id: str
    model: ScientificModelRefV0
    equation_refs: tuple[ScientificEquationRefV0, ...] = ()
    invariant_refs: tuple[ScientificInvariantV0, ...] = ()
    applicability_condition_refs: tuple[str, ...] = ()
    validity_scope_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.binding_id:
            raise ValueError("thermodynamic law binding requires identity")
        for equation in self.equation_refs:
            if equation.model_ref != self.model.model_ref:
                raise ValueError("thermodynamic equation/model binding mismatch")
        for invariant in self.invariant_refs:
            if invariant.model_ref is not None and invariant.model_ref != self.model.model_ref:
                raise ValueError("thermodynamic invariant/model binding mismatch")


@dataclass(frozen=True)
class PhysicalThermodynamicStateCandidateV0:
    state_id: str
    system: ThermodynamicSystemRefV0
    quantities: tuple[PhysicalThermodynamicQuantityV0, ...]
    law_bindings: tuple[ThermodynamicLawBindingV0, ...] = ()
    constraint_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    candidate_only: bool = True
    physical_truth_proven: bool = False
    readonly: bool = True
    advisory_only: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.state_id:
            raise ValueError("physical thermodynamic state requires identity")
        if not self.quantities:
            raise ValueError("physical thermodynamic state requires at least one physical quantity")
        if not self.candidate_only:
            raise ValueError("physical thermodynamic state must remain candidate")
        if self.physical_truth_proven:
            raise ValueError("F19 cannot self-promote physical thermodynamic truth")
        if not self.readonly or not self.advisory_only:
            raise ValueError("physical thermodynamic state must remain readonly/advisory")
        if self.decision_authority != "KX108_ONLY" or self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("physical thermodynamic state cannot decide or act")


@dataclass(frozen=True)
class PhysicalThermodynamicAssessmentBundleV0:
    bundle_id: str
    state_ref: str
    constraint_assessments: tuple[ConstraintAssessmentV0, ...]
    evidence_refs: tuple[str, ...] = ()
    readonly: bool = True
    advisory_only: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.bundle_id or not self.state_ref:
            raise ValueError("thermodynamic assessment bundle requires identity and state ref")
        if not self.readonly or not self.advisory_only:
            raise ValueError("thermodynamic assessment bundle must remain readonly/advisory")
        if self.decision_authority != "KX108_ONLY" or self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("thermodynamic assessment bundle cannot decide or act")


def build_physical_thermodynamic_constraint_v0(
    *,
    constraint_id: str,
    statement: str,
    law_binding: ThermodynamicLawBindingV0,
    scope_refs: tuple[str, ...] = (),
    reversible: bool | None = None,
) -> ScientificConstraintV0:
    return ScientificConstraintV0(
        constraint_id=constraint_id,
        statement=statement,
        model_ref=law_binding.model.model_ref,
        equation_refs=tuple(eq.equation_ref for eq in law_binding.equation_refs),
        invariant_refs=tuple(inv.invariant_id for inv in law_binding.invariant_refs),
        scope_refs=scope_refs,
        reversible=reversible,
    )
