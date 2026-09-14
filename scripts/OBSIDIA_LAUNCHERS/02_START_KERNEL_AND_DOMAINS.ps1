# ============================================================
# 02_START_KERNEL_AND_DOMAINS.ps1
# CANONICAL LIVE MATRIX — Kernel Ragnarok 3001 + API Bridge 8000 + Domaines
# Lance : Kernel Ragnarok 3001, API Live Kernel Bridge 8000,
#         Bank connector, Trading connector, Aviation/GPS connector
# Source : section "CMD relance complète — matrice propre" du DOCX
#
# Chemin auto-détecté depuis $PSScriptRoot — aucun chemin absolu à modifier.
# ============================================================

# ── Auto-détection du repo root ────────────────────────────────────────────
# Ce script est dans scripts/OBSIDIA_LAUNCHERS/ → repo root = deux niveaux au-dessus
$REPO = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$RT   = Join-Path $REPO "runtime_terrain_bank_trading_gps"

Set-Location $REPO
Write-Host "  Repo : $REPO" -ForegroundColor Gray
Write-Host "  RT   : $RT"   -ForegroundColor Gray

# Vérification critique avant de lancer
if (-not (Test-Path "$RT\server.kernel.sealed.cjs")) {
    Write-Host "[ERREUR] server.kernel.sealed.cjs introuvable dans : $RT" -ForegroundColor Red
    Write-Host "  Repo détecté : $REPO" -ForegroundColor Red
    exit 1
}

# ============================================================
# STOP CANONICAL LIVE MATRIX (nettoyage avant relance)
# ============================================================
Write-Host "`n=== STOP CANONICAL LIVE MATRIX ===" -ForegroundColor Cyan

Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match "server\.kernel\.sealed\.cjs" -or
    $_.CommandLine -match "uvicorn apps\.obsidia_api\.main:app --host 127\.0\.0\.1 --port 8000" -or
    $_.CommandLine -match "connectors\\bank_normal_flow\.py" -or
    $_.CommandLine -match "connectors\\trading_live\.py" -or
    $_.CommandLine -match "connectors\\aviation_robo\.py"
} | ForEach-Object {
    Write-Host "Stopping PID=$($_.ProcessId)  CMD=$($_.CommandLine)" -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 2

# Arrêt par port 3001 et 8000
foreach ($port in @(3001, 8000)) {
    $pids = netstat -ano | Select-String ":$port\s" |
        Where-Object { $_.Line -match "LISTENING" } |
        ForEach-Object { ($_ -split "\s+")[-1] } |
        Sort-Object -Unique

    foreach ($pid in $pids) {
        if ($pid -and $pid -ne "0") {
            Write-Host "Stopping port $port  PID=$pid" -ForegroundColor Yellow
            Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
        }
    }
}

Start-Sleep -Seconds 2

# ============================================================
# 1. KERNEL RAGNAROK — 3001
# ============================================================
Write-Host "`n=== START KERNEL RAGNAROK 3001 ===" -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    [Console]::Title='RAGNAROK KERNEL 3001 - AUTHORITY';
    Set-Location '$RT';
    node .\server.kernel.sealed.cjs
"
Start-Sleep -Seconds 4

# ============================================================
# 2. API OBSIDIA — 8000 (Live Kernel Bridge)
# ============================================================
Write-Host "`n=== START OBSIDIA API 8000 - LIVE KERNEL BRIDGE ===" -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    [Console]::Title='OBSIDIA API 8000 - LIVE KERNEL BRIDGE';
    Set-Location '$REPO';
    `$env:PYTHONPATH='$REPO';
    `$env:OBSIDIA_KERNEL_URL='http://127.0.0.1:3001/kernel/ragnarok';
    python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000
"
Start-Sleep -Seconds 7

# ============================================================
# CHECK API 8000 HEALTH
# ============================================================
Write-Host "`n=== CHECK API 8000 HEALTH ===" -ForegroundColor Cyan
try {
    Invoke-RestMethod "http://127.0.0.1:8000/api/health" -TimeoutSec 10 | ConvertTo-Json -Depth 6
} catch {
    Write-Host "API 8000 NOT READY - $($_.Exception.Message)" -ForegroundColor Red
}

# ============================================================
# CHECK LIVE KERNEL BRIDGE ROUTES
# ============================================================
Write-Host "`n=== CHECK LIVE KERNEL BRIDGE ROUTES ===" -ForegroundColor Cyan
try {
    $openapi = Invoke-RestMethod "http://127.0.0.1:8000/openapi.json" -TimeoutSec 10
    $openapi.paths.PSObject.Properties |
        Where-Object { $_.Name -match "/api/live/kernel/adapters" } |
        Select-Object Name |
        Format-Table -AutoSize
} catch {
    Write-Host "OPENAPI CHECK FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# ============================================================
# 3. DOMAIN CONNECTORS (Bank, Trading, Aviation/GPS)
# ============================================================
Write-Host "`n=== START DOMAIN CONNECTORS ===" -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    [Console]::Title='BANK LIVE -> KERNEL BRIDGE';
    Set-Location '$REPO';
    `$env:PYTHONPATH='$REPO';
    `$env:OBSIDIA_API_BASE='http://127.0.0.1:8000';
    python .\connectors\bank_normal_flow.py
"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    [Console]::Title='TRADING LIVE -> KERNEL BRIDGE';
    Set-Location '$REPO';
    `$env:PYTHONPATH='$REPO';
    `$env:OBSIDIA_API_BASE='http://127.0.0.1:8000';
    python .\connectors\trading_live.py
"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    [Console]::Title='GPS/AVIATION LIVE -> KERNEL BRIDGE';
    Set-Location '$REPO';
    `$env:PYTHONPATH='$REPO';
    `$env:OBSIDIA_API_BASE='http://127.0.0.1:8000';
    python .\connectors\aviation_robo.py
"

Start-Sleep -Seconds 5

# ============================================================
# FINAL PROCESS CHECK
# ============================================================
Write-Host "`n=== FINAL PROCESS CHECK ===" -ForegroundColor Cyan
netstat -ano | findstr ":3001"
netstat -ano | findstr ":8000"

Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match "server\.kernel\.sealed\.cjs" -or
    $_.CommandLine -match "uvicorn apps\.obsidia_api\.main:app --host 127\.0\.0\.1 --port 8000" -or
    $_.CommandLine -match "connectors\\bank_normal_flow\.py" -or
    $_.CommandLine -match "connectors\\trading_live\.py" -or
    $_.CommandLine -match "connectors\\aviation_robo\.py"
} | Select-Object ProcessId, CommandLine | Format-List

Write-Host "`nLIVE MATRIX RESTART DONE" -ForegroundColor Green
Write-Host "Regarde maintenant le terminal RAGNAROK KERNEL 3001 : il doit afficher BANK / TRADING / GPS." -ForegroundColor Green
Write-Host ""
Write-Host "Résultat attendu côté kernel :"
Write-Host "  [BRIDGE] Routing -> Domain: bank"
Write-Host "  [KERNEL_DECISION] ..."
Write-Host "  [SAVE] decision_bank_..."
Write-Host "  [BRIDGE] Routing -> Domain: trading"
Write-Host "  [KERNEL_DECISION] ..."
Write-Host "  [SAVE] decision_trading_..."
Write-Host "  [BRIDGE] Routing -> Domain: gps_defense_aviation"
Write-Host "  [KERNEL_DECISION] ..."
Write-Host "  [SAVE] decision_gps_defense_aviation_..."
