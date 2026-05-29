# Brody GPT V1 — Final README

**Canonical name:** `BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME`  
**Version:** V1.0.0-RC-CLOSED  
**Status:** V1_CLOSED · AUDIT_READY  
**Sealed at:** F42 · HEAD b67b2c3 · 2026-05-29

---

## What is Brody GPT V1?

Brody GPT V1 is a read-only advisory runtime component. It consults 7 runtime surfaces of the Obsidia X-108 governance system, aggregates their state, and produces context-only advisory responses across 4 domains (bank, gps_defense_aviation, trading, unknown_refusal).

**Brody does not decide. KX108_ONLY is the decision authority.**

This constraint is enforced at three independent layers simultaneously:
1. Module level — every function returns a 15-flag `BOUNDARY` dict
2. Route level — every FastAPI endpoint wraps output through `safe_backend_response()`
3. Response level — word-boundary regex scan verifies absence of forbidden tokens in all generated text

---

## Quick Start

**Start the server:**

```powershell
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8011
```

**Health check:**

```powershell
Invoke-WebRequest "http://127.0.0.1:8011/" -UseBasicParsing | Select-Object StatusCode
# Expected: 200
```

**Multi-domain advisory packet (4 domains):**

```powershell
$resp = (Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/brody-runtime/f38/multi-domain-scenarios" `
  -Method POST -Body "{}" -ContentType "application/json" -UseBasicParsing).Content | ConvertFrom-Json
$resp | Select-Object packet_id, global_status, scenario_count, all_mutations_false, forbidden_tokens_found
$resp.scenarios | Select-Object domain, status, can_decide, surfaces_ready
```

**Single domain (bank):**

```powershell
$body = @{ user_input = "Analyser une transaction bancaire."; domain = "bank"; sigma_payload = @{ balance = 10000 } } | ConvertTo-Json
(Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/brody-runtime/f36/user-scenario" `
  -Method POST -Body $body -ContentType "application/json" -UseBasicParsing).Content | ConvertFrom-Json |
  Select-Object scenario_id, mode, decision_authority
```

**Operator panel (browser):**

```powershell
Start-Process "http://127.0.0.1:8011/api/periphery/operator/runtime-panel.html"
```

---

## API Routes (7 — all READY_READONLY)

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/periphery/brody-runtime/f33/integration-packet` | 7-surface runtime integration packet |
| `GET`  | `/api/periphery/operator/runtime-panel` | Operator panel (JSON) |
| `GET`  | `/api/periphery/operator/runtime-panel.html` | Operator panel (HTML) |
| `GET`  | `/api/periphery/demo/runtime-readiness` | Runtime readiness status |
| `GET`  | `/api/periphery/workbench/runtime-connector` | Workbench connector |
| `POST` | `/api/periphery/brody-runtime/f36/user-scenario` | End-to-end user scenario |
| `POST` | `/api/periphery/brody-runtime/f38/multi-domain-scenarios` | Multi-domain 4-scenario packet |

---

## Runtime Surfaces (7)

| Surface | Role |
|---------|------|
| `sigma_dispatcher` | Context signal dispatch |
| `tree_signal_packet` | Arboreal signal packet |
| `monitoring_adapters` | Monitoring adapter aggregation |
| `operator_view_packet` | Synthetic operator view |
| `brody_runtime_context` | Brody runtime context |
| `workflow_governance_readonly` | Workflow governance (read-only) |
| `neo4j_guide_bridge` | Neo4j guidance bridge (read-only) |

---

## Domains (4)

| Domain | Status | Surfaces |
|--------|--------|----------|
| `bank` | READY_READONLY | 7 |
| `gps_defense_aviation` | READY_READONLY | 7 |
| `trading` | READY_READONLY | 7 |
| `unknown_refusal` | REFUSAL_READONLY | — |

---

## Boundary Contract

Every response from every route carries this contract — verifiable in real time:

| Flag | Value |
|------|-------|
| `decision_authority` | `KX108_ONLY` |
| `allowed_to_decide` | `false` |
| `can_decide` | `false` |
| `emits_act` | `false` |
| `emits_verdict` | `false` |
| `kernel_mutation` | `false` |
| `x108_mutation` | `false` |
| `neo4j_write` | `false` |
| `memory_write` | `false` |
| `brody_decision` | `false` |

**Forbidden response tokens:** `ALLOW · HOLD · BLOCK · ACT · DECIDE · VERDICT`  
**Check method:** word-boundary regex `\bTOKEN\b` — verified on every output.

---

## Proof Chain (F32→F41)

| Metric | Value |
|--------|-------|
| Git tags (F24→F41) | 14/14 |
| Unit tests | 103/103 PASS |
| Smoke checks (cumulative) | 474 |
| Live-server proofs | 3 (F34B/F36B/F38) |
| Runtime reports | 15 |

---

## Run Tests

```powershell
python -m pytest tests\api\ -q
# Expected: 103 passed
```

---

## Run Smoke Scripts

```powershell
# No server required:
python scripts\smoke_f37_multi_domain_user_scenarios_readonly.py
# PASS · CHECKS=139/139

# Requires live server on 8011:
python scripts\smoke_f38_multi_domain_live_uvicorn_api.py
# PASS · CHECKS=141/141
```

---

## What Brody V1 Is Not

- **Not a decision engine** — `KX108_ONLY` decides
- **Not formally Lean-proven** — runtime smoke + unit tests only
- **Not production-hardened** — no adversarial testing, no load testing
- **Not connected to live KX108 kernel** — kernel is the declared authority, not the instantiated one
- **Not a memory system** — `memory_write=false`, `graphiti_write=false`

---

## Verification (independent)

Anyone can verify V1 from the repository:

```powershell
git checkout b67b2c3          # HEAD at V1 seal
python -m pytest tests\api\ -q
# 103 passed
```

SHA256 of live-server proofs are in:  
`docs/runtime/OBSIDIA_F40_RELEASE_CANDIDATE_DEMO_FREEZE_INDEX_20260529_061923.json`

---

*Brody GPT V1 · READONLY · KX108_ONLY · Sealed 2026-05-29*
