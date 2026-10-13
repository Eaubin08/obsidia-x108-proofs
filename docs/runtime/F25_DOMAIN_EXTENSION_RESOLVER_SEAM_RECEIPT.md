# F2.5 — DOMAIN EXTENSION RESOLVER SEAM — PROOF RECEIPT

Date: 2026-10-06

## Source change

`scripts/obsidia_governed_runtime_cycle_v1.py` now accepts an optional `domain_extension_resolver` on:

- `run_governed_runtime_cycle()`;
- `run_governed_feedback_cycle()`.

Default value is `None`.

## Resolution semantics

```text
canonical _DOMAIN_PIPELINES
    first / immutable precedence
optional extension resolver
    only for absent canonical domain
otherwise
    fail closed
```

The extension cannot shadow an existing canonical domain because it is never consulted for one.

## Dedicated cross-repository proof

Consumer/proof repository:
`Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-`

Workflow run: 37524651160
Job: 112478457034
Result: `101 passed in 0.46s`
Conclusion: SUCCESS

The proof passes the CSSA/V0.1 portable Administration resolver directly through the new source-level dependency; no module monkey-patching is used.

Validated full lifecycle:

```text
registered non-sovereign agent
-> context validation
-> first-class domain extension resolver
-> real GuardX108
-> CanonicalDecisionEnvelope
-> pre-execution context
-> decision record
-> OS3 ticket
-> replay
-> execution gate
-> bounded provider
-> receipt
-> readonly feedback
```

Observed:
- clean -> ALLOW + bounded execution;
- unknown threshold -> HOLD + no execution;
- contradiction threshold -> BLOCK + no execution;
- no resolver -> unsupported Administration refused before decision;
- feedback cycle propagates the resolver and requires a fresh decision.

## Native X108 Periphery CI — baseline-equivalent

Security-hardened F2.5 branch run:
- run: 37526855143
- job: 112485940506
- result: `11 failed, 12451 passed, 46 skipped, 207 deselected`.

Current-main baseline run used for comparison:
- run: 37508621493
- job: 112423614411
- result: `11 failed, 12443 passed, 46 skipped, 207 deselected`.

The 11 failures are the same baseline failures in both runs; no F2.5 test fails:
- Brody/memory/Graphiti API route-registration audit;
- Sigma/bus route audit;
- two Lean tests missing `lake` in CI;
- five batch-execution/environment-sensitive failures;
- branching-ledger identity expectation;
- git-worktree test missing CI git author identity.

F2.5 adds eight focused integration tests, including forged-envelope rejection; the pass count increases by exactly eight:

```text
12451 - 12443 = 8
```

No new failing test is introduced by the resolver seam.

Therefore the native suite is recorded as:
`BASELINE_EQUIVALENT_NO_NEW_FAILURES`

rather than falsely described as globally green.

## Branch delta

Against main, the F2.5 branch contains only:
- one runtime coordinator modification;
- one focused integration test file;
- architecture/proof documentation.

GuardX108, sigma contracts, canonical domain bridges and proof kernels are not modified.

## Claim boundary

`SOURCE_LEVEL_FIRST_CLASS_RESOLVER_SEAM_PROVEN_NO_NEW_REGRESSION`

No claim of merge to main is made by this receipt.
