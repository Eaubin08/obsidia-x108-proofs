param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"
$x108 = Join-Path $Root "obsidia-x108-proofs"

function Read-Kv {
  param([string]$Path)

  if (!(Test-Path $Path)) { throw "MISSING_POINTER=$Path" }

  $kv = @{}
  Get-Content $Path | ForEach-Object {
    if ($_ -match "^\s*([^=]+)=(.*)$") {
      $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
    }
  }

  return $kv
}

$runbook = Read-Kv -Path (Join-Path $x108 "CURRENT_BRODY_X108_NATIVE_RUNBOOK_READONLY.txt")
$repairV3 = Read-Kv -Path (Join-Path $x108 "CURRENT_BRODY_X108_NATIVE_RUNBOOK_READONLY_REPAIR_V3.txt")

if ($runbook["STATUS"] -ne "BRODY_X108_NATIVE_RUNBOOK_READONLY_V1_PASS") {
  throw "BAD_RUNBOOK_STATUS=$($runbook["STATUS"])"
}

if ($repairV3["STATUS"] -ne "BRODY_X108_NATIVE_RUNBOOK_READONLY_REPAIR_V3_PASS") {
  throw "BAD_REPAIR_V3_STATUS=$($repairV3["STATUS"])"
}

powershell -NoProfile -ExecutionPolicy Bypass -File $runbook["RUN_PS1"] -Root $Root
if ($LASTEXITCODE -ne 0) { throw "RUNBOOK_FAILED_DURING_CLEAN_CLOSE" }

powershell -NoProfile -ExecutionPolicy Bypass -File $repairV3["RUN_PS1"] -Root $Root
if ($LASTEXITCODE -ne 0) { throw "REPAIR_V3_FAILED_DURING_CLEAN_CLOSE" }

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) { throw "VERIFY_ALL_FAILED_DURING_CLEAN_CLOSE" }

Write-Host "BRODY_X108_NATIVE_RUNBOOK_CLEAN_CLOSE_READONLY_V1_PASS"
