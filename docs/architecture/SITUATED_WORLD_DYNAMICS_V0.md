# F12 — Situated World Dynamics V0

Status: VERIFIED / NO F12 REGRESSION

## Purpose

Materialize the missing common dynamics layer identified by the source audit without turning MMonde into a physics engine.

This layer represents:
- multiple clocks without inventing missing timestamps;
- spatial frame references;
- N→N+1 transitions;
- trajectories;
- continuity / drift / rupture status;
- typed temporal/causal relations.

It does not:
- infer physical truth;
- perform sensor fusion;
- implement domain laws;
- decide;
- execute;
- mutate memory.

## Contracts

- `TimeEnvelopeV0`
- `SpatialFrameRefV0`
- `RelationStatusV0`
- `TypedRelationV0`
- `ContinuityStatusV0`
- `TransitionV0`
- `TrajectoryV0`

## Causality rule

`TEMPORAL != CORRELATED != DERIVED != CAUSAL_ASSERTED != CAUSAL_PROVEN`.

`CAUSAL_PROVEN` requires explicit evidence references.

## Authority rule

Every transition/trajectory remains readonly representation with:
- `decision_authority = KX108_ONLY`
- `allowed_to_decide = False`
- `allowed_to_act = False`

## Relationship to MMonde

F12 enriches the representational vocabulary around MMonde but does not replace `WorldObservationV0` or `WorldStateV0`.

A later adapter may reference F12 objects from MMonde once the F12 contract is verified.

## Next phase

F13 — Measurement / Evidence Contract V0:
phenomenon → signal → instrument/sensor → measurement with unit, precision, calibration, environment, uncertainty and limits.

No F13 runtime should be created before F12 validation.

## Verification finale

- Code SHA vérifié: `af3dc66835da742f75275e6e40faf7db4b4529ef`
- GitHub Actions run: `37557296648`
- Résultat global: `12490 passed / 11 failed / 46 skipped / 207 deselected`
- Failures F12 visibles: `0`
- Les 11 failures restantes correspondent aux familles baseline historiques déjà présentes avant F12.

**Verdict:** F12 `VERIFIED`. Le statut ne transforme pas les relations temporelles en causalité, n'invente aucun timestamp absent et n'ajoute aucune autorité hors KX108.
