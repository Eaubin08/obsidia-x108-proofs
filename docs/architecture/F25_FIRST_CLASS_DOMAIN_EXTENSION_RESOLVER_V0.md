# F2.5 — FIRST-CLASS DOMAIN EXTENSION RESOLVER SEAM V0

Date: 2026-10-06
Status: MERGE-CANDIDATE / NOT MAIN

## Objective

Expose a first-class, optional domain-extension seam in the governed runtime without changing default behavior or moving decision authority outside KX108.

## Public runtime dependency

```text
run_governed_runtime_cycle(..., domain_extension_resolver=None)
run_governed_feedback_cycle(..., domain_extension_resolver=None)
```

Default remains `None`.

## Resolver contract

The resolver is routing-only and trusted host configuration. It must expose:

```text
is_supported_domain(domain) -> bool
resolve_domain_aggregate_builder(domain)
    -> callable(domain_state, PeripheralSignalPacket)
    -> DomainAggregate
```

Critical security rule:

**an extension never returns CanonicalDecisionEnvelope and never renders ALLOW/HOLD/BLOCK.**

The extension may construct only the non-sovereign `DomainAggregate`. The governed runtime then invokes the real `GuardX108().decide(aggregate)` itself.

## Resolution order

```text
1. canonical _DOMAIN_PIPELINES
2. optional extension aggregate builder
3. fail closed
```

Canonical domains have immutable precedence. The extension is not consulted for Bank, Trading, Ecom, GPS or any other built-in domain.

## Why aggregate-only

An earlier F2.5 candidate accepted an extension-supplied pipeline returning an envelope. Audit found that this shape was too permissive: Python code could fabricate a dataclass-shaped `CanonicalDecisionEnvelope` carrying `ALLOW` and the decision store only verified dataclass shape, not cryptographic Guard provenance.

The candidate was hardened before freeze.

Now:

```text
extension
  -> DomainAggregate only
runtime
  -> validates DomainAggregate + domain binding
runtime
  -> real GuardX108.decide()
  -> CanonicalDecisionEnvelope
```

Therefore the extension cannot supply the sovereign gate through the supported contract.

## Default compatibility

With `domain_extension_resolver=None`:
- existing `is_supported_domain()` behavior is unchanged;
- existing canonical `resolve_domain_pipeline()` behavior is unchanged;
- unsupported domains are refused before decision;
- no extension code runs.

## Feedback cycles

`run_governed_feedback_cycle()` propagates the same explicit resolver dependency into the next cycle. The previous decision remains evidence only and a fresh GuardX108 decision is required.

## Trust boundary

This seam does not sandbox arbitrary Python plugins. Resolver objects must be explicitly supplied by trusted host/runtime configuration. No auto-discovery, remote code loading or third-party plugin execution is introduced by F2.5.

## Non-goals

- no change to GuardX108;
- no change to sigma contracts;
- no change to canonical domain tables;
- no Binder authority granted to the resolver;
- no memory write authority;
- no external-world authority;
- no CSSA business semantics in the core.
