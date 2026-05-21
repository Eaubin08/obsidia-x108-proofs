# V5A — Run All V3/V4 Full Stack Internal Flows
# No external Demo dependency. All flows run from within obsidia-x108-proofs.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "`n=== V5A Internal Flow Runner: V3/V4 Full Stack ===" -ForegroundColor Cyan

Write-Host "`n[1/3] v3_v4_full_stack_flow..." -ForegroundColor Yellow
python -m demos.local_flows.v3_v4_full_stack_flow
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`n[2/3] bank_full_stack_flow..." -ForegroundColor Yellow
python -m demos.local_flows.bank_full_stack_flow
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`n[3/3] trading_full_stack_flow..." -ForegroundColor Yellow
python -m demos.local_flows.trading_full_stack_flow
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`nOK All V3/V4 full stack flows passed." -ForegroundColor Green
