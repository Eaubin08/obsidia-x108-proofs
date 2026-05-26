# V5B — Start Workbench with API backend
# 1. Start Obsidia API on 8000 (background)
# 2. Start Workbench on 5173 (foreground)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "=== Obsidia X-108 V5B — Workbench + API ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting API backend on http://127.0.0.1:8000 ..." -ForegroundColor Yellow
Start-Process -NoNewWindow python -ArgumentList "-m", "uvicorn", "apps.obsidia_api.main:app", "--host", "127.0.0.1", "--port", "8000"

Start-Sleep -Seconds 3

Write-Host "Starting Workbench on http://127.0.0.1:5173 ..." -ForegroundColor Yellow
Set-Location apps/obsidia-workbench
npm run dev
