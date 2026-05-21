# V5A — Run World Call Gateway Internal Flow
# Dry-run only. No Sovereign Ticket = No World Call.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "`n=== V5A Internal Flow Runner: World Call Gateway ===" -ForegroundColor Cyan

Write-Host "`n[1/1] world_call_gateway_flow..." -ForegroundColor Yellow
python -m demos.local_flows.world_call_gateway_flow
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`nOK World Call Gateway flow passed." -ForegroundColor Green
