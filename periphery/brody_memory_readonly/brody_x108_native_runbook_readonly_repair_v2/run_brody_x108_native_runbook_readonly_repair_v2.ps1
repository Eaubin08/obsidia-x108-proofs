param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"
$x108 = Join-Path $Root "obsidia-x108-proofs"
$runbookRunner = Join-Path $x108 "periphery\brody_memory_readonly\brody_x108_native_runbook_readonly\run_brody_x108_native_runbook_readonly_v1.ps1"

if (!(Test-Path $runbookRunner)) {
  throw "MISSING_RUNBOOK_RUNNER=$runbookRunner"
}

powershell -NoProfile -ExecutionPolicy Bypass -File $runbookRunner -Root $Root
if ($LASTEXITCODE -ne 0) {
  throw "RUNBOOK_REPAIR_V2_VALIDATION_FAILED"
}

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_RUNBOOK_REPAIR_V2"
}

Write-Host "BRODY_X108_NATIVE_RUNBOOK_READONLY_REPAIR_V2_PASS"
