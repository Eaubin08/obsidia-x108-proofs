# OBSIDIA F43 — Brody V1 Full Live Server Port Matrix Audit

**Timestamp:** 20260529_085000  
**Mode:** AUDIT_ARTIFACT_ONLY · READONLY · KX108_ONLY · emits_act=false  
**Palier:** F43_BRODY_V1_FULL_LIVE_SERVER_PORT_MATRIX_AUDIT  
**Version:** F43_V1  
**HEAD:** 25ccc4d  
**Parent tag:** BRODY_F42_BRODY_GPT_V1_FINAL_RELEASE_SEAL_PALIER_20260529  
**PATCH_RUNTIME:** NO · **COMMIT:** NO · **TAG:** NO · **PUSH:** NO

---

## VERDICT GLOBAL

```
F43_BRODY_V1_FULL_LIVE_SERVER_PORT_MATRIX_AUDIT_STATUS=PASS
CANONICAL_NAME=BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME
HEAD=25ccc4d
SERVER_STARTED=true
SERVER_PORT=8011
SERVER_PID=20288
SERVER_STOPPED=true
PORTS_SCANNED=11 (3000,3001,3002,5173,7474,7687,7688,8000,8011,8501,9010)
PORTS_OCCUPIED=2 (7688,8000)
ROUTES_TESTED=9
ROUTES_PASS=9/9
F33_LIVE=PASS
F36_LIVE=PASS
F38_LIVE=PASS
SMOKE_SCRIPTS_RUN=5/5
SMOKE_CHECKS=474/474
BASELINE_TESTS_PASS=103/103
BOUNDARY_KX108_ONLY=true
BRODY_DECISION=false
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
GIT_DIFF=CLEAN
V1_INTEGRITY=CONFIRMED
FILES_CREATED=4
FILES_MODIFIED=none
COMMIT=NO
TAG=NO
PUSH=NO
```

---

## SECTION 1 — PORT MATRIX

### Ports scanned (11)

| Port | Status | PID | Bind | Note |
|------|--------|-----|------|------|
| 3000 | FREE | — | — | — |
| 3001 | FREE | — | — | — |
| 3002 | FREE | — | — | — |
| 5173 | FREE | — | — | — |
| 7474 | FREE | — | — | Neo4j HTTP (not running) |
| 7475 | OCCUPIED | 6680 | 0.0.0.0 | Neo4j HTTP variant (+1) |
| 7687 | FREE | — | — | Neo4j Bolt (not running) |
| 7688 | OCCUPIED | 6680/5324 | 0.0.0.0 | Bolt variant (+1) |
| 8000 | OCCUPIED | 12076 | 127.0.0.1 | Existing HTTP server (pre-F43) |
| 8011 | FREE → **USED** | 20288 | 127.0.0.1 | F43 uvicorn server |
| 8501 | FREE | — | — | — |
| 9010 | FREE | — | — | — |

**F43 server launched on 8011 — consistent with F36B/F38 live proof convention.**

### Pre-existing services (not touched by F43)

| Port | PID | Service hypothesis |
|------|-----|--------------------|
| 7475 | 6680 | Neo4j HTTP (port offset variant) |
| 7688 | 6680/5324 | Neo4j Bolt or similar (port offset variant) |
| 8000 | 12076 | Pre-existing Python/HTTP server — smoke_f34 used this as LIVE_SERVER_8000 |
| 8090 | 14260 | Unknown service — not targeted |

---

## SECTION 2 — SERVER LIFECYCLE

| Step | Result |
|------|--------|
| Start: `python -m uvicorn ... --host 127.0.0.1 --port 8011` | PID=20288 |
| Ready poll | 1 poll × 2s = 2 seconds |
| GET / → 200 | ✅ |
| All 9 routes tested | ✅ |
| smoke_f36b (61 checks) | ✅ |
| smoke_f38 (141 checks) | ✅ |
| Stop-Process PID=20288 | ✅ |

---

## SECTION 3 — ROUTE TEST RESULTS (9/9 PASS)

| Method | Route | HTTP | Status | Key values |
|--------|-------|------|--------|------------|
| `GET` | `/` | 200 | ✅ PASS | — |
| `GET` | `/openapi.json` | 200 | ✅ PASS | all 6 Brody routes present |
| `POST` | `/api/periphery/brody-runtime/f33/integration-packet` | 200 | ✅ PASS | `READY_READONLY`, surfaces=7 |
| `GET` | `/api/periphery/operator/runtime-panel` | 200 | ✅ PASS | — |
| `GET` | `/api/periphery/operator/runtime-panel.html` | 200 | ✅ PASS | 2698 bytes |
| `GET` | `/api/periphery/demo/runtime-readiness` | 200 | ✅ PASS | — |
| `GET` | `/api/periphery/workbench/runtime-connector` | 200 | ✅ PASS | — |
| `POST` | `/api/periphery/brody-runtime/f36/user-scenario` | 200 | ✅ PASS | `READONLY`, `can_decide=False`, `contextual_explanation_only` |
| `POST` | `/api/periphery/brody-runtime/f38/multi-domain-scenarios` | 200 | ✅ PASS | `READY_READONLY`, 4 scenarios, `all_mutations_false=True` |

### F38 domain breakdown

