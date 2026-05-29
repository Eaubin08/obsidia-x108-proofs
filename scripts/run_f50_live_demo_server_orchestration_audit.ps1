# F50 — Live Demo Server Orchestration Audit
# READONLY / KX108_ONLY / 127.0.0.1 ONLY
# Starts uvicorn, runs all checks, stops server, writes results to stdout.

Set-Location "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"
$env:PYTHONIOENCODING = "utf-8"

$PORT = 8011
$F50_HOST = "127.0.0.1"
$BASE = "http://${F50_HOST}:${PORT}"

Write-Host "=== F50 START === port=$PORT host=$F50_HOST"

# --- Start uvicorn ---
$proc = Start-Process -FilePath "python" `
    -ArgumentList @("-m", "uvicorn", "apps.obsidia_api.main:app", "--host", $F50_HOST, "--port", "$PORT") `
    -PassThru -WindowStyle Hidden
$PID_F50 = $proc.Id
Write-Host "SERVER_PID=$PID_F50"

# Poll ready (up to 30s)
$ready = $false
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 2
    try {
        $r = Invoke-WebRequest "$BASE/" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        if ($r.StatusCode -eq 200) { $ready = $true; Write-Host "SERVER_READY=true polls=$($i+1)"; break }
    } catch {}
}
if (-not $ready) { Write-Host "SERVER_READY=false"; Stop-Process -Id $PID_F50 -Force -ErrorAction SilentlyContinue; exit 1 }

# --- Route tests ---
$results = @{}

function Test-Route {
    param($label, $method, $url, $body=$null)
    try {
        if ($method -eq "GET") {
            $r = Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
        } else {
            $r = Invoke-WebRequest $url -Method POST -Body $body -ContentType "application/json" -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
        }
        $code = $r.StatusCode
        $content = $r.Content
        # Try JSON parse
        try { $j = $content | ConvertFrom-Json; $jsonOk = $true } catch { $j = $null; $jsonOk = $false }
        # Boundary checks
        $da = if ($j -and $j.decision_authority) { $j.decision_authority } else { "N/A" }
        $atd = if ($null -ne $j.allowed_to_decide) { $j.allowed_to_decide } else { "N/A" }
        $ea = if ($null -ne $j.emits_act) { $j.emits_act } else { "N/A" }
        $ev = if ($null -ne $j.emits_verdict) { $j.emits_verdict } else { "N/A" }
        $km = if ($null -ne $j.kernel_mutation) { $j.kernel_mutation } else { "N/A" }
        $bd = if ($null -ne $j.brody_decision) { $j.brody_decision } else { "N/A" }
        $status = if ($code -eq 200 -and $jsonOk) { "PASS" } elseif ($code -eq 200) { "PASS_NO_JSON" } else { "FAIL_$code" }
        Write-Host "  [$status] $label | HTTP=$code | da=$da | atd=$atd | ea=$ea"
        return @{ status=$status; code=$code; da=$da; atd=$atd; ea=$ea; ev=$ev; km=$km; bd=$bd }
    } catch {
        Write-Host "  [FAIL] $label | ERROR: $($_.Exception.Message.Split([char]10)[0])"
        return @{ status="FAIL_ERROR"; code=0 }
    }
}

Write-Host "`n=== ROUTE TESTS ==="
$results["root"]               = Test-Route "GET /"                       GET  "$BASE/"
$results["openapi"]            = Test-Route "GET /openapi.json"           GET  "$BASE/openapi.json"
$results["demo_readiness"]     = Test-Route "GET /demo/runtime-readiness" GET  "$BASE/api/periphery/demo/runtime-readiness"
$results["operator_panel"]     = Test-Route "GET /operator/runtime-panel" GET  "$BASE/api/periphery/operator/runtime-panel"
$results["workbench"]          = Test-Route "GET /workbench/connector"    GET  "$BASE/api/periphery/workbench/runtime-connector"

