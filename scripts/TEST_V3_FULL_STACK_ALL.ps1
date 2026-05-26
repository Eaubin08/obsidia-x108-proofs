# TEST_V3_FULL_STACK_ALL.ps1
# Master test runner for V3+V4 full stack.
# Runs all test suites: periphery, non_sovereignty, integration.

Write-Host "=== Obsidia X-108 — V3+V4 Full Stack Master Test Run ===" -ForegroundColor Cyan
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

Set-Location $PSScriptRoot

$failed = @()

function Run-Suite {
    param([string]$name, [string]$path)
    Write-Host "`n--- $name ---" -ForegroundColor Yellow
    python -m pytest $path -v --tb=short
    if ($LASTEXITCODE -ne 0) {
        $script:failed += $name
        Write-Host "  SUITE FAILED: $name" -ForegroundColor Red
    } else {
        Write-Host "  SUITE PASSED: $name" -ForegroundColor Green
    }
}

Run-Suite "Periphery Tests" "tests/periphery/"
Run-Suite "Non-Sovereignty Tests" "tests/non_sovereignty/"
Run-Suite "Integration Tests (V3+V4)" "tests/integration/"

Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
if ($failed.Count -eq 0) {
    Write-Host "ALL SUITES PASSED" -ForegroundColor Green
} else {
    Write-Host "FAILED SUITES:" -ForegroundColor Red
    $failed | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

Write-Host "`nX-108 sovereignty invariants verified:" -ForegroundColor Cyan
Write-Host "  can_emit_act=False | dry_run_only=True | egress_allowed=False | memory_write_allowed=False" -ForegroundColor Gray
