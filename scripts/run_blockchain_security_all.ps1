# V5A — Run Blockchain Security Dry-Run Internal Flow
# All blockchain operations are simulated. No real chain interaction.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "`n=== V5A Internal Flow Runner: Blockchain Security Dry-Run ===" -ForegroundColor Cyan

Write-Host "`n[1/1] blockchain_security_dryrun_flow..." -ForegroundColor Yellow
python -m demos.local_flows.blockchain_security_dryrun_flow
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`nOK Blockchain security flow passed." -ForegroundColor Green
