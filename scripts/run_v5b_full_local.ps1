# V5B — Run full local stack
# API (8000) + Workbench (5173) + Graphiti check (8011)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "=== Obsidia X-108 V5B Full Local Stack ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Starting Obsidia API on http://127.0.0.1:8012 ..." -ForegroundColor Yellow
Start-Process -NoNewWindow python -ArgumentList "-m", "uvicorn", "apps.obsidia_api.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"
Start-Sleep -Seconds 2

Write-Host "[2/3] Graphiti check (8011)..." -ForegroundColor Yellow
try {
    $r = Invoke-RestMethod -Uri "http://127.0.0.1:8011/graph/v20/frozen/status" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  Graphiti V20: LIVE (frozen readonly)" -ForegroundColor Green
} catch {
    Write-Host "  Graphiti V20: OFFLINE (mock fallback active)" -ForegroundColor DarkYellow
}

Write-Host "[3/3] Starting Workbench on http://127.0.0.1:5173 ..." -ForegroundColor Yellow
Set-Location apps/obsidia-workbench
Write-Host "  Open: http://127.0.0.1:5173" -ForegroundColor Green
npm run dev -- --host 127.0.0.1
