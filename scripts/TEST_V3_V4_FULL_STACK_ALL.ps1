# TEST_V3_V4_FULL_STACK_ALL.ps1 — Full V3+V4 test suite
Set-Location $PSScriptRoot\..
Write-Host "=== Obsidia X-108 Full Stack V3+V4 Test Suite ===" -ForegroundColor Cyan
python -m pytest tests/ -v --tb=short
Write-Host "=== Done ===" -ForegroundColor Cyan
