# Obsidia X-108 — Release Candidate Checklist (F40 RC1)

**Mode:** READONLY · KX108_ONLY · emits_act=false  
**Head:** 23ca559  
**Parent tag:** BRODY_F39_OPERATOR_DEMO_PACK_CONSOLIDATION_PALIER_20260529  
**Date:** 2026-05-29

---

## Pre-Demo Verification Checklist

### ☐ 1 — Repository state

```powershell
git status -sb          # must be clean (## main...origin/main, no changes)
git log --oneline -3    # HEAD must be 23ca559
git tag --list "BRODY_F3*" | Measure-Object -Line  # must be ≥11 lines
```

- [ ] `git status` is clean
- [ ] HEAD = `23ca559`
- [ ] All 10 tags F32→F39 present

---

### ☐ 2 — Baseline tests (must be 103/103)

```powershell
python -m pytest `
  tests\api\test_f38_multi_domain_live_api_route_readonly.py `
  tests\api\test_f37_multi_domain_user_scenarios_readonly.py `
  tests\api\test_f36_user_scenario_brody_workbench_controlled_response.py `
  tests\api\test_f35_1_operator_demo_workbench_surfaces.py `
  tests\api\test_f34_live_route_contract_readonly.py `
  tests\api\test_f33_brody_runtime_entrypoint_readonly.py `
  tests\api\test_f32_brody_full_runtime_integration_readonly_packet.py `
  tests\api\test_f29_1_neo4j_manual_write_surface_guard.py `
  -q
```

- [ ] Result = `103 passed`

---

### ☐ 3 — Server start

```powershell
# Check port availability
netstat -an | Select-String "8011.*LISTENING"   # should be empty

# Start server
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8011
```

- [ ] Port 8011 free (or choose another free port)
- [ ] Server starts without error
- [ ] `Uvicorn running on http://127.0.0.1:8011` visible in output

---

### ☐ 4 — Health check

```powershell
Invoke-WebRequest "http://127.0.0.1:8011/" -UseBasicParsing | Select-Object StatusCode
```

- [ ] HTTP 200

---

### ☐ 5 — OpenAPI routes verification

```powershell
$oas = (Invoke-WebRequest "http://127.0.0.1:8011/openapi.json" -UseBasicParsing).Content
@("f33/integration-packet", "f36/user-scenario", "f38/multi-domain-scenarios",
  "operator/runtime-panel", "demo/runtime-readiness", "workbench/runtime-connector") |
  ForEach-Object { Write-Host "$_=$($oas -match $_)" }
```

- [ ] `f33/integration-packet` = True
- [ ] `f36/user-scenario` = True
- [ ] `f38/multi-domain-scenarios` = True
- [ ] `operator/runtime-panel` = True
- [ ] `demo/runtime-readiness` = True
- [ ] `workbench/runtime-connector` = True

---

### ☐ 6 — F33 route (7 surfaces READY_READONLY)

```powershell
$body = '{"domain":"bank","sigma_payload":{"balance":10000}}'
(Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/brody-runtime/f33/integration-packet" `
  -Method POST -Body $body -ContentType "application/json" -UseBasicParsing).Content |
  ConvertFrom-Json |
  Select-Object integration_status, surfaces_ready, decision_authority, emits_act, kernel_mutation
```

- [ ] `integration_status` = `READY_READONLY`
- [ ] `surfaces_ready` = `7`
- [ ] `decision_authority` = `KX108_ONLY`
- [ ] `emits_act` = `False`
- [ ] `kernel_mutation` = `False`

---

### ☐ 7 — F36 user scenario (bank)

```powershell
$body = @{
  user_input = "Je veux analyser une transaction bancaire avant paiement."
  domain = "bank"
  sigma_payload = @{ balance = 10000.0 }
} | ConvertTo-Json
$resp = (Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/brody-runtime/f36/user-scenario" `
  -Method POST -Body $body -ContentType "application/json" -UseBasicParsing).Content | ConvertFrom-Json
$resp | Select-Object scenario_id, mode, decision_authority
$resp.controlled_response | Select-Object can_decide, can_execute, response_kind
```

- [ ] `scenario_id` = `F36_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE`
- [ ] `mode` = `READONLY`
- [ ] `can_decide` = `False`
- [ ] `can_execute` = `False`
- [ ] `response_kind` = `contextual_explanation_only`

---

### ☐ 8 — F38 multi-domain (4 scenarios)

```powershell
$resp = (Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/brody-runtime/f38/multi-domain-scenarios" `
  -Method POST -Body "{}" -ContentType "application/json" -UseBasicParsing).Content | ConvertFrom-Json
