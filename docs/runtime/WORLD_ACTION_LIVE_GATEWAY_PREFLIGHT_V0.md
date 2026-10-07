# WORLD_ACTION LIVE Gateway Preflight V0

Date: 2026-10-07

Branch:
`feat/world-action-live-gateway-v0`

Base:
`feat/world-action-pre-execution-v0`

Draft PR:
`#60`

Main mutation:
`NO`

External connector execution:
`NO`

## Purpose

Close the universal LIVE authorization boundary without binding a real network
executor yet.

The system can now prove that one exact external-world action is eligible to
reach a future connector executor, but V0 intentionally stops before any
network/API call.

## Canonical chain

```text
domain adapter
→ UniversalActionProposal
→ exact WorldActionRequest
→ exact HumanApproval
→ WORLD_ACTION_PRE_EXECUTION
→ persisted KX108 ALLOW
→ explicit ExternalRuntimeActivationPolicy
→ LiveSovereignTicketV0
→ ObsidiaLiveGatewayV0
→ LIVE_PREFLIGHT_READY
→ STOP (no executor bound)
```

## Explicit activation policy

`ExternalRuntimeActivationPolicyV0` is infrastructure policy only.

It:

- defaults to `enabled=false`
- carries an explicit operator approval reference
- binds exact connector / connector action / scope tuples
- limits allowed world-call classes
- limits allowed action-risk classes
- caps autonomy at level 4
- expires
- is hash-verified
- declares `is_execution_authority=false`
- keeps `decision_authority=KX108_ONLY`

It cannot produce ALLOW/HOLD/BLOCK.

Unsafe classes are rejected at policy construction:

- IRREVERSIBLE_WORLD_CALL
- CRITICAL_WORLD_CALL
- FORBIDDEN_WORLD_CALL
- ACTION_FINANCIAL
- ACTION_COMPLIANCE_BOUND
- ACTION_SENSITIVE
- ACTION_IRREVERSIBLE
- ACTION_FORBIDDEN

V0 therefore opens only low-risk read-only / reversible capability.

## LIVE sovereign ticket

`LiveSovereignTicketV0` is distinct from the historical V4
`SovereignTicket`.

Issuance requires reload + verification of:

1. exact persisted KX108 decision record
2. decision phase == WORLD_ACTION_PRE_EXECUTION
3. x108_gate == ALLOW
4. exact immutable WORLD_ACTION_PRE context
5. exact context hash
6. exact request hash
7. exact connector-call hash
8. exact human-approval hash
9. exact target pre-state hash
10. exact required scope
11. exact idempotency key
12. exact source domain/action identity
13. active activation policy
14. operation/class/autonomy allow-list match

Ticket properties:

- TTL <= 300 seconds
- `dry_run_only=false`
- `live_egress_preflight_capable=true`
- `executor_bound=false`
- hash-verified
- KX108_ONLY

A HOLD/BLOCK record cannot issue a LIVE ticket.

## LIVE Gateway preflight

`ObsidiaLiveGatewayV0` validates again:

- LIVE ticket integrity/expiry
- exact activation-policy id/hash
- exact connector id/action
- exact connector-call hash
- exact target reference
- exact current pre-state hash
- exact required scope
- exact idempotency key

Success returns:

```text
gate_result = LIVE_PREFLIGHT_READY
egress_preflight_allowed = true
egress_allowed = false
executor_bound = false
network_call_performed = false
```

This distinction is intentional.

The Gateway has become LIVE-capable; the runtime has not yet been activated.

## Legacy isolation

The old dry-run `SovereignTicket` is rejected by the LIVE Gateway.

Existing V4 Gateway and dry-run surfaces are unchanged.

## Runtime facts

Current facts:

```text
world_action_pre_execution_rail_present = true
world_action_live_gateway_capability_present = true
world_action_runtime_activated = false
execution_authority = false
emits_act = false
```

The following blockers remain deliberately present:

- EXTERNAL_WORLD_ACTUATION_NOT_ACTIVATED
- REAL_X108_GATED_EXECUTION_PATH_NOT_ACTIVATED

## Proof

Targeted proof:

```text
64 / 64 PASS
run 37601273459
0.54 s
```

Coverage includes:

- activation policy OFF/tamper
- unsafe class refusal
- real WORLD_ACTION_PRE KX108 ALLOW requirement
- HOLD cannot issue LIVE ticket
- exact scope allow-list
- LIVE ticket self-verification
- exact Gateway binding checks
- pre-state substitution BLOCK
- connector/action/call substitution BLOCK
- scope substitution BLOCK
- idempotency substitution BLOCK
- legacy dry-run ticket rejection
- ticket expiry
- PRE regression
- runtime-link facts
- V4 dry-run Gateway regression
- no-ticket/no-world-call regression
- SovereignTicket/OS3/PoG regression

## Protected core

No protected file is modified relative to the PRE branch:

- sigma/guard.py unchanged
- sigma/contracts.py unchanged
- sigma/protocols.py unchanged
- sigma/aggregation.py unchanged
- proofs/lean unchanged
- formal/tla unchanged
- merkle_seal.json unchanged

## Verdict

`WORLD_ACTION_LIVE_GATEWAY_PREFLIGHT_V0_PROVEN`

and simultaneously:

`REAL_EXTERNAL_WORLD_ACTUATION_NOT_ACTIVATED`

## Next

The next and last architectural boundary before a real pilot is a bounded
connector executor contract.

That future executor must consume only LIVE_PREFLIGHT_READY + exact live ticket,
must preserve idempotency/reconciliation rules, and must produce provider
receipt/replay evidence.

No real connector should be invoked without a separately authorized pilot.
