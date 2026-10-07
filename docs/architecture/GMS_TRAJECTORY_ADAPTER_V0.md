# F17 — GMS Trajectory Adapter V0

Status: IMPLEMENTED / VALIDATION REQUIRED

## Purpose

Connect the existing Brody 21D cognitive point cloud to F12 Situated World Dynamics without rebuilding GMS.

The existing cognitive point cloud already provides a 21-axis geometry used for layer selection and budgeting. F17 wraps successive point-cloud outputs as readonly semantic-position snapshots and maps explicit N→N+1 changes into world-dynamics transitions/trajectories.

## Reuse

F17 reuses:
- Brody `vector_21d` output as the semantic-position source;
- F12 `TimeEnvelopeV0`;
- F12 `TransitionV0`;
- F12 `TrajectoryV0`;
- F12 `ContinuityStatusV0`.

It does **not** modify Brody layer selection, budget, balances or authority logic.

## Contracts

- `GmsSemanticPointV0`
- `GmsAxisDeltaV0`
- `GmsSemanticTransitionV0`

## Adapter functions

- `semantic_point_from_brody_point_cloud_v0()`
- `build_gms_semantic_transition_v0()`
- `build_gms_trajectory_v0()`

## Geometry

For each transition, F17 preserves explicit per-axis deltas and a deterministic L1 drift magnitude.

This geometric drift is **not** automatically classified as semantic rupture.

A large distance does not become `RUPTURE` by threshold magic. Continuity status stays `UNKNOWN` unless an upstream validated rule explicitly declares `CONTINUOUS`, `DRIFT` or `RUPTURE`.

## Boundary

F17 is not:
- a new GMS engine;
- a language model;
- semantic truth;
- memory;
- causal proof;
- an authority layer.

It is a conservative bridge from existing cognitive geometry to the canonical time/trajectory grammar.

## Authority

All GMS points and resulting F12 transitions/trajectories remain:
- readonly;
- representation only;
- `decision_authority = KX108_ONLY`;
- `allowed_to_decide = False`;
- `allowed_to_act = False`.

## Next phase

F18 — Science / Constraint Engine V0.

No F18 runtime before F17 validation.
