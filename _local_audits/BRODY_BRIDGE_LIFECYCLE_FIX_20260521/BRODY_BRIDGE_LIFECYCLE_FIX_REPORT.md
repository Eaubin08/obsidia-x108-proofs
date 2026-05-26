# Brody Bridge Lifecycle Fix — Report
## BRODY_BRIDGE_LIFECYCLE_REGISTRATION_FIX_PASS

**Created:** 2026-05-22T00:00:00+00:00  
**Session:** Post-crash resumption from RUNTIME_FREEZE 20260521_003721

---

## Summary

The BrodyBridge lifecycle registration was audited and patched across 6 phases.
The fix ensures BrodyBridge attaches to the same `get_bus()` singleton as AuditMiddleware
at FastAPI startup, via an idempotent `ensure_brody_bridge_registered()` call in the lifespan hook.

A secondary bug was diagnosed and fixed during Phase 6 test validation:
BrodyBridge.handle() emitted a receipt back onto the bus, creating an infinite asyncio feedback
loop that prevented drain_loop cancellation. The receipt emission block was removed.

---

## Chain Verified

```
AuditMiddleware
  → get_bus() singleton (bus_id=2188865445168)
  → publish_nowait(event)
  → UniversalEventBus.drain_loop() dispatches to subscribers
  → BrodyBridge.handle() (ATTACHED, subscriber #1 in test / #4 in app)
  → advisory_response generated
  → buffered in _output_buffer
  → writable to brody_bridge_*.jsonl via write_generated_output()
```

---

## Files Modified

| File | Change | Risk |
|---|---|---|
| `periphery/brody_bridge.py` | Removed receipt re-emission block (lines 107-115) — broke asyncio feedback loop | LOW |
| `apps/obsidia_api/brody_bridge_lifecycle.py` | Created — idempotent ensure_brody_bridge_registered() | LOW |
| `apps/obsidia_api/main.py` | Wired ensure_brody_bridge_registered(_bus) in lifespan hook | LOW |
| `tests/periphery/test_bridge_connection.py` | Created — 6 unit tests for bus↔bridge signal path | NONE |
| `tests/periphery/test_http_audit_generated_output.py` | Created — 3 integration tests with tmp_path JSONL | NONE |

---

## Test Results

| Suite | Result | Duration |
|---|---|---|
| `test_bridge_connection.py` (6 tests) | **6/6 PASS** | 2.12s |
| `test_http_audit_generated_output.py` (3 tests) | **3/3 PASS** | 2.12s |
| `test_brody_three_foundations_no_500.py` (16 tests) | **16/16 PASS** | 89.61s |

---

## Protected Files — Diff

```
sigma/guard.py          — UNTOUCHED
sigma/contracts.py      — UNTOUCHED
sigma/protocols.py      — UNTOUCHED
sigma/aggregation.py    — UNTOUCHED
proofs/lean/            — UNTOUCHED
formal/tla/             — UNTOUCHED
merkle_seal.json        — UNTOUCHED
```

---

## Boundary Invariants Confirmed

| Flag | Value |
|---|---|
| bus_singleton_used | true |
| same_bus_instance | true |
| bridge_registered_on_startup | true |
| duplicate_subscription_prevented | true |
| publish_nowait_reaches_bridge | true |
| generated_output_jsonl_test | PASS |
| memory_write | false |
| graphiti_write | false |
| neo4j_write | false |
| emits_act | false |
| decision_authority | KX108_ONLY |
| kernel_untouched | true |
