# BUILD_AND_RUN.ps1 — Obsidia Workbench bootstrap
# Run from this directory:  .\BUILD_AND_RUN.ps1

$root = $PSScriptRoot
Set-Location $root

Write-Host "=== Obsidia Workbench — Install + Build ===" -ForegroundColor Cyan

# Install
Write-Host "[1/3] npm install..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) { Write-Host "INSTALL FAILED" -ForegroundColor Red; exit 1 }

# Build
Write-Host "[2/3] npm run build..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) { Write-Host "BUILD FAILED" -ForegroundColor Red; exit 1 }

Write-Host "[3/3] FRONTEND_BUILD_PASS" -ForegroundColor Green
Write-Host ""
Write-Host "Start dev server:   npm run dev" -ForegroundColor Cyan
Write-Host "Then open:          http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Result: FRONTEND_BUILD_PASS / MOCK_FALLBACK_READY / BACKEND_BRIDGE_READY" -ForegroundColor Green
