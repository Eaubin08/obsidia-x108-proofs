# F2.5 — MERGE-READINESS AUDIT / FREEZE CANDIDATE

Date: 2026-10-06
Branch: `feat/f2-5-portable-domain-resolver-seam-v0`
Target considered: `main`
Action on main: **NONE**

## Executive verdict

`MERGE_READY_CANDIDATE_AFTER_SECURITY_HARDENING`

The branch is prepared and frozen as a candidate only. No merge, fast-forward, cherry-pick or push to `main` is authorized by this audit.

## Branch delta

Compared with current `main` (`48f0c2fbcfe097c213b2783bc7b4d0fba78e6621`), the branch changes only:

- `scripts/obsidia_governed_runtime_cycle_v1.py`;
- focused F2.5 integration tests;
- F2.5 architecture/runtime documentation.

Not modified:

- `sigma/guard.py`;
- `sigma/contracts.py`;
- kernel/protocol proofs;
- canonical domain bridges;
- Binder authority;
- memory runtime;
- existing `_DOMAIN_PIPELINES` contents.

## Security finding discovered during merge audit

### F25-AUDIT-001 — extension-supplied sovereign envelope

Initial F2.5 draft allowed an extension resolver to return a full `(state, packet) -> CanonicalDecisionEnvelope` pipeline.

That was rejected during audit.

Reason: `persist_kx108_agent_pre_execution_decision()` rejects plain dicts but accepts dataclass objects. A hostile in-process extension could therefore construct a dataclass-shaped `CanonicalDecisionEnvelope(x108_gate="ALLOW")` and attempt to bypass the intended `GuardX108` provenance.

Severity before fix: **HIGH / sovereignty boundary**.

### Fix

The first-class extension API is now aggregate-only:

```text
extension resolver
  -> resolve_domain_aggregate_builder(domain)
  -> builder(state, packet)
  -> DomainAggregate only

runtime coordinator
  -> validates DomainAggregate type
  -> validates aggregate.domain.value == requested domain
  -> invokes REAL GuardX108().decide(aggregate)
  -> CanonicalDecisionEnvelope
```

A forged `CanonicalDecisionEnvelope(ALLOW)` returned by an extension is now rejected before persistence/execution.

Dedicated upstream and cross-repository negative tests cover this exact attack.

Verdict: `CLOSED_BEFORE_FREEZE`.

## Authority audit

Preserved:

- `KX108_ONLY` remains the decision authority;
- extension cannot supply sovereign gate through supported API;
- canonical domains have strict precedence;
- extension is consulted only for a domain absent from `_DOMAIN_PIPELINES`;
- no resolver => original unsupported-domain refusal;
- HOLD/BLOCK remain non-executing;
- feedback re-entry obtains a new decision;
- no memory-write or kernel-mutation authority is introduced.

## Compatibility audit

The new argument is keyword-only and defaults to `None`:

```text
domain_extension_resolver=None
```

Therefore existing callers remain source-compatible.

Default route remains:

```text
existing canonical domain -> existing canonical bridge
unknown domain + no resolver -> REFUSED_UNSUPPORTED_DOMAIN
```

## Trust boundary

F2.5 does **not** sandbox arbitrary Python extension code.

Frozen rule:

> A domain extension resolver is explicit trusted host configuration. No automatic plugin discovery, remote-code loading or third-party untrusted Python execution may be added under this F2.5 contract.

If untrusted plugins are desired later, they require a separate process/sandbox boundary and a new proof.

## Cross-repository proof

CSSA/V0.1 consumer branch:
`feat/f2-5-first-class-runtime-seam-v0`

Final security-hardened focused proof:

```text
102 passed in 0.43s
GitHub Actions run 37527394792
job 112487760134
```

Coverage includes:
- F1 through F2.4 regression;
- first-class direct resolver path;
- ALLOW/HOLD/BLOCK;
- no-resolver refusal;
- feedback-cycle propagation;
- forged-envelope rejection.

## Native upstream CI baseline

Current `main` is not globally green in `X108 Periphery CI` for environment/pre-existing reasons.

Known main baseline:

```text
11 failed, 12443 passed, 46 skipped, 207 deselected
run 37508621493
```

Earlier F2.5 pre-hardening comparison had the same 11 failures and only added passes.

Security-hardened aggregate-only native run:

```text
11 failed, 12451 passed, 46 skipped, 207 deselected
run 37526855143 / job 112485940506
```

The failure names are identical to the 11 current-main baseline failures. No F2.5 test fails. The pass count rises from 12443 to 12451 because F2.5 adds eight focused passing tests.

Verdict: `BASELINE_EQUIVALENT_NO_NEW_FAILURES`.

## Merge policy

Before any future merge to main, require all of:

1. latest cross-repo focused proof green;
2. native upstream failure set identical to main baseline, or smaller;
3. no protected kernel/proof file modified;
4. branch still based directly on current main or explicitly rebased/audited;
5. aggregate-only extension contract unchanged;
6. no auto-discovery/untrusted plugin loading;
7. explicit human decision to merge.

## Freeze instruction

After final CI evidence is recorded, treat this branch as:

`F25_FREEZE_V0`

Any semantic change after freeze requires a new branch/version or an explicit unfreeze record.


## Final freeze verdict

`F25_FREEZE_V0 = ACTIVE ON BRANCH`

Merge-readiness technical verdict:
`READY_TO_CONSIDER_FOR_MAIN`.

Operational verdict:
`DO_NOT_MERGE_WITHOUT_EXPLICIT_USER_DECISION`.

No main mutation has been performed.
