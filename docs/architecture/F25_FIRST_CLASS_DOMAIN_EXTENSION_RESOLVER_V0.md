# F2.5 — FIRST-CLASS DOMAIN EXTENSION RESOLVER SEAM V0

Date: 2026-10-06
Branch: `feat/f2-5-portable-domain-resolver-seam-v0`

## Objective

Promote the domain-resolution seam into the canonical governed runtime source without changing default behavior.

## API

`run_governed_runtime_cycle(..., domain_extension_resolver=None)`

`run_governed_feedback_cycle(..., domain_extension_resolver=None)`

The extension contract is intentionally tiny:

```text
is_supported_domain(domain) -> bool
resolve_domain_pipeline(domain) -> callable(state, packet) -> envelope
```

## Resolution rule

```text
canonical _DOMAIN_PIPELINES first
then optional extension
otherwise fail closed
```

An extension is never consulted for an existing canonical domain, so it cannot shadow Bank, Trading, Ecom or GPS.

With `domain_extension_resolver=None`, the existing code path keeps the same canonical lookup and unsupported-domain refusal semantics.

## Authority boundary

The resolver only supplies routing. It receives no authority from the coordinator.

The returned pipeline still has to produce the envelope consumed by the existing canonical lifecycle. All downstream controls remain unchanged: context validation, Guard/KX108 result, decision-record persistence/verification, OS3 ticket/replay, execution authorization, provider binding, receipt and readonly feedback.

## Fail closed

Invalid resolver shape, support-check failure, pipeline-resolution failure or non-callable pipeline raise a transport/contract error; they do not synthesize a decision.

## Feedback

The resolver dependency is explicitly propagated into `run_governed_feedback_cycle`, so t1+ requires a fresh KX108 decision through the same domain route. No previous authority is inherited.
