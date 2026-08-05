# ============================================================
# 00_STOP_ALL_SERVERS.ps1
# OBSIDIA — Nettoyage complet de tous les serveurs locaux
# Ports ciblés : 3001 (Kernel Ragnarok), 8000 (API), 8011 (Graphiti), 5173 (UI)
# Source : "CLEAN OLD LOCAL SERVER PORTS" + "STOP CANONICAL LIVE MATRIX"
#
# Chemin auto-détecté depuis $PSScriptRoot — aucun chemin absolu à modifier.
# ============================================================

# ── Auto-détection du repo root ────────────────────────────────────────────
$REPO = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$RT   = Join-Path $REPO "runtime_terrain_bank_trading_gps"

Set-Location $REPO
Write-Host "  Repo : $REPO" -ForegroundColor Gray

Write-Host "`n=== STOP CANONICAL LIVE MATRIX ===" -ForegroundColor Cyan

# Arrêt par ligne de commande (processus nommés)
Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match "server\.kernel\.sealed\.cjs" -or
    $_.CommandLine -match "uvicorn apps\.obsidia_api\.main:app" -or
    $_.CommandLine -match "connectors\\bank_normal_flow\.py" -or
    $_.CommandLine -match "connectors\\trading_live\.py" -or
    $_.CommandLine -match "connectors\\aviation_robo\.py" -or
    $_.CommandLine -match "obsidia_core\.agent_bridge" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite"
} | ForEach-Object {
    Write-Host "Stopping PID=$($_.ProcessId)  CMD=$($_.CommandLine)" -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 2

Write-Host "`n=== CLEAN OLD LOCAL SERVER PORTS ===" -ForegroundColor Cyan

# Arrêt par port — cible : 3001, 8000, 8011, 5173
$PORTS_TO_KILL = @(3001, 8000, 8011, 5173)

foreach ($P in $PORTS_TO_KILL) {
    $LINES = netstat -ano | Select-String ":$P\s"
    foreach ($L in $LINES) {
        if ($L -match "LISTENING\s+(\d+)") {
            $PID_TO_KILL = $Matches[1]
            if ($PID_TO_KILL -and $PID_TO_KILL -ne "0") {
                Write-Host "KILL PORT $P  PID $PID_TO_KILL" -ForegroundColor Yellow
                Stop-Process -Id ([int]$PID_TO_KILL) -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

Start-Sleep -Seconds 2

Write-Host "`n=== VÉRIFICATION PORTS APRÈS NETTOYAGE ===" -ForegroundColor Cyan
foreach ($P in $PORTS_TO_KILL) {
    $LISTEN = netstat -ano | Select-String ":$P\s" | Select-String "LISTENING"
    if ($LISTEN) {
        Write-Host "[WARN] Port $P encore LISTENING - verifier manuellement" -ForegroundColor Red
    } else {
        Write-Host "[OK]   Port $P libre" -ForegroundColor Green
    }
}

Write-Host "`n=== TOUS LES SERVEURS ARRÊTÉS ===" -ForegroundColor Green
