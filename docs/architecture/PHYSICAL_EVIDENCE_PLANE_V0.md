# F15 — Physical Evidence Plane V0

Status: IMPLEMENTED / VALIDATION REQUIRED

## Purpose

Create the generic compatibility/evidence layer below domain-specific reality gates.

F15 does **not** replace the GPS `RealityAuthenticityGate`.
It provides a reusable evidence-plane contract for GPS, Vision and future physical-signal domains.

## Contracts

- `CompatibilityStatusV0`
- `EvidenceCompatibilityV0`
- `ReplayablePhysicalEvidenceCandidateV0`

## Compatibility axes

- temporal
- spatial/frame
- metric
- causal
- evidence/source independence

The initial implementation is deliberately conservative:
- same explicit clock/frame/unit can be marked compatible;
- mismatched or unproven transforms remain UNKNOWN;
- causality is always UNKNOWN unless a later dedicated proof layer establishes it;
- repeated use of the same source does not count as independent evidence.

## Truth boundary

`compatible != true`

`coherent != authentic`

`replayable evidence candidate != canonical reality`

F15 never sets `physical_authenticity_proven=True`.

## Replay binding

A physical evidence candidate binds:
- report ref
- world-state candidate ref
- event refs
- evidence refs
- provenance refs
- compatibility assessment
- replay refs

Binding mismatches fail closed.

## Authority

All F15 objects are:
- readonly
- advisory only
- `decision_authority = KX108_ONLY`
- `allowed_to_decide = False`
- `allowed_to_act = False`

## Next phase

F16 — Vision / Real Image V0.

No F16 runtime before F15 validation.
