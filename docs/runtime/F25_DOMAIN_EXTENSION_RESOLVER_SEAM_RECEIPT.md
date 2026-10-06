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

## Cross-repository proof

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

## Native branch CI

`X108 Periphery CI` run 37524473637 is the native all-tests/protected-files workflow for this branch.
Its final status must be recorded separately once complete.

## Claim boundary

`SOURCE_LEVEL_FIRST_CLASS_RESOLVER_SEAM_CROSS_REPO_PROVEN`

No claim of merge to main is made by this receipt.