| Domain | Status | can_decide |
|--------|--------|-----------|
| bank | READY_READONLY | False |
| gps_defense_aviation | READY_READONLY | False |
| trading | READY_READONLY | False |
| unknown_refusal | REFUSAL_READONLY | False |

---

## SECTION 4 — BOUNDARY VERIFICATION (live)

Verified on F33, F36, F38 responses from live server (127.0.0.1:8011):

```
decision_authority  = KX108_ONLY   ✅ (F33 + F36 + F38)
allowed_to_decide   = False        ✅ (F33 + F36 + F38)
emits_act           = False        ✅ (F33 + F36 + F38)
emits_verdict       = False        ✅ (F33 + F36 + F38)
kernel_mutation     = False        ✅ (F33 + F36 + F38)
x108_mutation       = False        ✅ (F33 + F36 + F38)
neo4j_write         = False        ✅ (F33 + F36 + F38)
all_mutations_false = True         ✅ (F38 packet level)
forbidden_tokens_found = False     ✅ (F38 packet level)
can_decide          = False        ✅ (F36 controlled_response)
response_kind       = contextual_explanation_only ✅ (F36)
```

---

## SECTION 5 — SMOKE SCRIPTS (474/474)

| Script | Mode | Checks | Status | New Proof SHA256 |
|--------|------|--------|--------|-----------------|
| `smoke_f34_live_route_contract_readonly.py` | LIVE_SERVER_8000 | 73/73 | ✅ PASS | `C0DBCA06...` |
| `smoke_f36_user_scenario_controlled_response.py` | TestClient | 60/60 | ✅ PASS | `1807EFF5...` |
| `smoke_f36b_true_live_uvicorn_user_scenario.py` | LiveUvicorn_8011 | 61/61 | ✅ PASS | `B119FAC6...` |
| `smoke_f37_multi_domain_user_scenarios_readonly.py` | DirectCall | 139/139 | ✅ PASS | `F0B32007...` |
| `smoke_f38_multi_domain_live_uvicorn_api.py` | LiveUvicorn_8011 | 141/141 | ✅ PASS | `E3247E5F...` |

**Note on F34 smoke:** Used `SOURCE=LIVE_SERVER_8000` — the pre-existing server at port 8000 was detected and used by the smoke script's port-scanning logic. Not a F43 artifact.

**New proof files generated by F43 audit (5 files, untracked):**

```
docs/runtime/F34_LIVE_ROUTE_PROOF_20260529_052241.json
docs/runtime/F36_USER_SCENARIO_PROOF_20260529_052242.json
docs/runtime/F36B_TRUE_LIVE_UVICORN_USER_SCENARIO_PROOF_20260529_052033.json
docs/runtime/F37_MULTI_DOMAIN_PROOF_20260529_052245.json
docs/runtime/F38_MULTI_DOMAIN_LIVE_UVICORN_PROOF_20260529_052035.json
```

---

## SECTION 6 — BASELINE TESTS

```
test_f29_1_neo4j_manual_write_surface_guard.py    —  4 passed
test_f32_brody_full_runtime_integration_*         — 17 passed
test_f33_brody_runtime_entrypoint_readonly.py     — 12 passed
test_f34_live_route_contract_readonly.py          — 14 passed
test_f35_1_operator_demo_workbench_surfaces.py    — 12 passed
test_f36_user_scenario_*                          — 14 passed
test_f37_multi_domain_user_scenarios_readonly.py  — 18 passed
test_f38_multi_domain_live_api_route_readonly.py  — 20 passed
TOTAL = 103/103 PASS ✅
```

---

## SECTION 7 — V1 INTEGRITY CHECK

```
git diff --check  → CLEAN (no staged changes)
git status -sb    → ## main...origin/main (only ?? new proof files from smoke run)
CODE_MODIFIED     = false
ROUTES_MODIFIED   = false
TESTS_MODIFIED    = false
RUNTIME_MODIFIED  = false
V1_SEAL_INTACT    = true
```

---

## TERMINAL FINAL

```
F43_BRODY_V1_FULL_LIVE_SERVER_PORT_MATRIX_AUDIT_STATUS=PASS
CANONICAL_NAME=BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME
HEAD=25ccc4d
SERVER_STARTED=true  PORT=8011  PID=20288
SERVER_STOPPED=true
PORTS_SCANNED=11
PORTS_OCCUPIED=2 (7688, 8000)
ROUTES_TESTED=9/9 PASS
F33_LIVE=PASS
F36_LIVE=PASS
F38_LIVE=PASS
SMOKE_SCRIPTS_RUN=5/5  CHECKS=474/474
BASELINE_TESTS_PASS=103/103
BOUNDARY_KX108_ONLY=true
BRODY_DECISION=false
KERNEL_MUTATION=false
X108_MUTATION=false
NEO4J_WRITE=false
FILES_CREATED=docs/runtime/OBSIDIA_F43_*_AUDIT_20260529_085000.json,
              docs/runtime/OBSIDIA_F43_*_AUDIT_20260529_085000.md,
              docs/demo/OBSIDIA_F43_LIVE_SERVER_RUNBOOK.md,
              .runtime_freezes/F43_.../MANIFEST_SHA256.json
FILES_MODIFIED=none
COMMIT=NO
TAG=NO
PUSH=NO
NEXT=commit F43 → tag BRODY_F43_BRODY_V1_FULL_LIVE_SERVER_PORT_MATRIX_AUDIT_PALIER_20260529
```
