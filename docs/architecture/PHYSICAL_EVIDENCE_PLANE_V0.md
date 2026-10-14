# F15 — Physical Evidence Plane V0

Status: VERIFIED / NO F15 REGRESSION

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

## CI observation

Run `37560271802`: `12506 passed / 12 failed / 46 skipped / 207 deselected`.

- F15 failures: `0`
- 11 failures: historical baseline families
- 1 additional failure: `TestApprovalConcurrency.test_concurrent_identical_content_idempotent`
- the same concurrency failure is present on the contract-only and test commits, with no F15 code path in that test.

A fresh CI run is requested by this documentation-only commit before freezing F15, to distinguish an unrelated nondeterministic baseline failure from an actual regression.

## Verification finale

- Code SHA vérifié: `f48fd37a20a827dcf471a5ed1d4b41d65585485c`
- GitHub Actions run: `37561024457`
- Résultat global: `12507 passed / 11 failed / 46 skipped / 207 deselected`
- Failures F15 visibles: `0`
- Le failure concurrent `TestApprovalConcurrency` n'est pas réapparu au re-run.
- Les 11 failures restantes correspondent aux familles baseline historiques.

**Verdict:** F15 `VERIFIED`.
