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

$validator = Read-Kv -Path (Join-Path $x108 "CURRENT_BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY.txt")

if ($validator["STATUS"] -ne "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_PASS") {
  throw "BAD_HUMAN_OUTPUT_RECEIPT_VALIDATOR_STATUS=$($validator["STATUS"])"
}

if (!(Test-Path $validator["RUN_PS1"])) {
  throw "MISSING_VALIDATOR_RUNNER=$($validator["RUN_PS1"])"
}

powershell -NoProfile -ExecutionPolicy Bypass -File $validator["RUN_PS1"] -Root $Root
if ($LASTEXITCODE -ne 0) {
  throw "HUMAN_OUTPUT_RECEIPT_VALIDATOR_FAILED_DURING_CLEAN_CLOSE"
}

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_HUMAN_OUTPUT_VALIDATOR_CLEAN_CLOSE"
}

Write-Host "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_CLEAN_CLOSE_READONLY_V1_PASS"
