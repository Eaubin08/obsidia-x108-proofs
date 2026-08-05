# ============================================================
# 01_START_BRODY_STACK.ps1
# OBSIDIA / BRODY FULL STACK LAUNCH
# Servers + UI + Docs + Neo4j Browser + Brody V1 + Brody Enriched
# Exclut volontairement le terminal brut inspector
# Source : section "OBSIDIA / BRODY FULL STACK LAUNCH" du DOCX
#
# Chemin auto-détecté depuis $PSScriptRoot — aucun chemin absolu à modifier.
# ============================================================

# ── Auto-détection des chemins ─────────────────────────────────────────────
# Ce script est dans scripts/OBSIDIA_LAUNCHERS/ → repo root = deux niveaux au-dessus
$X108  = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$ROOT  = Split-Path -Parent $X108
$SHELL = Join-Path $ROOT "obsidiashell-main"

$API             = "http://127.0.0.1:8000"
$GRAPH           = "http://127.0.0.1:8011"
$UI              = "http://127.0.0.1:5173"
$NEO4J           = "http://127.0.0.1:7475/browser/"
$GRAPH_WORKBENCH = "$GRAPH/graph/v20/frozen/workbench"
$GRAPH_DOCS      = "$GRAPH/docs#/default/graph_v20_frozen_workbench_graph_v20_frozen_workbench_get"

Set-Location $X108
Write-Host "  Repo  : $X108"  -ForegroundColor Gray
Write-Host "  Root  : $ROOT"  -ForegroundColor Gray
Write-Host "  Shell : $SHELL" -ForegroundColor Gray

# ============================================================
# 0. CLEAN OLD LOCAL SERVER PORTS (8000, 8011, 5173)
# ============================================================
Write-Host "`n=== 0. CLEAN OLD LOCAL SERVER PORTS ===" -ForegroundColor Cyan

$PORTS_TO_KILL = @(8000, 8011, 5173)
foreach ($P in $PORTS_TO_KILL) {
    $LINES = netstat -ano | Select-String ":$P\s"
    foreach ($L in $LINES) {
        if ($L -match "LISTENING\s+(\d+)") {
            $PID_TO_KILL = $Matches[1]
            Write-Host "KILL PORT $P  PID $PID_TO_KILL" -ForegroundColor Yellow
            Stop-Process -Id $PID_TO_KILL -Force -ErrorAction SilentlyContinue
        }
    }
}
Start-Sleep -Seconds 2

# ============================================================
# 1. NEO4J DOCKER
# ============================================================
Write-Host "`n=== 1. START NEO4J DOCKER ===" -ForegroundColor Cyan
docker start deploy-neo4j-1 | Out-Host
Start-Sleep -Seconds 3
docker ps | Select-String "neo4j|deploy-neo4j" | Out-Host

# ============================================================
# 2. API BRODY / OBSIDIA — 8000
# ============================================================
Write-Host "`n=== 2. START API BRODY / OBSIDIA - 8000 ===" -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "[Console]::Title='OBSIDIA API 8000 - BRODY STACK'; Set-Location '$X108'; `$env:PYTHONPATH='$X108'; python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
)
Start-Sleep -Seconds 6

Write-Host "`n=== CHECK API 8000 ===" -ForegroundColor Cyan
try {
    Invoke-RestMethod "$API/" | ConvertTo-Json -Depth 8 | Out-Host
} catch {
    Write-Host "API 8000 NOT READY - $($_.Exception.Message)" -ForegroundColor Red
}

# ============================================================
# 3. GRAPHITI FROZEN BRIDGE — 8011
# ============================================================
Write-Host "`n=== 3. START GRAPHITI FROZEN BRIDGE - 8011 ===" -ForegroundColor Cyan

