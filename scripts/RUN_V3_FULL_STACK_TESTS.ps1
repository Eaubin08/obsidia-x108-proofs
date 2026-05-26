# RUN_V3_FULL_STACK_TESTS.ps1 — Obsidia X-108 Patch V3
# Full stack test suite: periphery + non_sovereignty + integration
# No kernel modification. No real action. Dry-run only.

Write-Host "=== OBSIDIA X-108 V3 FULL STACK TESTS ===" -ForegroundColor Cyan
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

# Compile check
Write-Host "`n[STEP 1] Python compile check..." -ForegroundColor Yellow
python -m compileall periphery -q
if ($LASTEXITCODE -ne 0) { Write-Host "COMPILE FAIL" -ForegroundColor Red; exit 1 }
Write-Host "PY_COMPILE_PASS" -ForegroundColor Green

# Periphery tests
Write-Host "`n[STEP 2] Periphery tests..." -ForegroundColor Yellow
python -m pytest tests/periphery -v --tb=short
if ($LASTEXITCODE -ne 0) { Write-Host "PERIPHERY_TESTS_FAIL" -ForegroundColor Red; exit 1 }
Write-Host "PERIPHERY_TESTS_PASS" -ForegroundColor Green

# Non-sovereignty tests
Write-Host "`n[STEP 3] Non-sovereignty tests..." -ForegroundColor Yellow
python -m pytest tests/non_sovereignty -v --tb=short
if ($LASTEXITCODE -ne 0) { Write-Host "NON_SOVEREIGNTY_FAIL" -ForegroundColor Red; exit 1 }
Write-Host "NON_SOVEREIGNTY_PASS" -ForegroundColor Green

# Integration tests
Write-Host "`n[STEP 4] Integration tests..." -ForegroundColor Yellow
python -m pytest tests/integration -v --tb=short
if ($LASTEXITCODE -ne 0) { Write-Host "INTEGRATION_TESTS_FAIL" -ForegroundColor Red; exit 1 }
Write-Host "INTEGRATION_TESTS_PASS" -ForegroundColor Green

# Kernel untouched check
Write-Host "`n[STEP 5] Kernel untouched check..." -ForegroundColor Yellow
$diffs = @(
    "sigma/guard.py",
    "sigma/contracts.py",
    "sigma/protocols.py",
    "sigma/aggregation.py",
    "proofs/lean",
    "formal/tla",
    "merkle_seal.json"
)
$dirty = $false
foreach ($d in $diffs) {
    $out = git diff -- $d 2>&1
    if ($out) { Write-Host "DIFF DETECTED: $d" -ForegroundColor Red; $dirty = $true }
}
if ($dirty) { Write-Host "KERNEL_UNTOUCHED_FAIL" -ForegroundColor Red; exit 1 }
Write-Host "KERNEL_UNTOUCHED_PASS" -ForegroundColor Green

Write-Host "`n=== ALL V3 TESTS PASS ===" -ForegroundColor Cyan
