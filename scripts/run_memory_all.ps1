# V5A — Run Memory / Brody / Graphiti Internal Flow
# Dry-run only. No memory write. No decision.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "`n=== V5A Internal Flow Runner: Memory / Brody / Graphiti ===" -ForegroundColor Cyan

Write-Host "`n[1/1] memory_brody_graphiti_flow..." -ForegroundColor Yellow
python -m demos.local_flows.memory_brody_graphiti_flow
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`nOK Memory / Brody / Graphiti flow passed." -ForegroundColor Green
