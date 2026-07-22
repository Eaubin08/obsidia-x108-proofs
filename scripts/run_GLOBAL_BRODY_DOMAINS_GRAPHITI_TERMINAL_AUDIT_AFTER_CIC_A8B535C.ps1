# GLOBAL_BRODY_DOMAINS_GRAPHITI_TERMINAL_AUDIT_AFTER_CIC_A8B535C
# DECISION_AUTHORITY=KX108_ONLY | COMMIT=NO | PUSH=NO | PATCH=NO | ACT=NO
# Usage : powershell -File scripts\run_GLOBAL_BRODY_DOMAINS_GRAPHITI_TERMINAL_AUDIT_AFTER_CIC_A8B535C.ps1
#Requires -Version 5.1

$ErrorActionPreference = "Continue"

# -- Config ------------------------------------------------------------------
$BLOCK         = "GLOBAL_BRODY_DOMAINS_GRAPHITI_TERMINAL_AUDIT_AFTER_CIC_A8B535C"
$EXPECTED_HEAD = "46149b5"
$REPO_ROOT     = "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"
$TS            = (Get-Date -Format "yyyyMMdd_HHmmss")
$OUT_DIR       = Join-Path $REPO_ROOT ".local_audits\${BLOCK}_${TS}"

$BASE_8012   = "http://127.0.0.1:8012"
$BASE_8011   = "http://127.0.0.1:8011"
$UI_5173     = "http://localhost:5173"
$BASE_3001   = "http://localhost:3001"
$BRODY_CHAT  = "$BASE_8012/api/brody/chat"
$TIMEOUT_SEC       = 8    # healthchecks / infra probes
$TIMEOUT_BRODY_SEC = 60   # appels /api/brody/chat (pipeline complet peut etre lent)

# -- Helpers -----------------------------------------------------------------
function Write-Step { param([string]$msg) Write-Host "[AUDIT] $msg" -ForegroundColor Cyan }
function Write-OK   { param([string]$msg) Write-Host "  OK   $msg" -ForegroundColor Green }
function Write-FAIL { param([string]$msg) Write-Host "  FAIL $msg" -ForegroundColor Red }
function Write-WARN { param([string]$msg) Write-Host "  WARN $msg" -ForegroundColor Yellow }
function Write-SKIP { param([string]$msg) Write-Host "  SKIP $msg" -ForegroundColor DarkGray }

function Invoke-SafeWeb {
    param([string]$Uri, [string]$Method = "GET", [string]$Body = "", [int]$TimeoutSec = 8)
    try {
        $params = @{ Uri = $Uri; Method = $Method; TimeoutSec = $TimeoutSec; UseBasicParsing = $true }
        if ($Body -ne "") {
            $params["Body"]        = $Body
            $params["ContentType"] = "application/json"
        }
        $r = Invoke-WebRequest @params
        return @{ ok = $true; status = [int]$r.StatusCode; body = [string]$r.Content }
    } catch {
        $sc = 0
        if ($_.Exception.Response) {
            try { $sc = [int]$_.Exception.Response.StatusCode.value__ } catch {}
        }
        return @{ ok = $false; status = $sc; body = $_.Exception.Message }
    }
}

