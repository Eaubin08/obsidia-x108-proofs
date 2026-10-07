# F13 — Measurement / Evidence Contract V0

Status: VERIFIED / NO F13 REGRESSION

## Purpose

Materialize the generic measurement contract identified in the physical/scientific source corpus.

This layer sits between situated world dynamics and specialized physical/vision/signal adapters.

It preserves:
- phenomenon reference;
- signal kind;
- instrument identity/configuration/calibration reference;
- unit;
- precision;
- multi-clock time envelope;
- spatial frame;
- environment reference;
- measurement limits;
- uncertainty;
- contradictions;
- provenance and source hashes.

## Contracts

- `InstrumentRefV0`
- `MeasurementContextV0`
- `SituatedMeasurementV0`

## Truth boundary

A measurement is not the world.

`source/provenance != physical authenticity`

Missing calibration must remain explicit. Physical authenticity cannot be asserted without explicit evidence refs.

## Authority boundary

All measurement objects remain readonly representation only:
- `decision_authority = KX108_ONLY`
- `allowed_to_decide = False`
- `allowed_to_act = False`

## Relationship to F12

F13 reuses:
- `TimeEnvelopeV0`
- `SpatialFrameRefV0`

It does not infer trajectories, causality or domain meaning.

## Next phase

F14 — Physical Signal Periphery V0:
- PhysicalSignalEvent
- PhysicalSignalReport
- WorldStateCandidate
- SignalContradiction
- PhysicalRiskHint

No F14 runtime before F13 validation.

## Verification finale

- Code SHA vérifié: `ed0d8fddbc388dd062c4f73ca08672ec07043449`
- GitHub Actions run: `37558499132`
- Résultat global: `12495 passed / 11 failed / 46 skipped / 207 deselected`
- Failures F13 visibles: `0`
- Les 11 failures restantes correspondent aux familles baseline historiques déjà présentes avant F13.

**Verdict:** F13 `VERIFIED`.
