# WORLD_ACTION_PRE_EXECUTION V0

Date: 2026-10-07

Branch:
`feat/world-action-pre-execution-v0`

Base:
`feat/f2-5-portable-domain-resolver-seam-v0`

Main mutation:
`NO`

## Purpose

Add one canonical sovereign KX108 checkpoint for exact external-world action
requests without activating external egress.

This closes the missing PRE-decision producer identified by the universal
Decision-Execution work while preserving the existing dry-run world-action
boundary.

## Canonical chain

```text
domain adapter
→ universal action proposal
→ exact world-action request
→ exact human approval
→ immutable WORLD_ACTION_PRE context
→ GuardX108.decide()
→ immutable kxworld-* decision record
→ dry-run PRE evidence
→ STOP
```

The stop is intentional. Current SovereignTicket/Gateway/WorldActionBus remain
dry-run only.

## Native KX108 decision phase

The canonical decision store now supports:

`WORLD_ACTION_PRE_EXECUTION`

with a dedicated binding set:

- world-action PRE context id/hash
- world-action request hash
- connector call hash
- human approval hash
- target pre-state hash
- required scope
- idempotency key
- source domain
- action id

It is additive and does not change historical PRE_EXECUTION,
AGENT_PRE_EXECUTION or POST_EXECUTION records.

## Structural kernel-domain token

`world_action` is supplied by the PRE translator through a local enum-like token. `sigma/contracts.py` remains protected and unchanged.

Business meaning is not moved into the kernel.

The original métier domain is retained as `source_domain`; the
WORLD_ACTION translator submits only structural facts:

- unknowns
- contradictions
- risk flags
- evidence refs
- world-call class
- action-risk class
- autonomy level
- exact binding hashes

KX108 remains the only producer of ALLOW / HOLD / BLOCK.

## Exact request verification

The upstream context layer does not trust caller-provided hashes.

It recomputes:

1. connector-call SHA-256
2. idempotency key
3. full world-action request SHA-256
4. exact human-approval SHA-256

Any mismatch is rejected before KX108.

## Secret boundary

Connector args are inspected before context creation.

Fields indicating credentials, passwords, tokens, API keys, authorization,
private keys or similar secrets are rejected.

The immutable KX108 context stores only hashes and action metadata, never raw
connector args.

## Policy fail-closed

The translator automatically introduces blocking contradictions for:

- CRITICAL_WORLD_CALL
- FORBIDDEN_WORLD_CALL
- ACTION_FORBIDDEN

A clean structurally complete request can reach real GuardX108 ALLOW, but this
does not enable egress.

## Runtime facts

New observable fact:

`world_action_pre_execution_rail_present=true`

The following remain false / missing:

- `world_action_runtime_activated=false`
- `execution_authority=false`
- `emits_act=false`
- `EXTERNAL_WORLD_ACTUATION_NOT_ACTIVATED`
- `REAL_X108_GATED_EXECUTION_PATH_NOT_ACTIVATED`

This distinction is intentional:

```text
PRE sovereign decision producer present
!=
external world execution activated
```

## Proof

Targeted regression:

```text
76 / 76 PASS
run 37599687908
```

Coverage includes:

- new WORLD_ACTION_PRE integration suite
- runtime-link facts
- existing KX108 decision-record rail
- Gateway dry-run-only proof
- no-ticket/no-world-call proof
- V4 world-call Gateway pipeline
- SovereignTicket / OS3 / PoG chain

## Current verdict

`WORLD_ACTION_PRE_EXECUTION_CANONICAL_PRODUCER_V0_PROVEN`

and simultaneously:

`REAL_EXTERNAL_WORLD_ACTUATION_NOT_ACTIVATED`

## Next

The next phase may add a live-capable external ticket/gateway path behind an
explicit activation contract, while keeping the existing dry-run path as the
default.

No real connector should be invoked until that separate activation phase is
proved.

## Protected-core boundary

- protected `sigma/contracts.py` unchanged
- protected `sigma/guard.py` unchanged
- protected `sigma/protocols.py` unchanged
- KX108 engine mutation: NO
