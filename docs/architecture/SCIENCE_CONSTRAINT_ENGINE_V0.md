# F18 — Science / Constraint Engine V0

Status: IMPLEMENTED / VALIDATION REQUIRED

## Purpose

Materialize the minimal scientific constraint grammar defined by the master plan without creating a monolithic physics brain.

F18 represents:
- scientific model references;
- equation references;
- invariants;
- constraints;
- candidate predictions;
- bounded constraint assessments;
- POSSIBLE / IMPOSSIBLE / UNKNOWN status.

It does not solve arbitrary physics, infer truth, or authorize action.

## Contracts

- `ScientificModelRefV0`
- `ScientificEquationRefV0`
- `ScientificInvariantV0`
- `ScientificConstraintV0`
- `ScientificPredictionCandidateV0`
- `ConstraintAssessmentV0`
- `ConstraintStatusV0`
- `PossibilityStatusV0`

## Proof boundaries

A non-assumed invariant requires explicit `proof_refs`.

An assumed invariant must remain explicitly marked `assumed=True`.

A prediction is always a candidate until tested and must name its expected observables.

A resolved constraint assessment (`SATISFIED` or `VIOLATED`) requires evidence.

`IMPOSSIBLE` requires evidence and remains scoped to the declared model/constraint.

## Separation rules

`model reference != model execution`

`equation reference != solved equation`

`constraint assessment != decision`

`scientific evidence != KX108 authority`

`IMPOSSIBLE in model != metaphysical impossibility`

## Authority

Every assessment remains:
- readonly;
- advisory only;
- `decision_authority = KX108_ONLY`;
- `allowed_to_decide = False`;
- `allowed_to_act = False`.

## Boundary

F18 is intentionally generic. Specialized engines for mechanics, thermodynamics, optics, RF, biology or other scientific domains may attach later, each carrying its own laws, models, equations, evidence and validity domain.

The MMonde core remains world/domain agnostic.

## Next phase

F19 — Physical Thermodynamics Adapter.

No F19 runtime before F18 validation.