if (-not (Test-Path $SHELL)) {
    Write-Host "[WARN] obsidiashell-main introuvable : $SHELL" -ForegroundColor Yellow
    Write-Host "  Graphiti 8011 ignore - verifier que obsidiashell-main est dans $ROOT" -ForegroundColor Yellow
} else {
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "[Console]::Title='GRAPHITI FROZEN BRIDGE 8011'; Set-Location '$SHELL'; python -m uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011"
    )
    Start-Sleep -Seconds 6

    Write-Host "`n=== CHECK GRAPHITI 8011 ===" -ForegroundColor Cyan
    try {
        Invoke-RestMethod "$GRAPH/graph/v20/frozen/status" | ConvertTo-Json -Depth 8 | Out-Host
    } catch {
        Write-Host "GRAPHITI 8011 NOT READY - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ============================================================
# 4. UI WORKBENCH — 5173
# ============================================================
Write-Host "`n=== 4. START UI WORKBENCH - 5173 ===" -ForegroundColor Cyan
$UI_DIR = Join-Path $X108 "apps\obsidia-workbench"
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "[Console]::Title='OBSIDIA WORKBENCH UI 5173'; Set-Location '$UI_DIR'; npm run dev -- --host 127.0.0.1 --port 5173"
)
Start-Sleep -Seconds 7

Write-Host "`n=== CHECK UI 5173 ===" -ForegroundColor Cyan
try {
    $STATUS = (Invoke-WebRequest "$UI" -UseBasicParsing -TimeoutSec 5).StatusCode
    Write-Host "UI status=$STATUS" -ForegroundColor Green
} catch {
    Write-Host "UI 5173 NOT READY - $($_.Exception.Message)" -ForegroundColor Red
}

# ============================================================
# 5. OPEN BROWSERS
# ============================================================
Write-Host "`n=== 5. OPEN BROWSERS ===" -ForegroundColor Cyan
Start-Process "$UI"
Start-Process "$GRAPH_WORKBENCH"
Start-Process "$GRAPH_DOCS"
Start-Process "$NEO4J"

# ============================================================
# 6. BRODY V1 CHAT TERMINAL
# ============================================================
Write-Host "`n=== 6. START BRODY V1 CHAT TERMINAL ===" -ForegroundColor Cyan
$BRODY_V1_CHAT = Join-Path $X108 "scripts\run_brody_terminal_chat.ps1"
if (Test-Path $BRODY_V1_CHAT) {
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-File", "`"$BRODY_V1_CHAT`"",
        "$API"
    )
} else {
    Write-Host "[WARN] run_brody_terminal_chat.ps1 introuvable : $BRODY_V1_CHAT" -ForegroundColor Yellow
}

# ============================================================
# 7. BRODY ENRICHED TERMINAL
# ============================================================
Write-Host "`n=== 7. START BRODY ENRICHED TERMINAL ===" -ForegroundColor Cyan
$BRODY_ENRICHED = Join-Path $X108 "scripts\run_brody_terminal_enriched.ps1"
if (-not (Test-Path $BRODY_ENRICHED)) {
    $BRODY_ENRICHED = Join-Path $X108 "ci_recheck_optional_publication\scripts\run_brody_terminal_enriched.ps1"
}
if (Test-Path $BRODY_ENRICHED) {
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-File", "`"$BRODY_ENRICHED`"",
        "-Base", "$API"
    )
} else {
    Write-Host "[WARN] run_brody_terminal_enriched.ps1 introuvable" -ForegroundColor Yellow
}

Start-Sleep -Seconds 3

# ============================================================
# 8. FINAL PORT CHECK
# ============================================================
Write-Host "`n=== 8. FINAL PORT CHECK ===" -ForegroundColor Cyan
netstat -ano | Select-String ":8000|:8011|:5173|:7475|:7688" | Out-Host

Write-Host "`n=== STACK BRODY READY ===" -ForegroundColor Green
Write-Host "API Brody         : $API"
Write-Host "Graphiti bridge   : $GRAPH"
Write-Host "Graphiti Docs     : $GRAPH_DOCS"
Write-Host "Graphiti Workbench: $GRAPH_WORKBENCH"
Write-Host "UI Workbench      : $UI"
Write-Host "Neo4j Browser     : $NEO4J"
Write-Host "Brody V1          : terminal lancé"
Write-Host "Brody Enriched    : terminal lancé"
