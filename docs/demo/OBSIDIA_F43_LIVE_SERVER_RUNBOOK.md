# Brody GPT V1 — Live Server Runbook (F43)

**Canonical name:** `BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME`  
**Mode:** READONLY · KX108_ONLY · 127.0.0.1 ONLY  
**Date:** 2026-05-29

---

## Pre-flight: Port Check

Before starting the server, verify target ports are free:

```powershell
$ports = @(8011, 9010, 8000)
foreach ($p in $ports) {
  $hit = netstat -ano | Select-String ":$p\s.*LISTENING"
  Write-Host "$(if($hit){'OCCUPIED'}else{'FREE'})  $p"
}
```

**Preferred port order:** 8011 → 9010 → 8000  
**Never bind to 0.0.0.0 — always use 127.0.0.1**

---

## Start the Server

```powershell
cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8011
```

Wait for: `Uvicorn running on http://127.0.0.1:8011`

---

## Start as Background Process (with PID capture)

```powershell
$proc = Start-Process -FilePath "python" `
  -ArgumentList @("-m","uvicorn","apps.obsidia_api.main:app","--host","127.0.0.1","--port","8011") `
  -PassThru -WindowStyle Hidden

Write-Host "PID=$($proc.Id)"

# Poll ready
for ($i = 0; $i -lt 15; $i++) {
  Start-Sleep -Seconds 2
  try {
    $r = Invoke-WebRequest "http://127.0.0.1:8011/" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    if ($r.StatusCode -eq 200) { Write-Host "READY after $($i+1) polls"; break }
  } catch {}
}
```

---

## Health Check

```powershell
Invoke-WebRequest "http://127.0.0.1:8011/" -UseBasicParsing | Select-Object StatusCode
# Expected: 200
```

---

## OpenAPI Route Verification

```powershell
$oas = (Invoke-WebRequest "http://127.0.0.1:8011/openapi.json" -UseBasicParsing).Content
@("f33/integration-packet","f36/user-scenario","f38/multi-domain-scenarios",
  "operator/runtime-panel","demo/runtime-readiness","workbench/runtime-connector") |
  ForEach-Object { Write-Host "$_=$($oas -match $_)" }
# All should be True
```

---

## Route Tests

### F33 — 7-Surface Integration Packet

```powershell
$body = '{"domain":"bank","sigma_payload":{"request_type":"STRUCTURAL_PREPARATION","amount":100},"title":"Live check","session_id":"runbook-f33","signal_id":"runbook-tree","theta":0.15,"request_type":"STRUCTURAL_PREPARATION"}'
(Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/brody-runtime/f33/integration-packet" `
  -Method POST -Body $body -ContentType "application/json" -UseBasicParsing).Content |
  ConvertFrom-Json | Select-Object integration_status, surfaces_ready, decision_authority, emits_act, kernel_mutation
```

Expected: `integration_status=READY_READONLY`, `surfaces_ready=7`, `decision_authority=KX108_ONLY`, `emits_act=False`, `kernel_mutation=False`

---

### Operator Panel (JSON)

```powershell
(Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/operator/runtime-panel" -UseBasicParsing).StatusCode
# Expected: 200
```

### Operator Panel (HTML — open in browser)

```powershell
Start-Process "http://127.0.0.1:8011/api/periphery/operator/runtime-panel.html"
```

### Runtime Readiness

```powershell
(Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/demo/runtime-readiness" -UseBasicParsing).StatusCode
# Expected: 200
```

### Workbench Connector

```powershell
(Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/workbench/runtime-connector" -UseBasicParsing).StatusCode
# Expected: 200
```

---

### F36 — User Scenario (bank)

```powershell
$body = @{
  user_input = "Je veux analyser une transaction bancaire avant paiement."
  domain = "bank"
  session_id = "runbook-f36"
  signal_id = "runbook-f36-tree"
  theta = 0.15
  request_type = "STRUCTURAL_PREPARATION"
} | ConvertTo-Json
$resp = (Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/brody-runtime/f36/user-scenario" `
  -Method POST -Body $body -ContentType "application/json" -UseBasicParsing).Content | ConvertFrom-Json
$resp | Select-Object scenario_id, mode, decision_authority
$resp.controlled_response | Select-Object can_decide, can_execute, response_kind
```

Expected: `mode=READONLY`, `can_decide=False`, `response_kind=contextual_explanation_only`

---

### F38 — Multi-Domain Scenarios (4 domains)

```powershell
$resp = (Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/brody-runtime/f38/multi-domain-scenarios" `
  -Method POST -Body '{"theta":0.15,"request_type":"STRUCTURAL_PREPARATION"}' `
  -ContentType "application/json" -UseBasicParsing).Content | ConvertFrom-Json
$resp | Select-Object packet_id, global_status, scenario_count, all_mutations_false, forbidden_tokens_found
$resp.scenarios | Select-Object domain, status, can_decide, surfaces_ready
```

Expected: `global_status=READY_READONLY`, `all_mutations_false=True`, `forbidden_tokens_found=False`  
Domains: bank/gps_defense_aviation/trading → `READY_READONLY`, unknown_refusal → `REFUSAL_READONLY`

---

## Smoke Scripts

### No server required

```powershell
# F37 — direct module call (fastest, 139 checks)
python scripts\smoke_f37_multi_domain_user_scenarios_readonly.py
# F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY_STATUS=PASS · CHECKS=139/139

# F34 — TestClient (73 checks)
python scripts\smoke_f34_live_route_contract_readonly.py
# STATUS=PASS · CHECKS=73/73

# F36 — TestClient (60 checks)
python scripts\smoke_f36_user_scenario_controlled_response.py
# STATUS=PASS · CHECKS=60/60
```

### Requires live server on 8011

```powershell
# F36B — live uvicorn user scenario (61 checks)
python scripts\smoke_f36b_true_live_uvicorn_user_scenario.py
# F36B_TRUE_LIVE_UVICORN_USER_SCENARIO_SMOKE_STATUS=PASS · CHECKS=61/61

# F38 — live uvicorn multi-domain (141 checks)
python scripts\smoke_f38_multi_domain_live_uvicorn_api.py
# F38_MULTI_DOMAIN_LIVE_UVICORN_API_SMOKE_STATUS=PASS · CHECKS=141/141
```

**Total smoke checks: 474/474**

---

## Baseline Tests

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
# Expected: 103 passed
```

---

## Stop the Background Server

```powershell
# If you have the $proc variable:
Stop-Process -Id $proc.Id -Force

# If you lost the PID, find it:
netstat -ano | Select-String ":8011.*LISTENING"
# Then: Stop-Process -Id <PID> -Force
```

---

## Post-Stop Verification

```powershell
git diff --check   # must be clean
git status -sb     # must show ## main...origin/main
```

---

## Boundary Contract (All Routes)

Every Brody V1 response must carry:

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

Forbidden tokens: `ALLOW · HOLD · BLOCK · ACT · DECIDE · VERDICT`  
Check: word-boundary regex `\bTOKEN\b` applied to `controlled_response.text` and `response`/`response_text` fields (F47 hardening). KERNEL_TRACE stderr tokens (ALLOW, VERDICT, GATE, BLOCK) are internal computation results from sigma/evaluate — they are NOT Brody API response emissions and are excluded from this scan.

---

*F43 Live Server Runbook · READONLY · KX108_ONLY · Generated 2026-05-29*
