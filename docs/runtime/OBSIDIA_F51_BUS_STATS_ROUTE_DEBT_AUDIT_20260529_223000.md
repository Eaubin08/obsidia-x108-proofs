# F51 — Bus Stats Route Debt Audit

**Artifact:** `OBSIDIA_F51_BUS_STATS_ROUTE_DEBT_AUDIT_20260529_223000`  
**Palier:** F51  
**Parent:** F50_LIVE_DEMO_SERVER_ORCHESTRATION_AUDIT  
**Status:** PASS_WITH_FINDINGS  
**Date:** 2026-05-29  
**Head:** cdc3c98  

---

## Purpose

F51 audits the `/bus/stats` 404 debt detected out-of-scope during the F50 background test run. F51 is AUDIT ONLY — no patches, no route creation, no commits.

---

## Issue

| Field | Value |
|-------|-------|
| Route expected | `GET /bus/stats` |
| Observed | 404 Not Found |
| Companion route | `GET /bus/bridge` |
| Companion observed | 404 Not Found |
| Source test | `tests/api/test_output_envelope_bus_stats.py` |
| Companion test | `tests/api/test_output_envelope_bus_bridge.py` |
| In F50 scope | No |
| Introduced commit | `a5f21c6` — 2026-05-26 |
| Introduced by | `chore: clean repo hygiene and exclude generated audit artifacts` |

---

## Classification

**Primary:** `ROUTE_MISSING_CONFIRMED`

The `output_envelope.py` utility module exists and is correct. Tests were written expecting `GET /bus/stats` and `GET /bus/bridge` HTTP endpoints. No router file (`bus.py` / `bus_stats.py`) was ever created. No `include_router()` call for a bus router exists in `apps/obsidia_api/main.py`. Both routes return 404 — they were never wired.

**Secondary:** `TEST_OUT_OF_SCOPE`

From Brody V1 / F50 scope: `/bus/stats` is not a Brody V1 API route. The 8 F50-verified routes are unaffected. This debt is orthogonal to the sovereignty/boundary/sanitizer contract.

---

## Root Cause

| Component | Status |
|-----------|--------|
| `apps/obsidia_api/output_envelope.py` | EXISTS — correct implementation |
| Bus router file (`routes/bus.py` or similar) | **MISSING** |
| `include_router()` for bus in `main.py` | **MISSING** |
| OpenAPI entry for `/bus/stats` | **ABSENT** |
| OpenAPI entry for `/bus/bridge` | **ABSENT** |
| Phase 1 (`/bus/stats`) | Not implemented |
| Phase 2 (`/bus/bridge`) | Not implemented |

The `output_envelope.py` module was created with `/bus/stats` as its canonical usage example. A two-phase plan was anticipated:

- **Phase 1:** Wire `/bus/stats` with `build_output_envelope()`
- **Phase 2:** Also wrap `/bus/bridge`

Neither phase was executed. The test contract is complete and correct, but the route handlers are absent.

---

## Test Contract Extracted

Expected behavior of `GET /bus/stats`:

| Field | Expected Value |
|-------|---------------|
| `decision_authority` | `KX108_ONLY` |
| `emits_act` | `false` |
| `emits_verdict` | `false` |
| `memory_write` | `false` |
| `graphiti_write` | `false` |
| `neo4j_write` | `false` |
| `kernel_mutation` | `false` |
| `readonly` | `true` |
| `source` | `OBSIDIA_API` |
| `route` | `/bus/stats` |
| `status` | `OK` |
| `compact` (default) | `false` |
| `debug` (default) | `false` |

**Modes tested:** default / `?compact=true` / `?debug=true`

**Internal bus fields expected in default/debug mode:** `emitted`, `dropped`, `queue_size`

**Deep fields omitted in compact mode:** `brody_context`, `sigma_counters`, `bridge_snapshot`, `bridge_registration`

---

## Evidence

| Check | Result |
|-------|--------|
| OpenAPI contains `/bus/stats` | **false** |
| OpenAPI contains `/bus/bridge` | **false** |
| Route definition file found | **false** |
| `output_envelope.py` module exists | **true** |
| `output_envelope.py` correct | **true** |
| Both phases missing | **true** |
| Test origin pre-F42 | **true** (2026-05-26) |
| F50 baseline 85/85 PASS | **true** |
| F50 routes unaffected | **true** |
| F47.1 sovereignty unaffected | **true** |
| F47.2 sanitizer unaffected | **true** |

---

## Boundary Contract (F51 preserved)

| Flag | Value |
|------|-------|
| `decision_authority` | `KX108_ONLY` |
| `brody_decision` | `false` |
| `kernel_mutation` | `false` |
| `x108_mutation` | `false` |
| `neo4j_write` | `false` |

---

## Recommendation for F52

Two options. Decision belongs to the user.

### Option A — Implement the routes (F52_BUS_STATS_ROUTE_CONTRACT_PATCH)

Create `apps/obsidia_api/routes/bus.py` with `GET /bus/stats` and `GET /bus/bridge` using `build_output_envelope()`. Wire into `main.py` via `include_router()`. Both routes exist in concept — the output_envelope module and the test contract are already complete. Implementation is low-risk.

### Option B — Retire the tests (F52_BUS_STATS_TEST_RETIRE)

If `/bus/stats` and `/bus/bridge` are not planned for Brody V1, mark the test files as `pytest.skip` or remove them. This removes the noise from the test suite without adding runtime code.

---

## F51 Constraints Verified

| Constraint | Status |
|------------|--------|
| No runtime patches | CONFIRMED |
| No route creation | CONFIRMED |
| No test modification | CONFIRMED |
| No Neo4j writes | CONFIRMED |
| No commit | CONFIRMED |
| No tag | CONFIRMED |
| No push | CONFIRMED |
| F50 not broken | CONFIRMED |

---

## JSON Artifact

`docs/runtime/OBSIDIA_F51_BUS_STATS_ROUTE_DEBT_AUDIT_20260529_223000.json`  
SHA256: `3C600EFAC3BF9851A14F1BB41B1C02E91843A516D992D0EF4FC6FB561454D442`

---

*F51 · AUDIT ONLY · PASS_WITH_FINDINGS · KX108_ONLY · 2026-05-29*
