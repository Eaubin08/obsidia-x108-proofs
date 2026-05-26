# World Call Gateway Integration Report — V4

**Date:** 2026-05-19

## Architecture

```
ActionCandidate
    ↓
classify_action_risk()  → ActionRiskClass
    ↓
classify_world_call()   → WorldCallClass
    ↓
compute_autonomy_level() → AutonomyLevel (0-5)
    ↓
issue_sovereign_ticket() → SovereignTicket (dry_run_only=True always)
    ↓
ObsidiaGateway.check()  → GatewayDecision (egress_allowed=False always)
    ↓
WorldActionBus.publish() → append-only local journal (no real egress)
```

## Invariants

1. **No Ticket → No World Call**: Every world call attempt without a valid sovereign ticket returns `gate_result=BLOCK`.
2. **egress_allowed=False**: The `ObsidiaGateway` never sets `egress_allowed=True` in V4.
3. **dry_run_only=True**: Every `SovereignTicket` and `WorldActionDryRunPacket` has `dry_run_only=True`.
4. **Append-only**: The `WorldActionBus` and `TicketStore` only append, never overwrite.
5. **Secret boundary**: `assert_no_secret_in_agent_payload()` runs before any gateway pass.

## WorldCallClass Hierarchy

| Class | Blocked |
|---|---|
| NO_WORLD_CALL | No |
| READ_ONLY | No |
| REVERSIBLE | No |
| IRREVERSIBLE | No (but requires autonomy level 4+) |
| CRITICAL | Yes |
| FORBIDDEN | Yes |

## Files Created

- `periphery/world_calls/world_call_classifier.py`
- `periphery/world_calls/action_risk_classifier.py`
- `periphery/world_calls/autonomy_level_matrix.py`
- `periphery/world_calls/sovereign_ticket.py`
- `periphery/world_calls/ticket_store.py`
- `periphery/world_calls/world_action_bus.py`
- `periphery/world_calls/secret_boundary.py`
- `periphery/world_calls/obsidia_gateway.py`
- `periphery/world_calls/egress_policy.py`
- `periphery/world_calls/route_policy_x25.py`
- `periphery/world_calls/world_executor_dryrun.py`
- `periphery/schemas/sovereign_ticket.schema.json`
- `periphery/schemas/world_action_event.schema.json`
