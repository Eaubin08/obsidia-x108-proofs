# World Calls Module

**Status:** FIRST_CLASS_X108_MODULE — DRY_RUN_ONLY
**Source:** `periphery/world_calls/` (12 modules)
**Tests:** `tests/periphery/test_world_*.py` + `tests/non_sovereignty/test_world_*.py`

## Modules

| Module | Role |
|--------|------|
| `action_risk_classifier.py` | Classifies action risk (READ_ONLY → IRREVERSIBLE) |
| `world_call_classifier.py` | Classifies world call type (NO_WORLD_CALL → FORBIDDEN) |
| `sovereign_ticket.py` | Issues SovereignTicket for controlled egress |
| `obsidia_gateway.py` | Main gateway — checks ticket + world call class |
| `world_action_bus.py` | Append-only local event bus for world actions |
| `secret_boundary.py` | Blocks secrets from reaching agents |
| `world_executor_dryrun.py` | Dry-run executor — never executes real actions |
| `egress_policy.py` | Egress policy rules |
| `route_policy_x25.py` | Route policy matrix |
| `ticket_store.py` | Ticket storage |
| `autonomy_level_matrix.py` | Autonomy level definitions |

## Sovereignty Invariants
- No world call without SovereignTicket
- Gateway = dry-run only
- No real egress. No real ACT.
