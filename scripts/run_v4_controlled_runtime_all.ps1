# V5A — Run All V4 Controlled Runtime Internal Flows
# No external Demo dependency.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "`n=== V5A Internal Flow Runner: V4 Controlled Runtime ===" -ForegroundColor Cyan

Write-Host "`n[1/2] v4_controlled_runtime_flow..." -ForegroundColor Yellow
python -m demos.local_flows.v4_controlled_runtime_flow
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`n[2/2] gps_full_stack_flow..." -ForegroundColor Yellow
python -m demos.local_flows.gps_full_stack_flow
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`nOK All V4 controlled runtime flows passed." -ForegroundColor Green
