# WORLD_ACTION Bounded Executor V0

Date: 2026-10-07

Branch:
`feat/world-action-bounded-executor-v0`

Base:
`feat/world-action-live-gateway-v0`

Draft PR:
`#61`

Main mutation:
`NO`

Real network connector:
`NO`

## Purpose

Close the universal executor/receipt/replay/recovery architecture without
binding any real network-capable connector.

The executor is deliberately restricted to deterministic sandbox adapters.

## Canonical chain

```text
Domain facts
→ UniversalActionProposal
→ exact WorldActionRequest
→ exact HumanApproval
→ WORLD_ACTION_PRE_EXECUTION
→ persisted KX108 ALLOW
→ ExternalRuntimeActivationPolicy
→ LiveSovereignTicketV0
→ ObsidiaLiveGatewayV0
→ LIVE_PREFLIGHT_READY
→ BoundedConnectorExecutorV0
→ sandbox provider outcome
→ append-only execution receipt
→ replay / duplicate guard / reconciliation
```

## Executor boundary

V0 requires all of the following before the adapter is called:

- exact LIVE Gateway revalidation
- exact connector-call hash
- exact target reference
- exact target pre-state hash
- exact scope
- exact idempotency key
- adapter connector id/action/scope exact match
- `execution_mode=SANDBOX_DETERMINISTIC`
- `external_network_capable=false`
- `side_effect_free=true`

Any real-network adapter is rejected with:

`EXTERNAL_NETWORK_ADAPTER_FORBIDDEN_V0`

Any non-sandbox executor mode is rejected with:

`REAL_CONNECTOR_EXECUTOR_NOT_BOUND_V0`

## Outcome model

Four provider outcomes are modeled:

- `CONFIRMED_SUCCESS`
- `CONFIRMED_NO_EFFECT`
- `UNKNOWN_OUTCOME`
- `PROVIDER_REJECTED`

### Confirmed success

Produces an append-only receipt.

Any later attempt with the same idempotency key is blocked:

`DUPLICATE_CONFIRMED_EXECUTION_BLOCK`

### Confirmed no effect

The receipt can mark retry as eligible only when the adapter policy explicitly
permits retry after a proven no-effect result.

### Unknown outcome

Retry is blocked:

`UNKNOWN_PRIOR_OUTCOME_RECONCILIATION_REQUIRED`

A separate append-only `WorldActionReconciliationV0` is required.

The reconciliation must carry:

- exact unknown receipt id/hash
- exact idempotency key
- provider verification reference
- human review reference
- one resolution:
  - `CONFIRMED_SUCCESS`
  - `CONFIRMED_NO_EFFECT`

It is explicitly non-sovereign:

`is_execution_authority=false`

If reconciliation proves success, duplicate execution remains blocked.

If reconciliation proves no effect, the unknown-outcome block can be cleared
and a retry can proceed through the full gate again.

### Provider rejected

A later attempt is blocked pending a new decision:

`PROVIDER_REJECTED_NEW_DECISION_REQUIRED`

## Receipt

`WorldActionExecutionReceiptV0` binds:

- action/source domain
- live sovereign ticket id/hash
- activation policy hash
- world-action request hash
- connector id/action
- connector-call hash
- target ref/pre-state
- required scope
- idempotency key
- provider id
- provider outcome
- provider receipt/state references
- recovery state
- retry policy result
- execution mode
- decision authority

Receipt properties in V0:

```text
sandbox_execution = true
real_external_effect = false
network_call_performed = false
decision_authority = KX108_ONLY
```

Receipt replay rechecks:

- receipt integrity hash
- exact sovereign-ticket hash
- exact connector-call hash
- exact idempotency key

## Runtime facts

Current stack facts:

```text
world_action_pre_execution_rail_present = true
world_action_live_gateway_capability_present = true
world_action_bounded_executor_contract_present = true
world_action_runtime_activated = false
execution_authority = false
emits_act = false
```

The two external blockers remain:

- EXTERNAL_WORLD_ACTUATION_NOT_ACTIVATED
- REAL_X108_GATED_EXECUTION_PATH_NOT_ACTIVATED

## Proof

Targeted proof:

```text
78 / 78 PASS
run 37601883581
0.64 s
```

Coverage includes:

- PRE KX108
- LIVE ticket
- activation policy
- LIVE Gateway
- exact connector-call rebinding
- sandbox executor
- append-only receipt
- receipt replay
- duplicate success block
- confirmed-no-effect retry
- unknown-outcome retry block
- unknown reconciliation to no-effect
- unknown reconciliation to success
- provider rejection
- adapter network-capability refusal
- adapter side-effect refusal
- adapter identity mismatch
- runtime-facts regression
- historical V4 dry-run gateway/ticket regressions

## Protected core

Compared with the LIVE Gateway base branch:

`0 protected files changed`

No change to:

- sigma/guard.py
- sigma/contracts.py
- sigma/protocols.py
- sigma/aggregation.py
- proofs/lean
- formal/tla
- merkle_seal.json

## Verdict

`WORLD_ACTION_BOUNDED_EXECUTOR_RECEIPT_RECOVERY_V0_PROVEN`

and simultaneously:

`REAL_EXTERNAL_WORLD_ACTUATION_NOT_ACTIVATED`

## What remains before a real pilot

The universal architecture is now complete through a bounded executor contract.

The remaining step is no longer another governance layer. It is to bind one
specific real connector adapter under explicit pilot authorization and prove:

1. one low-risk exact external action
2. provider response capture
3. real receipt
4. replay
5. no duplicate
6. unknown-outcome recovery

That pilot must be separately authorized; V0 does not perform it.