$resp | Select-Object packet_id, global_status, scenario_count, all_mutations_false, forbidden_tokens_found
$resp.scenarios | Select-Object domain, status, can_decide, surfaces_ready
```

- [ ] `packet_id` = `F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY`
- [ ] `global_status` = `READY_READONLY`
- [ ] `scenario_count` = `4`
- [ ] `all_mutations_false` = `True`
- [ ] `forbidden_tokens_found` = `False`
- [ ] bank → `READY_READONLY`, surfaces=7
- [ ] gps_defense_aviation → `READY_READONLY`, surfaces=7
- [ ] trading → `READY_READONLY`, surfaces=7
- [ ] unknown_refusal → `REFUSAL_READONLY`

---

### ☐ 9 — Operator panel (HTML)

```powershell
# Open in browser
Start-Process "http://127.0.0.1:8011/api/periphery/operator/runtime-panel.html"
```

- [ ] Page loads without error
- [ ] Shows `READY_READONLY` status
- [ ] Shows `KX108_ONLY` authority

---

### ☐ 10 — Smoke scripts (no server required for F34/F36/F37)

```powershell
python scripts\smoke_f37_multi_domain_user_scenarios_readonly.py
# Expected: F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY_STATUS=PASS · CHECKS=139/139
```

- [ ] F37 smoke = PASS 139/139

```powershell
# With server on 8011:
python scripts\smoke_f38_multi_domain_live_uvicorn_api.py
# Expected: F38_MULTI_DOMAIN_LIVE_UVICORN_API_SMOKE_STATUS=PASS · CHECKS=141/141
```

- [ ] F38 smoke = PASS 141/141 (requires live server)

---

### ☐ 11 — Boundary contract final check

For every response in the demo, verify:

| Check | Expected |
|-------|----------|
| `decision_authority` | `KX108_ONLY` |
| `allowed_to_decide` | `false` |
| `emits_act` | `false` |
| `emits_verdict` | `false` |
| `kernel_mutation` | `false` |
| `x108_mutation` | `false` |
| `neo4j_write` | `false` |
| `can_decide` | `false` |
| `can_execute` | `false` |

- [ ] All boundary flags confirmed

---

### ☐ 12 — Proof artifacts present

```powershell
# Live-server proofs (highest-confidence)
Test-Path "docs\runtime\F34B_LIVE_UVICORN_ROUTE_PROOF_20260529_044331.json"  # F34B REAL_BACKEND
Test-Path "docs\runtime\F36B_TRUE_LIVE_UVICORN_USER_SCENARIO_PROOF_20260529_034044.json"  # F36B LIVE_SERVER_8011
Test-Path "docs\runtime\F38_MULTI_DOMAIN_LIVE_UVICORN_PROOF_20260529_040328.json"  # F38 LIVE_SERVER_8011
```

- [ ] F34B proof present (SHA256: `20A27188...`, 562KB)
- [ ] F36B proof present (SHA256: `A6FD4BC2...`)
- [ ] F38 proof present (SHA256: `746621E5...`)

---

## Demo Narrative (for human audience)

1. **What we show:** Brody consults 7 runtime surfaces, builds advisory responses across 4 domains, exposes them via a live FastAPI server — without ever deciding, executing, or mutating.

2. **Key proof:** Every response carries `decision_authority=KX108_ONLY`, `emits_act=false`, `kernel_mutation=false`. These flags are enforced at module level, route level, and response level. TestClient and live uvicorn tests confirm consistency.

3. **The chain:** F32 (internal packet) → F33 (entrypoint) → F34/F34B (live proof) → F35 (operator surfaces) → F36/F36B (user scenario) → F37 (multi-domain) → F38 (multi-domain live) → F39 (consolidated pack).

4. **What KX108 retains:** All decisions. Brody only observes and reports. The boundary is not a configuration — it is enforced by immutable flags at every layer.

---

## RC1 Sign-off

| Item | Status |
|------|--------|
| All tags F32→F39 present | ✅ 10/10 |
| Baseline tests 103/103 | ✅ |
| Live server proofs (F34B, F36B, F38) | ✅ 3 proofs |
| Boundary KX108_ONLY at all layers | ✅ |
| No forbidden tokens in any response | ✅ |
| No mutation flags anywhere | ✅ |
| Operator demo guide present | ✅ `docs/demo/OBSIDIA_OPERATOR_DEMO_README_F39.md` |
| Release index present | ✅ `docs/runtime/OBSIDIA_F40_RELEASE_CANDIDATE_DEMO_FREEZE_INDEX_20260529_061923.json` |

**RC1 VERDICT: READY FOR DEMO / AUDIT**

---

*F40 RC1 · READONLY · KX108_ONLY · Generated 2026-05-29*