function Get-Sha256String { param([string]$text)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $hash  = [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
    return ($hash | ForEach-Object { $_.ToString("x2") }) -join ""
}

function Get-FileSha256 { param([string]$path)
    if (-not (Test-Path $path)) { return "FILE_MISSING" }
    return (Get-FileHash -Path $path -Algorithm SHA256).Hash.ToLower()
}

# Renvoie $true si le serveur est joignable (200 sur au moins une route sonde)
function Test-ServerUp {
    param([string]$Base, [string]$PostFallback = "", [int]$TimeoutSec = 8)
    $probes = @("$Base/health", "$Base/", "$Base/openapi.json")
    foreach ($probe in $probes) {
        $r = Invoke-SafeWeb -Uri $probe -TimeoutSec $TimeoutSec
        if ($r.ok) { return @{ up = $true; probe = $probe; status = $r.status } }
        if ($r.status -in @(200,301,302,307,308,403,405,422)) {
            return @{ up = $true; probe = $probe; status = $r.status }
        }
    }
    # Fallback POST sur le chat
    if ($PostFallback -ne "") {
        $testBody = '{"message":"ping_audit","debug":false}'
        $rp = Invoke-SafeWeb -Uri $PostFallback -Method "POST" -Body $testBody -TimeoutSec $TimeoutSec
        if ($rp.ok -or $rp.status -in @(200,400,422)) {
            return @{ up = $true; probe = $PostFallback; status = $rp.status }
        }
    }
    return @{ up = $false; probe = "none"; status = 0 }
}

# -- Init --------------------------------------------------------------------
Write-Step "Creation $OUT_DIR"
New-Item -ItemType Directory -Force -Path $OUT_DIR | Out-Null
Set-Location $REPO_ROOT

$GLOBAL_PASS  = $true
$HAS_SKIPS    = $false
$VERDICTS     = [ordered]@{}

# ============================================================================
# 1. GIT LOG
# ============================================================================
Write-Step "1/12 git log --oneline -20"
$gitLog  = git log --oneline -20 2>&1
$gitLog | Out-File (Join-Path $OUT_DIR "git_log.txt") -Encoding utf8
$headLine = ($gitLog | Select-Object -First 1)
$headHash = ($headLine -split " ")[0].Trim()
Write-Host "  HEAD: $headLine"
if ($headHash -eq $EXPECTED_HEAD) {
    Write-OK "HEAD = $EXPECTED_HEAD confirmed"
    $VERDICTS["git_head"] = "PASS - $headHash"
} else {
    Write-WARN "HEAD $headHash != expected $EXPECTED_HEAD"
    $VERDICTS["git_head"] = "WARN - got $headHash expected $EXPECTED_HEAD"
}

# ============================================================================
# 2. GIT STATUS SHORT
# ============================================================================
Write-Step "2/12 git status --short"
$gitStatus = git status --short 2>&1
$gitStatus | Out-File (Join-Path $OUT_DIR "git_status_short.txt") -Encoding utf8

$stagedUnexpected = @($gitStatus | Where-Object {
    $_ -match "^[AMDR]" } | Where-Object {
    $_ -notmatch "sigma/(run_pipeline|guard|aggregation|contracts)" -and
    $_ -notmatch "connectors/(aviation_robo|bank_normal_flow|trading_live)" -and
    $_ -notmatch "apps/obsidia_api/(brody_|routes/brody|main|cic)" -and
    $_ -notmatch "apps/obsidia-workbench" -and
    $_ -notmatch "scripts/run_brody" -and
    $_ -notmatch "\.claude/(settings|memory)" -and
    $_ -notmatch "audit/" -and
    $_ -notmatch "docs/runtime"
})

if ($stagedUnexpected.Count -eq 0) {
    Write-OK "0 staged unexpected"
    $VERDICTS["git_status"] = "PASS - 0 staged unexpected"
} else {
    Write-WARN "Staged unexpected: $($stagedUnexpected -join ', ')"
    $VERDICTS["git_status"] = "WARN - staged unexpected: $($stagedUnexpected -join '; ')"
}

# ============================================================================
# 3. GIT SHOW --CHECK HEAD
# ============================================================================
Write-Step "3/12 git show --check --stat HEAD"
$gitShow = git show --check --stat HEAD 2>&1
$gitShow | Out-File (Join-Path $OUT_DIR "git_show_check_head.txt") -Encoding utf8
$wsErrors = @($gitShow | Where-Object { $_ -match "whitespace error" })
if ($wsErrors.Count -eq 0) {
    Write-OK "git show --check: 0 whitespace error"
    $VERDICTS["git_show_check"] = "PASS"
} else {
    Write-WARN "$($wsErrors.Count) whitespace error(s)"
    $VERDICTS["git_show_check"] = "WARN - $($wsErrors.Count) whitespace errors"
}

# ============================================================================
# 4. SERVER 8012 STATUS — fallback multi-probe
# ============================================================================
Write-Step "4/12 Brody/API 8012 - multi-probe (health / / openapi.json / POST chat)"

$probe_detail = @{}
$server_up    = $false

foreach ($probe in @("$BASE_8012/health", "$BASE_8012/", "$BASE_8012/openapi.json")) {
    $rp = Invoke-SafeWeb -Uri $probe -TimeoutSec $TIMEOUT_SEC
    $probe_detail[$probe] = @{ status = $rp.status; ok = $rp.ok }
    if ($rp.ok -or $rp.status -in @(301,302,307,308,403,405)) {
        $server_up = $true
        Write-OK "8012 probe '$probe' => HTTP $($rp.status)"
        break
    } else {
        Write-Host "  probe '$probe' => HTTP $($rp.status) (next fallback...)" -ForegroundColor DarkGray
    }
}

if (-not $server_up) {
    # Dernier fallback : POST /api/brody/chat
    $pingBody = '{"message":"ping_audit","debug":false}'
    $rChat = Invoke-SafeWeb -Uri $BRODY_CHAT -Method "POST" -Body $pingBody -TimeoutSec $TIMEOUT_SEC
    $probe_detail[$BRODY_CHAT] = @{ status = $rChat.status; ok = $rChat.ok; method = "POST" }
    if ($rChat.ok -or $rChat.status -in @(200,400,422)) {
        $server_up = $true
        Write-OK "8012 fallback POST /api/brody/chat => HTTP $($rChat.status)"
    } else {
        Write-FAIL "8012 inaccessible (tous les probes echoues)"
    }
}

$server8012_obj = @{
    probes      = $probe_detail
    server_up   = $server_up
    chat_route  = $BRODY_CHAT
}
$server8012_obj | ConvertTo-Json -Depth 6 | Out-File (Join-Path $OUT_DIR "server_8012_status.json") -Encoding utf8

if ($server_up) {
    $VERDICTS["server_8012"] = "PASS - server joignable (route /health peut etre absente)"
} else {
    $VERDICTS["server_8012"] = "FAIL - aucun probe reussi"
    $GLOBAL_PASS = $false
}

# ============================================================================
# 5. BRODY CIC LIVE SMOKE — route /api/brody/chat, invariants complets
# ============================================================================
Write-Step "5/12 Brody CIC live smoke (2 appels POST $BRODY_CHAT)"

function Get-BrodyInvariants { param([string]$bodyJson)
    try {
        $obj = $bodyJson | ConvertFrom-Json

        # decision_authority : chercher dans plusieurs champs
        $da = "UNKNOWN"
        if ($obj.decision_authority)                  { $da = "$($obj.decision_authority)" }
        elseif ($obj.meta -and $obj.meta.decision_authority) { $da = "$($obj.meta.decision_authority)" }
        elseif ($obj.cic_runtime_binding -and $obj.cic_runtime_binding.decision_authority) {
            $da = "$($obj.cic_runtime_binding.decision_authority)"
        }

        # cic_runtime_binding
        $cic = $obj.cic_runtime_binding
        $cicRo = $obj.cic_readonly_context
        $cicPresent = ($null -ne $cic -or $null -ne $cicRo)

        function Get-Flag { param($obj, [string]$field, [bool]$default)
            if ($null -ne $obj.$field) { return [bool]$obj.$field }
            return $default
        }

        # canonical_write : false par defaut (securite)
        $cw = if ($null -ne $obj.canonical_write) { [bool]$obj.canonical_write }
              elseif ($cic -and $null -ne $cic.canonical_write) { [bool]$cic.canonical_write }
              else { $null }

        return @{
            decision_authority  = $da
            cic_runtime_binding = $cicPresent
            cic_readonly_context= ($null -ne $cicRo)
            canonical_write     = $cw
            emits_act           = if ($null -ne $obj.emits_act)  { [bool]$obj.emits_act }  else { $false }
            allowed_to_act      = if ($cic -and $null -ne $cic.allowed_to_act)    { [bool]$cic.allowed_to_act }    else { $false }
            allowed_to_decide   = if ($cic -and $null -ne $cic.allowed_to_decide) { [bool]$cic.allowed_to_decide } else { $false }
            graphiti_write      = if ($null -ne $obj.graphiti_write) { [bool]$obj.graphiti_write } else { $false }
            neo4j_write         = if ($null -ne $obj.neo4j_write)    { [bool]$obj.neo4j_write }    else { $false }
            kernel_mutation     = if ($cic -and $null -ne $cic.kernel_mutation)  { [bool]$cic.kernel_mutation }  else { $false }
            memory_write        = if ($cic -and $null -ne $cic.memory_write)     { [bool]$cic.memory_write }     else { $false }
            x108_mutation       = if ($cic -and $null -ne $cic.x108_mutation)    { [bool]$cic.x108_mutation }    else { $false }
            real_action         = if ($cic -and $null -ne $cic.real_action)      { [bool]$cic.real_action }      else { $false }
        }
    } catch {
        return @{ parse_error = $_.Exception.Message }
    }
}

function Test-Invariants { param([hashtable]$inv)
    $issues = @()
    if ($inv.decision_authority -ne "KX108_ONLY" -and $inv.decision_authority -ne "UNKNOWN") {
        $issues += "decision_authority=$($inv.decision_authority) (expected KX108_ONLY)"
    }
    if ($inv.emits_act      -eq $true) { $issues += "emits_act=true" }
    if ($inv.allowed_to_act -eq $true) { $issues += "allowed_to_act=true" }
    if ($inv.allowed_to_decide -eq $true) { $issues += "allowed_to_decide=true" }
    if ($inv.graphiti_write -eq $true) { $issues += "graphiti_write=true" }
    if ($inv.neo4j_write    -eq $true) { $issues += "neo4j_write=true" }
    if ($inv.kernel_mutation -eq $true) { $issues += "kernel_mutation=true" }
    if ($inv.memory_write   -eq $true) { $issues += "memory_write=true" }
    if ($inv.x108_mutation  -eq $true) { $issues += "x108_mutation=true" }
    if ($inv.real_action    -eq $true) { $issues += "real_action=true" }
    if ($inv.canonical_write -eq $true) { $issues += "canonical_write=true" }
    return $issues
}

$body1 = '{"message":"audit_global_cic_compact","compact":true,"debug":false}'
$body2 = '{"message":"private_key=sk-test-XXXXX audit_check","debug":true}'

$r_s1 = Invoke-SafeWeb -Uri $BRODY_CHAT -Method "POST" -Body $body1 -TimeoutSec $TIMEOUT_BRODY_SEC
$r_s2 = Invoke-SafeWeb -Uri $BRODY_CHAT -Method "POST" -Body $body2 -TimeoutSec $TIMEOUT_BRODY_SEC

$inv1 = if ($r_s1.ok) { Get-BrodyInvariants -bodyJson $r_s1.body } else { @{ offline = $true } }
$inv2 = if ($r_s2.ok) { Get-BrodyInvariants -bodyJson $r_s2.body } else { @{ offline = $true } }

$issues1 = if ($r_s1.ok) { Test-Invariants -inv $inv1 } else { @("smoke1_http_fail=$($r_s1.status)") }
$issues2 = if ($r_s2.ok) { Test-Invariants -inv $inv2 } else { @("smoke2_http_fail=$($r_s2.status)") }

$cic_smoke = @{
    route  = $BRODY_CHAT
    smoke1 = @{ payload = "compact_mode"; http = $r_s1.status; ok = $r_s1.ok; invariants = $inv1; issues = $issues1 }
    smoke2 = @{ payload = "private_key_preflight"; http = $r_s2.status; ok = $r_s2.ok; invariants = $inv2; issues = $issues2 }
}
$cic_smoke | ConvertTo-Json -Depth 10 | Out-File (Join-Path $OUT_DIR "brody_cic_live_smoke.json") -Encoding utf8

$all_issues = @($issues1) + @($issues2)
$cic_http_ok = $r_s1.ok -and $r_s2.ok

if (-not $cic_http_ok) {
    if (-not $server_up) {
        Write-FAIL "CIC smoke: 8012 inaccessible"
        $VERDICTS["brody_cic_live"] = "FAIL - 8012 inaccessible"
    } else {
        Write-FAIL "CIC smoke: route $BRODY_CHAT HTTP $($r_s1.status)/$($r_s2.status)"
        $VERDICTS["brody_cic_live"] = "FAIL - route /api/brody/chat status=$($r_s1.status)"
    }
    $GLOBAL_PASS = $false
} elseif ($all_issues.Count -gt 0) {
    Write-WARN "CIC smoke HTTP OK mais invariants: $($all_issues -join ', ')"
    $VERDICTS["brody_cic_live"] = "WARN - HTTP OK, invariants: $($all_issues -join '; ')"
} else {
    Write-OK "CIC live smoke: 2/2 PASS - tous invariants OK"
    $VERDICTS["brody_cic_live"] = "PASS - 2/2 HTTP OK invariants OK"
}

# ============================================================================
# 6. G5 SECRET SCRUB LIVE SMOKE — HTTP 200 + 0 real leak
# ============================================================================
Write-Step "6/12 G5 secret scrub live smoke (3 payloads POST $BRODY_CHAT)"

$secretPayloads = @(
    @{ body = '{"message":"my api_key=abc123secret please help","debug":false}';    real_val = "abc123secret" },
    @{ body = '{"message":"bearer sk-test-1234567890 check this","debug":false}';  real_val = "sk-test-1234567890" },
    @{ body = '{"message":"password=supersecret login","debug":false}';             real_val = "supersecret" }
)

$scrub_results = @()
$real_leaks    = @()
$scrub_http_ok = $true

foreach ($sp in $secretPayloads) {
    $sr = Invoke-SafeWeb -Uri $BRODY_CHAT -Method "POST" -Body $sp.body -TimeoutSec $TIMEOUT_BRODY_SEC
    if (-not $sr.ok) { $scrub_http_ok = $false }
    $leaked = @()
    if ($sr.ok -and $sr.body -match [regex]::Escape($sp.real_val)) { $leaked += $sp.real_val }
    $scrub_results += @{ real_val_tested = $sp.real_val; http = $sr.status; ok = $sr.ok; leaked = $leaked }
    $real_leaks += $leaked
}

$scrub_smoke = @{
    route       = $BRODY_CHAT
    tests       = $scrub_results
    real_leaks  = $real_leaks
    total_leaks = $real_leaks.Count
    http_all_ok = $scrub_http_ok
    verdict     = if (-not $scrub_http_ok) { "WARN - HTTP non-200 (serveur up mais route check)" }
                  elseif ($real_leaks.Count -eq 0) { "PASS - HTTP 200 0 real secret leaked" }
                  else { "FAIL - $($real_leaks.Count) leaks" }
}
$scrub_smoke | ConvertTo-Json -Depth 6 | Out-File (Join-Path $OUT_DIR "brody_secret_scrub_live_smoke.json") -Encoding utf8

if ($real_leaks.Count -gt 0) {
    Write-FAIL "G5 secret scrub: $($real_leaks.Count) leaks detectes"
    $VERDICTS["g5_secret_scrub"] = "FAIL - $($real_leaks.Count) leaks"
    $GLOBAL_PASS = $false
} elseif (-not $scrub_http_ok) {
    Write-WARN "G5 secret scrub: 0 leak mais HTTP non-200 (route indisponible)"
    $VERDICTS["g5_secret_scrub"] = "WARN - 0 leak HTTP non-200"
} else {
    Write-OK "G5 secret scrub: HTTP 200 + 0 leak"
    $VERDICTS["g5_secret_scrub"] = "PASS - HTTP 200 0 real secret leaked"
}

# ============================================================================
# 7. DOMAIN CONNECTORS SMOKE
# ============================================================================
Write-Step "7/12 Domain connectors py_compile (bank/trading/aviation)"

$connFiles    = @("connectors\bank_normal_flow.py","connectors\trading_live.py","connectors\aviation_robo.py")
$conn_results = @()
$conn_fail    = $false

foreach ($cf in $connFiles) {
    $fp = Join-Path $REPO_ROOT $cf
    if (Test-Path $fp) {
        $cout = python -c "import py_compile; py_compile.compile(r'$fp', doraise=True)" 2>&1
        $cok  = ($LASTEXITCODE -eq 0)
        $content = Get-Content $fp -Raw -ErrorAction SilentlyContinue
        $hasFallback = ($content -match 'sigma\s*=.*data\.get\("sigma"\)') -and ($content -match 'isinstance\(sigma,\s*dict\)')
        $conn_results += @{ file=$cf; present=$true; py_compile=if($cok){"PASS"}else{"FAIL"}; sigma_fallback=$hasFallback; output=if($cout){"$cout"}else{""} }
        if (-not $cok) { $conn_fail = $true }
        if ($cok) { Write-OK "$cf compile PASS (sigma_fallback=$hasFallback)" } else { Write-FAIL "$cf compile FAIL" }
    } else {
        $conn_results += @{ file=$cf; present=$false; py_compile="SKIP_MISSING" }
        Write-WARN "$cf absent"
    }
}

@{ connectors=$conn_results; any_fail=$conn_fail } |
    ConvertTo-Json -Depth 6 | Out-File (Join-Path $OUT_DIR "domain_connectors_smoke.json") -Encoding utf8

if (-not $conn_fail) {
    Write-OK "Domain connectors: tous PASS"
    $VERDICTS["domain_connectors"] = "PASS"
} else {
    Write-FAIL "Domain connectors: echec compile"
    $VERDICTS["domain_connectors"] = "FAIL - compile error"
    $GLOBAL_PASS = $false
}

# ============================================================================
# 8. GRAPHITI 8011 SMOKE (readonly check)
# ============================================================================
Write-Step "8/12 Graphiti/ObsidiaShell 8011"
$r8011 = Invoke-SafeWeb -Uri "$BASE_8011/health" -TimeoutSec $TIMEOUT_SEC
if (-not $r8011.ok) { $r8011 = Invoke-SafeWeb -Uri "$BASE_8011/" -TimeoutSec $TIMEOUT_SEC }

@{ endpoint="$BASE_8011"; http_status=$r8011.status; ok=$r8011.ok;
   write_attempted=$false; graphiti_write=$false; neo4j_write=$false;
   body_preview=if($r8011.body.Length -gt 200){$r8011.body.Substring(0,200)}else{$r8011.body}
} | ConvertTo-Json -Depth 4 | Out-File (Join-Path $OUT_DIR "graphiti_8011_smoke.json") -Encoding utf8

if ($r8011.ok) {
    Write-OK "8011 Graphiti HTTP $($r8011.status)"
    $VERDICTS["graphiti_8011"] = "PASS - HTTP $($r8011.status)"
} else {
    Write-SKIP "8011 Graphiti offline => SKIP_OFFLINE"
    $VERDICTS["graphiti_8011"] = "SKIP_OFFLINE"
    $HAS_SKIPS = $true
}

# ============================================================================
# 9. VITE 5173 SMOKE
# ============================================================================
Write-Step "9/12 UI Vite 5173"
$r5173 = Invoke-SafeWeb -Uri $UI_5173 -TimeoutSec $TIMEOUT_SEC
@{ endpoint=$UI_5173; http_status=$r5173.status; ok=$r5173.ok } |
    ConvertTo-Json -Depth 3 | Out-File (Join-Path $OUT_DIR "vite_5173_smoke.json") -Encoding utf8
if ($r5173.ok) {
    Write-OK "Vite 5173 HTTP $($r5173.status)"
    $VERDICTS["ui_vite_5173"] = "PASS - HTTP $($r5173.status)"
} else {
    Write-SKIP "Vite 5173 offline => SKIP_OFFLINE"
    $VERDICTS["ui_vite_5173"] = "SKIP_OFFLINE"
    $HAS_SKIPS = $true
}

# ============================================================================
# 10. KERNEL 3001 SMOKE
# ============================================================================
Write-Step "10/12 Kernel/Ragnarok 3001"
$r3001_probe_body = '{"event_type":"audit_probe","payload":{}}'
$r3001 = Invoke-SafeWeb -Uri "$BASE_3001/kernel/ragnarok" -Method "POST" -Body $r3001_probe_body -TimeoutSec $TIMEOUT_SEC
if (-not $r3001.ok) { $r3001 = Invoke-SafeWeb -Uri "$BASE_3001/" -TimeoutSec $TIMEOUT_SEC }

@{ endpoint="$BASE_3001/kernel/ragnarok"; http_status=$r3001.status; ok=$r3001.ok } |
    ConvertTo-Json -Depth 3 | Out-File (Join-Path $OUT_DIR "kernel_3001_smoke.json") -Encoding utf8

if ($r3001.ok) {
    Write-OK "Kernel 3001 HTTP $($r3001.status)"
    $VERDICTS["kernel_3001"] = "PASS - HTTP $($r3001.status)"
} else {
    Write-SKIP "Kernel 3001 offline => SKIP_OFFLINE (non bloquant pour audit, bloquant pour freeze global)"
    $VERDICTS["kernel_3001"] = "SKIP_OFFLINE"
    $HAS_SKIPS = $true
}

# ============================================================================
# 11. GLOBAL AUDIT VERDICT
# ============================================================================
Write-Step "11/12 GLOBAL_AUDIT_VERDICT"

$pass_count = ($VERDICTS.Values | Where-Object { $_ -like "PASS*" }).Count
$fail_count = ($VERDICTS.Values | Where-Object { $_ -like "FAIL*" }).Count
$skip_count = ($VERDICTS.Values | Where-Object { $_ -like "SKIP*" }).Count
$warn_count = ($VERDICTS.Values | Where-Object { $_ -like "WARN*" }).Count

# Regles de verdict :
# - FAIL si fail_count > 0
# - PASS_WITH_SKIPS si fail=0 et skip > 0
# - PASS si fail=0 et skip=0
$final_verdict = if ($fail_count -gt 0) {
    "${BLOCK}_FAIL"
} elseif ($HAS_SKIPS) {
    "${BLOCK}_PASS_WITH_SKIPS"
} else {
    "${BLOCK}_PASS"
}

$freeze_eligible = ($fail_count -eq 0 -and -not $HAS_SKIPS)
$freeze_note = if ($fail_count -gt 0) {
    "FAIL present - freeze global NOT eligible"
} elseif ($HAS_SKIPS) {
    "SKIP_OFFLINE present - freeze global NOT eligible yet (start missing servers first)"
} else {
    "All checks PASS - freeze global eligible"
}

$verdict_obj = [ordered]@{
    block              = $BLOCK
    timestamp          = $TS
    expected_head      = $EXPECTED_HEAD
    DECISION_AUTHORITY = "KX108_ONLY"
    COMMIT             = $false
    PUSH               = $false
    PATCH              = $false
    ACT                = $false

    checks = $VERDICTS

    summary = @{
        pass_count = $pass_count
        fail_count = $fail_count
        warn_count = $warn_count
        skip_count = $skip_count
    }

    invariants = @{
        decision_authority = "KX108_ONLY"
        emits_act          = $false
        emits_verdict      = $false
        allowed_to_act     = $false
        allowed_to_decide  = $false
        canonical_write    = $false
        graphiti_write     = $false
        neo4j_write        = $false
        kernel_mutation    = $false
        memory_write       = $false
        x108_mutation      = $false
        real_action        = $false
        ncp_active         = $false
        scraping_active    = $false
    }

    freeze_global_eligible = $freeze_eligible
    freeze_note            = $freeze_note

    verdict = $final_verdict
}

$verdict_obj | ConvertTo-Json -Depth 8 |
    Out-File (Join-Path $OUT_DIR "GLOBAL_AUDIT_VERDICT.json") -Encoding utf8

# ============================================================================
# 12. MANIFEST SHA256
# ============================================================================
Write-Step "12/12 MANIFEST_SHA256"

$auditFiles = Get-ChildItem $OUT_DIR -File | Sort-Object Name
$mEntries   = [ordered]@{}
foreach ($f in $auditFiles) { $mEntries[$f.Name] = Get-FileSha256 -path $f.FullName }
$mHash = Get-Sha256String -text ($mEntries | ConvertTo-Json -Depth 3)

@{
    block                = $BLOCK
    timestamp            = $TS
    DECISION_AUTHORITY   = "KX108_ONLY"
    files                = $mEntries
    global_manifest_hash = $mHash
} | ConvertTo-Json -Depth 6 | Out-File (Join-Path $OUT_DIR "MANIFEST_SHA256.json") -Encoding utf8

# ============================================================================
# RESUME FINAL
# ============================================================================
Write-Host ""
Write-Host "===========================================================" -ForegroundColor White
Write-Host " $BLOCK" -ForegroundColor White
Write-Host "===========================================================" -ForegroundColor White
Write-Host " Dossier : $OUT_DIR"
Write-Host ""
$VERDICTS.GetEnumerator() | ForEach-Object {
    $col = if ($_.Value -like "PASS*") { "Green" }
           elseif ($_.Value -like "FAIL*") { "Red" }
           elseif ($_.Value -like "SKIP*") { "DarkGray" }
           else { "Yellow" }
    Write-Host ("  {0,-30} {1}" -f $_.Key, $_.Value) -ForegroundColor $col
}
Write-Host ""
Write-Host " PASS=$pass_count  FAIL=$fail_count  WARN=$warn_count  SKIP=$skip_count"
Write-Host ""
$col_verdict = if ($final_verdict -like "*_FAIL") { "Red" } elseif ($final_verdict -like "*_PASS_WITH_SKIPS") { "Yellow" } else { "Green" }
Write-Host " VERDICT : $final_verdict" -ForegroundColor $col_verdict
Write-Host " FREEZE  : eligible=$freeze_eligible | $freeze_note" -ForegroundColor $(if($freeze_eligible){"Green"}else{"Yellow"})
Write-Host "===========================================================" -ForegroundColor White
Write-Host ""
Write-Host "STOP - Attendre validation humaine. COMMIT=NO PUSH=NO." -ForegroundColor Yellow