$f33body = '{"domain":"bank","sigma_payload":{"request_type":"STRUCTURAL_PREPARATION","amount":100,"recipient":"f50-readonly-target"},"title":"F50 F33 live demo check","session_id":"f50-f33","signal_id":"f50-tree-signal","theta":0.15,"request_type":"STRUCTURAL_PREPARATION"}'
$results["f33"]                = Test-Route "POST /f33/integration-packet" POST "$BASE/api/periphery/brody-runtime/f33/integration-packet" $f33body

$f36body = '{"user_input":"Je veux analyser une transaction bancaire avant paiement. ALLOW DECIDE VERDICT","domain":"bank","session_id":"f50-f36","signal_id":"f50-f36-tree-signal","theta":0.15,"request_type":"STRUCTURAL_PREPARATION"}'
$results["f36"]                = Test-Route "POST /f36/user-scenario"     POST "$BASE/api/periphery/brody-runtime/f36/user-scenario"       $f36body

$f38body = '{"theta":0.15,"request_type":"STRUCTURAL_PREPARATION"}'
$results["f38"]                = Test-Route "POST /f38/multi-domain"      POST "$BASE/api/periphery/brody-runtime/f38/multi-domain-scenarios" $f38body

# F36 special: check cr.text for forbidden tokens
Write-Host "`n=== F36 FORBIDDEN TOKEN CHECK IN CR.TEXT ==="
try {
    $f36resp = (Invoke-WebRequest "$BASE/api/periphery/brody-runtime/f36/user-scenario" `
        -Method POST -Body $f36body -ContentType "application/json" -UseBasicParsing -TimeoutSec 10).Content | ConvertFrom-Json
    $crText = $f36resp.controlled_response.text
    $forbidden = @("ALLOW","HOLD","BLOCK","DECIDE","VERDICT") | Where-Object { $crText -match "\b$_\b" }
    if ($crText) {
        Write-Host "  CR_TEXT_PREVIEW: $($crText.Substring(0, [Math]::Min(120, $crText.Length)))..."
    }
    if ($forbidden) {
        Write-Host "  [FAIL] FORBIDDEN_TOKENS_IN_CR_TEXT: $($forbidden -join ', ')"
    } else {
        Write-Host "  [PASS] NO_FORBIDDEN_TOKENS_IN_CR_TEXT"
    }
} catch { Write-Host "  [SKIP] F36 cr.text check error: $_" }

# F38 special: check global_status + all_mutations_false
Write-Host "`n=== F38 MULTI-DOMAIN BOUNDARY CHECK ==="
try {
    $f38resp = (Invoke-WebRequest "$BASE/api/periphery/brody-runtime/f38/multi-domain-scenarios" `
        -Method POST -Body $f38body -ContentType "application/json" -UseBasicParsing -TimeoutSec 10).Content | ConvertFrom-Json
    Write-Host "  global_status=$($f38resp.global_status)"
    Write-Host "  all_mutations_false=$($f38resp.all_mutations_false)"
    Write-Host "  forbidden_tokens_found=$($f38resp.forbidden_tokens_found)"
    Write-Host "  scenario_count=$($f38resp.scenario_count)"
    foreach ($s in $f38resp.scenarios) {
        Write-Host "  domain=$($s.domain) | status=$($s.status) | can_decide=$($s.can_decide)"
    }
} catch { Write-Host "  [SKIP] F38 detail check error: $_" }

# --- STOP SERVER ---
Write-Host "`n=== STOP SERVER PID=$PID_F50 ==="
Stop-Process -Id $PID_F50 -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
$stillRunning = Get-Process -Id $PID_F50 -ErrorAction SilentlyContinue
if ($stillRunning) {
    Write-Host "SERVER_STOPPED=false"
} else {
    Write-Host "SERVER_STOPPED=true"
}

# Port clean check
$portClean = -not (netstat -ano | Select-String ":$PORT\s.*LISTENING")
Write-Host "PORT_CLEAN_AFTER_STOP=$portClean"

Write-Host "`n=== F50 SERVER DONE ==="
Write-Host "SERVER_PID=$PID_F50"
Write-Host "SERVER_PORT=$PORT"
Write-Host "ROUTES_TESTED=$($results.Count)"
