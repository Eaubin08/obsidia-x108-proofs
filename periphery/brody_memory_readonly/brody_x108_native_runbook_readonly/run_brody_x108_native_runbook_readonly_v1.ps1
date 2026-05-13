param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"
$x108 = Join-Path $Root "obsidia-x108-proofs"

function Read-Kv {
  param([string]$Path)

  if (!(Test-Path $Path)) {
    throw "MISSING_POINTER=$Path"
  }

  $kv = @{}
  Get-Content $Path | ForEach-Object {
    if ($_ -match "^\s*([^=]+)=(.*)$") {
      $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
    }
  }

  return $kv
}

$checks = @(
  @{ file = "CURRENT_BRODY_X108_ONLY_BUILD_MODE_READONLY.txt"; status = "BRODY_X108_ONLY_BUILD_MODE_READONLY_V1_PASS" },
  @{ file = "CURRENT_BRODY_RUNTIME_FREEZE_V1_4_12A_READONLY.txt"; status = "BRODY_RUNTIME_FREEZE_V1_4_12A_READONLY_READY" },
  @{ file = "CURRENT_BRODY_NATIVE_TERMINAL_SESSION_TEST_READONLY.txt"; status = "BRODY_NATIVE_TERMINAL_SESSION_TEST_READONLY_READY" },
  @{ file = "CURRENT_BRODY_NATIVE_TERMINAL_DETECTOR_PATCH_READONLY.txt"; status = "BRODY_NATIVE_TERMINAL_DETECTOR_PATCH_READONLY_READY" },
  @{ file = "CURRENT_MEMORY_LAYER_AUTHORITY_MODEL_READONLY.txt"; status = "MEMORY_LAYER_AUTHORITY_MODEL_READONLY_V1_PASS" },
  @{ file = "CURRENT_BRODY_X108_PROOF_STATE_FREEZE_V1.txt"; status = "BRODY_X108_PROOF_STATE_FREEZE_V1_PASS" },
  @{ file = "CURRENT_BRODY_API_BRIDGE_EXTERNAL_ACCESS_FREEZE_READONLY.txt"; status = "BRODY_API_BRIDGE_EXTERNAL_ACCESS_FREEZE_READONLY_V1_PASS" },
  @{ file = "CURRENT_BRODY_API_BRIDGE_LIVE_DRIFT_GUARD_READONLY.txt"; status = "BRODY_API_BRIDGE_LIVE_DRIFT_GUARD_READONLY_V1_PASS" },
  @{ file = "CURRENT_BRODY_LOCAL_COMMAND_GATE_CLEAN_CLOSE_READONLY.txt"; status = "BRODY_LOCAL_COMMAND_GATE_CLEAN_CLOSE_READONLY_V1_PASS" }
)

foreach ($check in $checks) {
  $path = Join-Path $x108 $check.file
  $kv = Read-Kv -Path $path

  if ($kv["STATUS"] -ne $check.status) {
    throw "BAD_STATUS_FOR_$($check.file)=$($kv["STATUS"]) EXPECTED=$($check.status)"
  }

  if ($kv["DECISION_AUTHORITY"] -and $kv["DECISION_AUTHORITY"] -ne "KX108_ONLY") {
    throw "BAD_DECISION_AUTHORITY_FOR_$($check.file)=$($kv["DECISION_AUTHORITY"])"
  }
}

$cleanClose = Read-Kv -Path (Join-Path $x108 "CURRENT_BRODY_LOCAL_COMMAND_GATE_CLEAN_CLOSE_READONLY.txt")
if (!(Test-Path $cleanClose["RUN_PS1"])) {
  throw "MISSING_CLEAN_CLOSE_RUNNER=$($cleanClose["RUN_PS1"])"
}

powershell -NoProfile -ExecutionPolicy Bypass -File $cleanClose["RUN_PS1"] -Root $Root
if ($LASTEXITCODE -ne 0) {
  throw "CLEAN_CLOSE_FAILED_DURING_RUNBOOK"
}

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_RUNBOOK"
}

Write-Host "BRODY_X108_NATIVE_RUNBOOK_READONLY_V1_PASS"
