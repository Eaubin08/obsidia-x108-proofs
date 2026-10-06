# F25_FREEZE_V0

Freeze date: 2026-10-06
Status: **FROZEN CANDIDATE — DO NOT MERGE TO MAIN WITHOUT EXPLICIT DECISION**

## Frozen semantic code

`scripts/obsidia_governed_runtime_cycle_v1.py` semantic code state:
`fc47df1f79a600fa29dff53228c057e5fdbe7679`

Later commits on this branch may add audit/freeze documentation only unless an explicit unfreeze record is created.

## Frozen contract

```text
run_governed_runtime_cycle(..., domain_extension_resolver=None)
run_governed_feedback_cycle(..., domain_extension_resolver=None)

resolver.is_supported_domain(domain)
resolver.resolve_domain_aggregate_builder(domain)
    -> builder(state, packet)
    -> DomainAggregate

runtime validates aggregate + domain binding
runtime invokes GuardX108().decide(aggregate)
```

## Non-negotiable invariants

- canonical `_DOMAIN_PIPELINES` have strict precedence;
- extension is consulted only for an absent canonical domain;
- extension cannot return a sovereign decision envelope through the supported contract;
- only real `GuardX108().decide()` renders the extension-domain x108 gate;
- no resolver preserves the historical unsupported-domain fail-closed path;
- feedback cycles require a fresh decision;
- KX108_ONLY remains unchanged;
- no kernel/proof/Sigma contract mutation;
- no automatic plugin discovery;
- no remote/untrusted Python extension loading;
- no implicit Binder, memory-write or world-action authority.

## Security audit closure

`F25-AUDIT-001` found that the initial pipeline-returning draft could theoretically allow a hostile in-process extension to fabricate a dataclass decision envelope.

That draft is rejected and is NOT the frozen design.

The frozen aggregate-only seam rejects a forged `CanonicalDecisionEnvelope(ALLOW)` before decision persistence/execution.

## Evidence at freeze

Cross-repository hardened proof:

```text
102 passed in 0.42s
run 37527113296
```

Main native baseline:

```text
11 failed, 12443 passed, 46 skipped, 207 deselected
run 37508621493
```

Native hardened branch confirmation is tracked separately because the global workflow already has inherited baseline failures.

## Change control

Any change to:
- resolver method names;
- aggregate-only rule;
- canonical precedence;
- Guard invocation location;
- unsupported-domain behavior;
- feedback propagation;
- authority flags;

requires:

1. an explicit `UNFREEZE_F25_V0` record;
2. new tests;
3. a new audit receipt;
4. a new freeze version.

## Main protection

This freeze authorizes **no merge, no push, no cherry-pick and no fast-forward to `main`**.
