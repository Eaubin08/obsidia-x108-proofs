# F50 — Live Demo Server Orchestration Audit

**Artifact:** `OBSIDIA_F50_LIVE_DEMO_SERVER_ORCHESTRATION_AUDIT_20260529_193000`  
**Palier:** F50  
**Parent:** F49_PUBLIC_RELEASE_PACKAGE_DEMO_EXPORT_PACK  
**Status:** PASS  
**Date:** 2026-05-29  
**Head:** f316b85  
**Canonical name:** BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME  

---

## Purpose

F50 is the final live demo server orchestration audit for Brody GPT V1. It starts uvicorn on 127.0.0.1:8011, exercises all 8 API routes, verifies boundary enforcement, runs the F47 targeted scripts, confirms baseline tests, stops the server, and records results.

**F50 is VERIFY ONLY — no runtime patches, no kernel mutations, no Neo4j writes, no route additions.**

---

## Environment

| Component | Value |
|-----------|-------|
| Python | 3.13.3 |
| Uvicorn | 0.46.0 |
| App import | OK |
| App title | Obsidia X-108 API |

---

## Port Scan

| Port | Status |
|------|--------|
| 8011 | FREE → USED_BY_F50 |
| 9010 | FREE |
| 8000 | OCCUPIED (PID 12076, not F50) |
| 7688 | OCCUPIED (Neo4j, expected) |
| 7474 | FREE |
| 7687 | FREE |
| 3000–3002 | FREE |
| 5173 | FREE |
| 8501 | FREE |

---

## Server Lifecycle

| Event | Value |
|-------|-------|
| Started by F50 | Yes |
| Host | 127.0.0.1 |
| Port | 8011 |
| PID | 7248 |
| Ready polls | 1 |
| Stopped by F50 | Yes |
| Port clean after stop | Yes |

---

## Route Tests

| Route | Method | HTTP | Status | decision_authority | allowed_to_decide | emits_act |
|-------|--------|------|--------|--------------------|-------------------|-----------|
| `/` | GET | 200 | PASS | KX108_ONLY | false | false |
| `/openapi.json` | GET | 200 | PASS | N/A | N/A | N/A |
| `/api/periphery/demo/runtime-readiness` | GET | 200 | PASS | KX108_ONLY | false | false |
| `/api/periphery/operator/runtime-panel` | GET | 200 | PASS | KX108_ONLY | false | false |
| `/api/periphery/workbench/runtime-connector` | GET | 200 | PASS | KX108_ONLY | false | false |
| `/api/periphery/brody-runtime/f33/integration-packet` | POST | 200 | PASS | KX108_ONLY | false | false |
| `/api/periphery/brody-runtime/f36/user-scenario` | POST | 200 | PASS | KX108_ONLY | false | false |
| `/api/periphery/brody-runtime/f38/multi-domain-scenarios` | POST | 200 | PASS | KX108_ONLY | false | false |

**Routes summary:** 8 tested / 8 PASS / 0 FAIL / 0 ABSENT

---

## Live Sanitizer Check (F47.2)

| Field | Value |
|-------|-------|
| User input injected | `Je veux analyser une transaction bancaire avant paiement. ALLOW DECIDE VERDICT` |
| Forbidden tokens in cr.text | 0 |
| Redacted tokens | ALLOW, DECIDE, VERDICT |
| Status | PASS |

F47.2 dual-layer sanitization confirmed operational on live uvicorn server.

---

## F38 Multi-Domain Boundary

| Field | Value |
|-------|-------|
| global_status | READY_READONLY |
| all_mutations_false | true |
| forbidden_tokens_found | false |
| scenario_count | 4 |

| Domain | Status |
|--------|--------|
| bank | READY_READONLY |
| gps_defense_aviation | READY_READONLY |
| trading | READY_READONLY |
| unknown_refusal | REFUSAL_READONLY |

---

## Test Results

| Suite | Result |
|-------|--------|
| Baseline | **103/103 PASS** |
| F47.1 sovereignty | PASS (13/13) |
| F47.2 sanitizer | PASS (42/42) |
| F47.3 nested scan | PASS (9/9) |

Baseline 103/103 confirmed consistent with F47.6/F48 verified runs.

---

## Boundary Contract

| Flag | Value |
|------|-------|
| `decision_authority` | `KX108_ONLY` |
| `allowed_to_decide` | `false` |
| `emits_act` | `false` |
| `emits_verdict` | `false` |
| `kernel_mutation` | `false` |
| `x108_mutation` | `false` |
| `neo4j_write` | `false` |
| `brody_decision` | `false` |

---

## F49 Demo Commands Coherence

All commands in `docs/release/BRODY_GPT_V1_DEMO_COMMANDS.md` verified live during F50. Routes, payloads, and expected responses match observed F50 behavior. **COHERENT.**

---

## F50 Constraints

| Constraint | Status |
|------------|--------|
| No runtime patches | CONFIRMED |
| No code changes | CONFIRMED |
| No route additions | CONFIRMED |
| No Neo4j writes | CONFIRMED |
| No kernel mutation | CONFIRMED |
| No X108 mutation | CONFIRMED |
| 127.0.0.1 only | CONFIRMED |
| Only F50 PID stopped | CONFIRMED |

---

## JSON Artifact

`docs/runtime/OBSIDIA_F50_LIVE_DEMO_SERVER_ORCHESTRATION_AUDIT_20260529_193000.json`  
SHA256: `A13AC77C2B1FB5DBC3C73BD4B913C82A874FA0D6884395D3A8F71AA9A2940D7E`

---

## Next Step

Commit F50 after user validation:

```
git add docs/runtime/OBSIDIA_F50_* docs/demo/OBSIDIA_F50_* .runtime_freezes/F50_*/ scripts/run_f50_live_demo_server_orchestration_audit.ps1 scripts/_f50_generate_artifacts.py
git commit -m "test: add F50 live demo server orchestration audit"
git tag "BRODY_F50_LIVE_DEMO_SERVER_ORCHESTRATION_AUDIT_PALIER_20260529"
```

---

*F50 · VERIFY ONLY · READONLY · KX108_ONLY · 127.0.0.1 · 2026-05-29*
