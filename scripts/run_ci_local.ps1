# V5A — Run CI checks locally
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot\..

Write-Host "`n=== X108 V5A Local CI ===" -ForegroundColor Cyan

Write-Host "`n[1/6] Python compile..." -ForegroundColor Yellow
python -m compileall periphery -q
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red } else { Write-Host "PASS" -ForegroundColor Green }

Write-Host "`n[2/6] Protected files..." -ForegroundColor Yellow
python scripts/check_protected_files.py
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red } else { Write-Host "PASS" -ForegroundColor Green }

Write-Host "`n[3/6] Forbidden content..." -ForegroundColor Yellow
python scripts/check_forbidden_content.py
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red } else { Write-Host "PASS" -ForegroundColor Green }

Write-Host "`n[4/6] Full test suite..." -ForegroundColor Yellow
python -m pytest tests/ -q --tb=short
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red } else { Write-Host "PASS" -ForegroundColor Green }

Write-Host "`n[5/6] Generate manifest..." -ForegroundColor Yellow
python scripts/generate_recursive_manifest.py
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red } else { Write-Host "PASS" -ForegroundColor Green }

Write-Host "`n[6/6] Verify manifest..." -ForegroundColor Yellow
python scripts/verify_recursive_manifest.py
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red } else { Write-Host "PASS" -ForegroundColor Green }

Write-Host "`n=== V5A Local CI Complete ===" -ForegroundColor Cyan
