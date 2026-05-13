param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$x108 = Join-Path $Root "obsidia-x108-proofs"
$repairV3Ptr = Join-Path $x108 "CURRENT_BRODY_LOCAL_COMMAND_GATE_READONLY_REPAIR_V3.txt"

if (!(Test-Path $repairV3Ptr)) {
  throw "MISSING_REPAIR_V3_POINTER=$repairV3Ptr"
}

$kv = @{}
Get-Content $repairV3Ptr | ForEach-Object {
  if ($_ -match "^\s*([^=]+)=(.*)$") {
    $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
  }
}

if ($kv["STATUS"] -ne "BRODY_LOCAL_COMMAND_GATE_READONLY_V1_REPAIR_V3_PASS") {
  throw "BAD_REPAIR_V3_STATUS=$($kv["STATUS"])"
}

if (!(Test-Path $kv["RUN_PS1"])) {
  throw "MISSING_REPAIR_V3_RUNNER=$($kv["RUN_PS1"])"
}

powershell -NoProfile -ExecutionPolicy Bypass -File $kv["RUN_PS1"] -Root $Root
if ($LASTEXITCODE -ne 0) {
  throw "REPAIR_V3_RUNNER_FAILED_DURING_CLEAN_CLOSE"
}

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_CLEAN_CLOSE"
}

Write-Host "BRODY_LOCAL_COMMAND_GATE_CLEAN_CLOSE_READONLY_V1_PASS"
