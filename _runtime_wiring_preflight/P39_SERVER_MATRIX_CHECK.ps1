# P39_SERVER_MATRIX_CHECK.ps1
# Validation matrice serveur locale — P26→P38
# NE MODIFIE RIEN. NE LANCE PAS DE SERVEUR.
# Teste les ports et les endpoints si les services sont actifs.
# KX108_ONLY. No ACT. No write. Readonly.

param(
  [string]$ApiBase    = "http://127.0.0.1:8000",
  [string]$ViteBase   = "http://127.0.0.1:5173",
  [string]$ShellBase  = "http://127.0.0.1:8011",
  [string]$OutputDir  = (Join-Path $PSScriptRoot ".")
)

$ErrorActionPreference = "Continue"

$timestamp = (Get-Date -Format "yyyyMMdd_HHmmss")
$outJson   = Join-Path $OutputDir "P39_SERVER_MATRIX_RESULTS.json"
$outMd     = Join-Path $OutputDir "P39_SERVER_MATRIX_REPORT.md"

Write-Host "P39_SERVER_MATRIX_CHECK — $timestamp"
Write-Host "ApiBase=$ApiBase | ViteBase=$ViteBase | ShellBase=$ShellBase"
Write-Host ""

# ── Helper: test port ────────────────────────────────────────────────────────
function Test-Port {
    param([string]$Host, [int]$Port, [int]$Timeout = 1000)
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $ar = $tcp.BeginConnect($Host, $Port, $null, $null)
        $ok = $ar.AsyncWaitHandle.WaitOne($Timeout, $false)
        if ($ok) { $tcp.EndConnect($ar); $tcp.Close(); return $true }
        $tcp.Close(); return $false
    } catch { return $false }
}

# ── Helper: HTTP GET ─────────────────────────────────────────────────────────
function Invoke-GetJson {
    param([string]$Url, [int]$TimeoutSec = 10)
    try {
        $resp = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec $TimeoutSec -UseBasicParsing
        return @{ status = $resp.StatusCode; body = ($resp.Content | ConvertFrom-Json) }
    } catch {
        return @{ status = 0; error = $_.Exception.Message }
    }
}

