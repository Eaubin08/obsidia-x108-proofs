# F14 — Physical Signal Periphery V0

Status: IMPLEMENTED / VALIDATION REQUIRED

## Purpose

Materialize the physical-signal objects recovered from the historical source corpus, on top of F13 situated measurements.

This layer represents:
- physical signal events;
- signal-window reports;
- contradictions between signal events;
- advisory physical-risk hints;
- candidate world states built from physical measurements.

It remains strictly non-sovereign.

## Contracts

- `PhysicalSignalEventV0`
- `SignalContradictionV0`
- `PhysicalRiskHintV0`
- `PhysicalSignalReportV0`
- `WorldStateCandidateV0`

## Truth boundary

`measurement != physical truth`

`report != physical truth`

`world state candidate != canonical reality`

Provenance and source hashes are preserved, but provenance is never promoted to physical authenticity.

## MMonde bridge

`physical_event_to_world_observation()` maps a physical signal event into `WorldObservationV0` while preserving:
- source refs/hashes;
- instrument/configuration/calibration refs;
- signal/unit/precision;
- spatial frame;
- environment;
- measurement limits;
- uncertainty;
- evidence.

`build_world_state_candidate_v0()` creates a candidate `WorldStateV0` from a report + event set.

It does not perform physical truth adjudication or cross-modal coherence.

## Authority boundary

All events/hints/candidates remain:
- readonly representation;
- `decision_authority = KX108_ONLY`;
- `allowed_to_decide = False`;
- `allowed_to_act = False`.

## Next phase

F15 — Physical Evidence Plane V0:
- temporal compatibility;
- spatial/frame compatibility;
- metric compatibility;
- causal compatibility;
- evidence independence;
- replayable physical evidence candidate;
- provenance != authenticity.

No F15 runtime before F14 validation.
