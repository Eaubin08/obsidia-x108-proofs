# Brody V1.4.12A — Live Stack Health Check
# Checks: Neo4j 7688 / ObsidiaShell 8011 / Obsidia API 8000 / Workbench 5173

$ErrorActionPreference = "Continue"
$pass = $true

function Check-Port {
    param($host_, $port, $label)
    $tc = Test-NetConnection $host_ -Port $port -WarningAction SilentlyContinue
    if ($tc.TcpTestSucceeded) {
        Write-Host "  [PASS] $label ($host_:$port)" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  [FAIL] $label ($host_:$port) — port not reachable" -ForegroundColor Red
        return $false
    }
}

Write-Host ""
Write-Host "=== BRODY LIVE STACK CHECK ===" -ForegroundColor Cyan
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor DarkGray
Write-Host ""

# 1. Neo4j
Write-Host "1. Neo4j Bolt (7688):" -ForegroundColor Yellow
$neo4j = Check-Port "127.0.0.1" 7688 "Neo4j Bolt"
if (-not $neo4j) {
    Write-Host "     Restart: neo4j console  OR  net start neo4j" -ForegroundColor DarkYellow
    $pass = $false
}
Write-Host ""

# 2. ObsidiaShell
Write-Host "2. ObsidiaShell (8011):" -ForegroundColor Yellow
$shell = Check-Port "127.0.0.1" 8011 "ObsidiaShell"
if ($shell) {
    try {
        $r = Invoke-RestMethod "http://127.0.0.1:8011/graph/v20/frozen/status" -TimeoutSec 5
        Write-Host "     status: $($r.status ?? 'OK')" -ForegroundColor Green
    } catch {
        Write-Host "     /graph/v20/frozen/status → error: $_" -ForegroundColor DarkYellow
    }
} else {
    Write-Host "     Restart: python -m uvicorn obsidia_shell.main:app --port 8011 --reload" -ForegroundColor DarkYellow
    $pass = $false
}
Write-Host ""

# 3. Obsidia API
Write-Host "3. Obsidia API (8000):" -ForegroundColor Yellow
$api = Check-Port "127.0.0.1" 8000 "Obsidia API"
if ($api) {
    try {
        $r = Invoke-RestMethod "http://127.0.0.1:8012/api/status" -TimeoutSec 5
        Write-Host "     status: $($r.status ?? 'OK') | version: $($r.version ?? 'V5B')" -ForegroundColor Green
    } catch {
        Write-Host "     /api/status → error: $_" -ForegroundColor DarkYellow
    }
} else {
    Write-Host "     Restart: .\scripts\run_obsidia_api.ps1" -ForegroundColor DarkYellow
    $pass = $false
}
Write-Host ""

# 4. Workbench
Write-Host "4. Workbench (5173):" -ForegroundColor Yellow
$wb = Check-Port "127.0.0.1" 5173 "Workbench Vite"
if (-not $wb) {
    Write-Host "     Launch: .\scripts\run_workbench_with_api.ps1" -ForegroundColor DarkYellow
    Write-Host "     (workbench offline is non-blocking for API tests)" -ForegroundColor DarkGray
}
Write-Host ""

# Final verdict
Write-Host "=== RESULT ===" -ForegroundColor Cyan
if ($pass) {
    Write-Host "BRODY_LIVE_STACK_CHECK_PASS" -ForegroundColor Green
} else {
    Write-Host "BRODY_LIVE_STACK_CHECK_PARTIAL — see FAIL lines above" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Services offline is expected in test-only mode." -ForegroundColor DarkGray
    Write-Host "API tests (pytest) use FastAPI TestClient and do NOT require live services." -ForegroundColor DarkGray
}
Write-Host ""