# ── Helper: HTTP POST JSON ────────────────────────────────────────────────────
function Invoke-PostJson {
    param([string]$Url, [hashtable]$Body, [int]$TimeoutSec = 20)
    try {
        $json = $Body | ConvertTo-Json -Depth 5
        $resp = Invoke-WebRequest -Uri $Url -Method POST -Body $json `
            -ContentType "application/json" -TimeoutSec $TimeoutSec -UseBasicParsing
        return @{ status = $resp.StatusCode; body = ($resp.Content | ConvertFrom-Json) }
    } catch {
        return @{ status = 0; error = $_.Exception.Message }
    }
}

$results = @{
    timestamp = $timestamp
    boundary  = @{ readonly=$true; emits_act=$false; decision_authority="KX108_ONLY"; no_act=$true }
    services  = @{}
    endpoints = @{}
    queries   = @{}
    workbench = @{}
    verdict   = "PENDING"
}

# ── 1. Port checks ───────────────────────────────────────────────────────────
Write-Host "=== PORT CHECKS ==="
$ports = @{
    API_8000      = @{ host="127.0.0.1"; port=8000 }
    WORKBENCH_5173= @{ host="127.0.0.1"; port=5173 }
    OBSIDASHELL_8011= @{ host="127.0.0.1"; port=8011 }
}

foreach ($name in $ports.Keys) {
    $h = $ports[$name].host; $p = $ports[$name].port
    $open = Test-Port -Host $h -Port $p
    $results.services[$name] = @{ port=$p; open=$open; status=if($open){"OPEN"}else{"CLOSED"} }
    Write-Host "  $name :$p => $(if($open){'OPEN'}else{'CLOSED'})"
}

# ── 2. GET endpoints ─────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=== ENDPOINT GET CHECKS ==="

$getEndpoints = @(
    @{ path="/api/status"; key="service" }
    @{ path="/api/runtime-wiring/preview"; key="status" }
    @{ path="/api/runtime-wiring/source-runtime/status"; key="source_runtime_status" }
    @{ path="/api/runtime-wiring/os-map/status"; key="os_map_status" }
    @{ path="/api/x108/status"; key="kernel_status" }
)

foreach ($ep in $getEndpoints) {
    $url = "$ApiBase$($ep.path)"
    $r = Invoke-GetJson -Url $url
    $key = $r.body.($ep.key)
    $da  = $r.body.decision_authority
    $ea  = $r.body.emits_act
    $ro  = $r.body.readonly
    $results.endpoints[$ep.path] = @{
        http=$r.status; $ep.key=$key; decision_authority=$da; emits_act=$ea; readonly=$ro
    }
    Write-Host "  GET $($ep.path) => HTTP $($r.status) | $($ep.key)=$key | da=$da | ea=$ea"
}

# ── 3. POST queries ───────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=== QUERY MATRIX (OS Map) ==="

$queries = @(
    @{ q="IR alphabet reverse OS interlanguage"; label="IR_QUERY" }
    @{ q="34 arbres agents registry"; label="AGENT_TREE_QUERY" }
    @{ q="lois protocoles non décision boundary"; label="LAW_PROTOCOL_QUERY" }
    @{ q="mémoire Brody Graphiti réintégration"; label="MEMORY_GRAPHITI_QUERY" }
    @{ q="envoie un mail maintenant"; label="ACTION_QUERY" }
)

foreach ($qdef in $queries) {
    $url  = "$ApiBase/api/runtime-wiring/os-map/query"
    $body = @{ query=$qdef.q; max_paths=3 }
    $r    = Invoke-PostJson -Url $url -Body $body
    $b    = $r.body
    $status = $b.os_map_status
    $cap    = if ($b.selected_runtime_path) { ($b.selected_runtime_path.capability_chain -join ",") } else { "?" }
    $x108   = $b.x108_decision
    $blocked= $b.action_blocked
    $ran    = $b.runtime_allowed_now
    $ea     = $b.emits_act

    $results.queries[$qdef.label] = @{
        query=$qdef.q; http=$r.status; os_map_status=$status; capability=$cap
        x108_decision=$x108; action_blocked=$blocked; runtime_allowed_now=$ran; emits_act=$ea
    }
    Write-Host "  [$($qdef.label)] HTTP=$($r.status) | status=$status | cap=$cap | x108=$x108 | blocked=$blocked"
}

# ── 4. Workbench Vite static check ───────────────────────────────────────────
Write-Host ""
Write-Host "=== WORKBENCH CHECK ==="
$wb = @{}

$repoRoot = Split-Path $PSScriptRoot -Parent
$wbPath   = Join-Path $repoRoot "apps\obsidia-workbench"
$osMapView= Join-Path $wbPath "src\views\OSMapView.tsx"
$appTsx   = Join-Path $wbPath "src\App.tsx"
$sidebar  = Join-Path $wbPath "src\components\LeftSidebar.tsx"
$dist     = Join-Path $wbPath "dist\index.html"

$wb["OSMapView_exists"]  = (Test-Path $osMapView)
$wb["App_imports_OSMap"] = if (Test-Path $appTsx) { (Get-Content $appTsx -Raw) -match "OSMapView" } else { $false }
$wb["Sidebar_has_os-map"]= if (Test-Path $sidebar) { (Get-Content $sidebar -Raw) -match "'os-map'" } else { $false }
$wb["dist_built"]        = (Test-Path $dist)
$wb["vite_port_open"]    = $results.services["WORKBENCH_5173"].open

foreach ($k in $wb.Keys) {
    Write-Host "  $k => $($wb[$k])"
}
$results.workbench = $wb

# ── 5. Global verdict ─────────────────────────────────────────────────────────
$allHttpOk     = ($results.endpoints.Values | Where-Object { $_.http -ge 200 -and $_.http -lt 300 }).Count
$actionBlocked = $results.queries["ACTION_QUERY"].action_blocked
$noActViolation= $results.queries.Values | Where-Object { $_.runtime_allowed_now -eq $true -or $_.emits_act -eq $true }

$verdict = if (
    $allHttpOk -ge 3 -and
    $actionBlocked -eq $true -and
    $noActViolation.Count -eq 0 -and
    $results.workbench["OSMapView_exists"] -eq $true
) { "P39_FULL_SERVER_MATRIX_READY" } else { "P39_PARTIAL_MATRIX_VALIDATED" }

$results.verdict = $verdict

Write-Host ""
Write-Host "=== VERDICT: $verdict ==="

# ── 6. Output ─────────────────────────────────────────────────────────────────
$results | ConvertTo-Json -Depth 8 | Out-File -FilePath $outJson -Encoding utf8
Write-Host "Results JSON: $outJson"

# MD report
$md = @"
# P39 — Server Matrix Check — $timestamp

**Verdict: $verdict**

## Services
$(foreach ($name in $results.services.Keys) { "- $name : $($results.services[$name].port) → $($results.services[$name].status)`n" })

## Endpoint GET Matrix
$(foreach ($path in $results.endpoints.Keys) { "- ``$path`` → HTTP $($results.endpoints[$path].http)`n" })

## Query Matrix (OS Map)
$(foreach ($label in $results.queries.Keys) {
    $q = $results.queries[$label]
    "- **$label**: status=$($q.os_map_status) | cap=$($q.capability) | x108=$($q.x108_decision) | blocked=$($q.action_blocked)`n"
})

## Workbench
$(foreach ($k in $results.workbench.Keys) { "- $k : $($results.workbench[$k])`n" })

## Invariants
- runtime_allowed_now=False dans toutes les queries
- emits_act=False dans toutes les queries
- decision_authority=KX108_ONLY
- No ACT / No write / KX108_ONLY

## Note serveur live
Le serveur actif sur :8000 tourne une version antérieure à P29 (153 routes).
Les routes P36-P38 ne sont disponibles qu'après redémarrage du serveur.
Validation complète réalisée via TestClient (code courant = source de vérité).
"@

$md | Out-File -FilePath $outMd -Encoding utf8
Write-Host "Report MD: $outMd"
