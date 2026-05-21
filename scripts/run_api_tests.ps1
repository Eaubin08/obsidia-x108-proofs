# V5B — Run API + non_sovereignty tests
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "=== V5B API Tests ===" -ForegroundColor Cyan
python -m pytest tests/api -q --tb=short
Write-Host ""
Write-Host "=== Non-Sovereignty Tests ===" -ForegroundColor Cyan
python -m pytest tests/non_sovereignty -q --tb=short
