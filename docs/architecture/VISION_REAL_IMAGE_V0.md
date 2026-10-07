# F16 — Vision / Real Image V0

Status: IMPLEMENTED / VALIDATION REQUIRED

## Purpose

Materialize the real-image branch defined in the source corpus without turning image perception into truth.

F16 preserves:
- immutable asset ref/hash;
- capture context (device, optics, application/author/consent refs, capture parameters);
- time/frame/latency;
- visual primitives;
- depth/motion/mask/geometry/text/features refs;
- physical-signal refs;
- prior-state refs;
- context-graph refs;
- candidate interpretations;
- image integrity report;
- uncertainty and contradictions.

## Contracts

- `ImageAssetRefV0`
- `CaptureContextV0`
- `VisualPrimitiveV0`
- `CandidateInterpretationV0`
- `ImageIntegrityReportV0`
- `RealImageObservationV0`

## Separation rules

`real image != generated image`

`candidate interpretation != observation`

`image integrity != physical truth`

`image agreement != causal proof`

Generated hypotheses cannot simultaneously be asserted as observed facts.

## Bridges

`real_image_to_modality_observation_v0()`
maps the image into the existing F6 multimodal transport.

`real_image_to_world_observation_v0()`
then maps conservatively into MMonde.

The bridge fixes:
- modality = `image`
- generated = `False`
- causal_status = `UNKNOWN`

Missing frame or latency remains explicit uncertainty.

## Integrity

`ImageIntegrityReportV0` carries:
- quality flags
- calibration refs
- uncertainty
- contradictions
- freshness flags
- synchronized physical signal refs
- physical compatibility refs

`integrity_proven=True` requires explicit physical compatibility evidence refs.

## Authority

All image objects remain:
- readonly
- representation only
- `decision_authority = KX108_ONLY`
- `allowed_to_decide = False`
- `allowed_to_act = False`

## Boundary

F16 is **not**:
- object-recognition intelligence;
- production computer vision;
- a physical simulator;
- image generation;
- a causal inference engine;
- an execution authority.

It is the canonical real-image evidence contract needed before any such specialized engine can be attached safely.

## Next phase

F17 — GMS Trajectory Adapter V0.

No F17 runtime before F16 validation.
