# F19 — Physical Thermodynamics Adapter V0

Status: VERIFIED / NO F19 REGRESSION

## Purpose

Create a physical-thermodynamics adapter that is strictly separate from Obsidia's existing computational/cognitive thermodynamics.

Existing computational signals such as:
- `entropy_score`
- `dissipation_score`
- `coherence_temperature`
- `thermo_debt`
- `compute_cost`
- `attention_cost`

must never be reused as physical entropy, temperature, internal energy, heat or work.

## Reuse

F19 reuses:
- F13 `SituatedMeasurementV0`
- F18 `ScientificModelRefV0`
- F18 `ScientificEquationRefV0`
- F18 `ScientificInvariantV0`
- F18 `ScientificConstraintV0`
- F18 `ConstraintAssessmentV0`

## Contracts

- `ThermodynamicSystemRefV0`
- `PhysicalThermodynamicQuantityV0`
- `ThermodynamicLawBindingV0`
- `PhysicalThermodynamicStateCandidateV0`
- `PhysicalThermodynamicAssessmentBundleV0`

## Physical quantities

The initial canonical quantity vocabulary is bounded to:
- temperature
- pressure
- volume
- mass
- internal_energy
- enthalpy
- entropy
- heat
- work
- density
- specific_heat
- heat_flux

Every physical quantity must come from a situated measurement with an explicit unit.

## Law/model binding

F19 does not hard-code a universal thermodynamic solver.

A physical thermo state binds:
- a declared thermodynamic system/boundary;
- situated physical quantities;
- explicit F18 model refs;
- equation refs;
- invariant refs;
- applicability/validity scope;
- evidence/uncertainty/contradictions.

Equation and invariant refs must belong to the same declared model.

## Separation rules

`computational entropy_score != physical entropy`

`coherence_temperature != physical temperature`

`thermo_debt != thermodynamic state variable`

`physical measurement != thermodynamic truth`

`law reference != law applicability proof`

`constraint assessment != KX108 decision`

## Authority

Physical thermodynamic states and assessment bundles remain:
- readonly;
- advisory only;
- candidate-only;
- `decision_authority = KX108_ONLY`;
- `allowed_to_decide = False`;
- `allowed_to_act = False`.

F19 cannot self-promote `physical_truth_proven=True`.

## Boundary

F19 is an adapter and contract layer. It is not:
- a universal physics solver;
- a CFD engine;
- a thermodynamic simulator;
- a material database;
- a truth oracle.

Specialized engines may later evaluate declared thermodynamic models and return bounded F18 assessments with evidence.

## Next phase

F20 — Cross-Modal Coherence V0.

No F20 runtime before F19 validation.

## Verification finale

- Code SHA vérifié: `27e54439fb0b46e9490bb5ddc4efdafebdd031b3`
- GitHub Actions run: `37566516144`
- Résultat global: `12531 passed / 11 failed / 46 skipped / 207 deselected`
- Failures F19 visibles: `0`
- Les 11 failures restantes correspondent aux familles baseline historiques.

**Verdict:** F19 `VERIFIED`.
