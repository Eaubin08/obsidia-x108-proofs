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

$checks = @(
  @{ file = "CURRENT_BRODY_HUMAN_COMMAND_PACKET_CLEAN_CLOSE_READONLY.txt"; status = "BRODY_HUMAN_COMMAND_PACKET_CLEAN_CLOSE_READONLY_V1_PASS" },
  @{ file = "CURRENT_BRODY_OPERATOR_EXECUTION_PROTOCOL_READONLY.txt"; status = "BRODY_OPERATOR_EXECUTION_PROTOCOL_READONLY_V1_PASS" },
  @{ file = "CURRENT_BRODY_OPERATOR_EXECUTION_RECEIPT_CLEAN_CLOSE_READONLY.txt"; status = "BRODY_OPERATOR_EXECUTION_RECEIPT_CLEAN_CLOSE_READONLY_V1_PASS" },
  @{ file = "CURRENT_BRODY_OPERATOR_EXECUTION_LINE_BASELINE_FREEZE_READONLY.txt"; status = "BRODY_OPERATOR_EXECUTION_LINE_BASELINE_FREEZE_READONLY_V1_PASS" },
  @{ file = "CURRENT_BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY.txt"; status = "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_PASS" },
  @{ file = "CURRENT_BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_CLEAN_CLOSE_READONLY.txt"; status = "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_CLEAN_CLOSE_READONLY_V1_PASS" }
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

$validatorClose = Read-Kv -Path (Join-Path $x108 "CURRENT_BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_CLEAN_CLOSE_READONLY.txt")

if (!(Test-Path $validatorClose["RUN_PS1"])) {
  throw "MISSING_VALIDATOR_CLEAN_CLOSE_RUNNER=$($validatorClose["RUN_PS1"])"
}

powershell -NoProfile -ExecutionPolicy Bypass -File $validatorClose["RUN_PS1"] -Root $Root
if ($LASTEXITCODE -ne 0) {
  throw "VALIDATOR_CLEAN_CLOSE_FAILED_DURING_OUTPUT_BASELINE"
}

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_OUTPUT_BASELINE"
}

Write-Host "BRODY_OPERATOR_OUTPUT_VALIDATION_LINE_BASELINE_FREEZE_READONLY_V1_PASS"
