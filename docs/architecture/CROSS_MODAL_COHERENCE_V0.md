# F20 — Cross-Modal Coherence V0

Status: VERIFIED / NO F20 REGRESSION

## Purpose

Create the canonical cross-modal compatibility layer on top of F6 modality observations and F15 compatibility statuses.

F20 does not replace F15 physical evidence compatibility. It applies the same conservative compatibility language across heterogeneous modality observations such as image, GNSS, IMU, radar, audio or other future channels.

## Contracts

- `CrossModalPairAssessmentV0`
- `CrossModalCoherenceReportV0`

## Compatibility axes

Each modality pair is assessed on:
- temporal alignment;
- spatial/frame compatibility;
- metric compatibility;
- causal compatibility;
- source independence.

## Conservative rules

Temporal compatibility is only marked `COMPATIBLE` when explicit observation times match exactly.

Spatial compatibility is only marked `COMPATIBLE` when explicit frame refs match. Different frames remain `UNKNOWN` until an explicit transform is proven.

Metric compatibility is only marked `COMPATIBLE` when both channels explicitly expose the same unit. Heterogeneous or transformed units remain `UNKNOWN`.

Causality is always `UNKNOWN` in F20. Agreement never proves causality.

Distinct sources may support source-independence compatibility; the same source remains `UNKNOWN`.

Generated modalities are explicitly flagged `GENERATED_MODALITY_NOT_PHYSICAL_TRUTH`.

## Separation rules

`cross-modal agreement != truth`

`temporal alignment != causality`

`same frame != same phenomenon`

`same unit != semantic equivalence`

`generated modality != physical evidence`

`coherence report != decision`

## Evidence and provenance

The report preserves:
- modality observation refs;
- all pair assessments;
- uncertainty;
- contradictions;
- evidence refs;
- provenance refs;
- whether generated content is present.

F20 cannot set `physical_coherence_proven=True`.

## Authority

Every report remains:
- readonly;
- advisory only;
- `decision_authority = KX108_ONLY`;
- `allowed_to_decide = False`;
- `allowed_to_act = False`.

## Boundary

F20 is not:
- a sensor-fusion truth engine;
- a causal inference engine;
- a calibration engine;
- a frame-transform engine;
- an execution gate.

Specialized domain adapters may consume F20 reports, but only domain governance + KX108 can authorize downstream action.

## Next phase

F21 — GPS Physical-World Closure.

No F21 runtime before F20 validation.

## Verification finale

- Code SHA vérifié: `db36a7592a43683056dc31acb5aba41bc1a69d8c`
- GitHub Actions run: `37567727213`
- Résultat global: `12538 passed / 11 failed / 46 skipped / 207 deselected`
- Failures F20 visibles: `0`
- Les 11 failures restantes correspondent aux familles baseline historiques.

**Verdict:** F20 `VERIFIED`.
