# Brody GPT V1 — Demo Commands

**Canonical name:** `BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME`  
**Mode:** READONLY · KX108_ONLY  
**Date:** 2026-05-29

All commands run from:
```
C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B
```

---

## 1 — Git State Check

```powershell
git status -sb
git log --oneline -5
git tag --points-at HEAD
```

Expected:
- Status: clean
- HEAD: `378867f` (F48 audit) or later
- Tag: `BRODY_F48_POST_HARDENING_VERIFICATION_RELEASE_READINESS_CHECK_PALIER_20260529`

---

## 2 — Baseline Tests (103/103)

```powershell
$env:PYTHONIOENCODING = "utf-8"
python -m pytest tests\api\ -q --tb=no
```

Expected: `103 passed`

Or targeted:
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
  -q --tb=no
```

Expected: `103 passed`  
Known allowed: Windows `PermissionError` on temp symlink cleanup — not a test failure.

---

## 3 — F47 Sovereignty Enforcement (13/13)

```powershell
$env:PYTHONIOENCODING = "utf-8"
python scripts\_f47_test_sovereignty.py 2>$null
```

Expected:
```
F47_1_PROTECTED_RESPONSE_ENVELOPE=PASS
```

Verifies: `decision_authority=KX108_ONLY` cannot be overridden by any module output.  
All 13 sovereignty flags blocked when injected.

---

## 4 — F47 Forbidden Token Sanitizer (42/42)

```powershell
$env:PYTHONIOENCODING = "utf-8"
python scripts\_f47_test_sanitizer.py 2>$null
```

Expected:
```
F47_2_CONTROLLED_RESPONSE_SANITIZER=PASS
```

Verifies: `ALLOW / HOLD / BLOCK / ACT / DECIDE / VERDICT` are redacted via word-boundary regex in all user-facing text.  
Zero false positives on trap words (`transaction`, `interaction`, `artifact`, `ACTOR`, `BLOCK_CHAIN`).

---

## 5 — F47 Nested Scan Scope (9/9)

```powershell
$env:PYTHONIOENCODING = "utf-8"
python scripts\_f47_test_nested_scan.py 2>$null
```

Expected:
```
F47_3_NESTED_SCAN_SCOPE=PASS
```

Verifies: F37 multi-domain packet clean, internal proof fields preserved, nested `controlled_response.text` sanitized.

---

## 6 — Smoke Scripts (no server required)

```powershell
$env:PYTHONIOENCODING = "utf-8"

# F37 — multi-domain direct call (139 checks)
python scripts\smoke_f37_multi_domain_user_scenarios_readonly.py
# Expected: F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY_STATUS=PASS · CHECKS=139/139

# F34 — TestClient route contract (73 checks)
python scripts\smoke_f34_live_route_contract_readonly.py
# Expected: STATUS=PASS · CHECKS=73/73

# F36 — TestClient user scenario (60 checks)
python scripts\smoke_f36_user_scenario_controlled_response.py
# Expected: STATUS=PASS · CHECKS=60/60
```

---

## 7 — Live Server (requires uvicorn)

### Start server

```powershell
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8011
```

Wait for: `Uvicorn running on http://127.0.0.1:8011`

### Health check

```powershell
Invoke-WebRequest "http://127.0.0.1:8011/" -UseBasicParsing | Select-Object StatusCode
# Expected: 200
```

### F33 — 7-surface integration packet

```powershell
$body = '{"domain":"bank","sigma_payload":{"request_type":"STRUCTURAL_PREPARATION","amount":100},"title":"Demo","session_id":"demo-f33","signal_id":"demo-tree","theta":0.15,"request_type":"STRUCTURAL_PREPARATION"}'
(Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/brody-runtime/f33/integration-packet" `
  -Method POST -Body $body -ContentType "application/json" -UseBasicParsing).Content |
  ConvertFrom-Json |
  Select-Object integration_status, surfaces_ready, decision_authority, emits_act, kernel_mutation
```

Expected: `integration_status=READY_READONLY · surfaces_ready=7 (nominal) · decision_authority=KX108_ONLY · emits_act=False · kernel_mutation=False`

### F36 — User scenario (bank domain)

```powershell
$body = @{
  user_input = "Je veux analyser une transaction bancaire avant paiement."
  domain = "bank"
  session_id = "demo-f36"
  signal_id = "demo-f36-tree"
  theta = 0.15
  request_type = "STRUCTURAL_PREPARATION"
} | ConvertTo-Json
$resp = (Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/brody-runtime/f36/user-scenario" `
  -Method POST -Body $body -ContentType "application/json" -UseBasicParsing).Content | ConvertFrom-Json
$resp | Select-Object scenario_id, mode, decision_authority
$resp.controlled_response | Select-Object can_decide, can_execute, response_kind
```

Expected: `mode=READONLY · can_decide=False · response_kind=contextual_explanation_only`

### F38 — Multi-domain packet (4 domains)

```powershell
$resp = (Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/brody-runtime/f38/multi-domain-scenarios" `
  -Method POST -Body '{"theta":0.15,"request_type":"STRUCTURAL_PREPARATION"}' `
  -ContentType "application/json" -UseBasicParsing).Content | ConvertFrom-Json
$resp | Select-Object packet_id, global_status, scenario_count, all_mutations_false, forbidden_tokens_found
$resp.scenarios | Select-Object domain, status, can_decide, surfaces_ready
```

Expected:
- `global_status=READY_READONLY`
- `all_mutations_false=True`
- `forbidden_tokens_found=False`
- bank / gps_defense_aviation / trading → `READY_READONLY`
- unknown_refusal → `REFUSAL_READONLY`

### Live server smoke (141 checks)

```powershell
python scripts\smoke_f38_multi_domain_live_uvicorn_api.py
# Expected: F38_MULTI_DOMAIN_LIVE_UVICORN_API_SMOKE_STATUS=PASS · CHECKS=141/141
```

### Operator panel (browser)

```powershell
Start-Process "http://127.0.0.1:8011/api/periphery/operator/runtime-panel.html"
```

---

## 8 — Boundary Contract Verification

Every response from every route must contain:

```powershell
# Example: check F33 response boundary
$r = (Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/brody-runtime/f33/integration-packet" `
  -Method POST -Body '{}' -ContentType "application/json" -UseBasicParsing).Content | ConvertFrom-Json
@("decision_authority","allowed_to_decide","emits_act","emits_verdict","kernel_mutation","x108_mutation","neo4j_write","brody_decision") |
  ForEach-Object { Write-Host "$_=$($r.$_)" }
```

Expected:
```
decision_authority=KX108_ONLY
allowed_to_decide=False
emits_act=False
emits_verdict=False
kernel_mutation=False
x108_mutation=False
neo4j_write=False
brody_decision=False
```

---

## Total Smoke Check Summary

| Script | Mode | Checks |
|--------|------|--------|
| `smoke_f34_live_route_contract_readonly.py` | TestClient | 73 |
| `smoke_f36_user_scenario_controlled_response.py` | TestClient | 60 |
| `smoke_f37_multi_domain_user_scenarios_readonly.py` | DirectCall | 139 |
| `smoke_f36b_true_live_uvicorn_user_scenario.py` | Live server | 61 |
| `smoke_f38_multi_domain_live_uvicorn_api.py` | Live server | 141 |
| **Total** | | **474** |

---

*Brody GPT V1 · Demo Commands · READONLY · KX108_ONLY · 2026-05-29*
