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

$receipt = Read-Kv -Path (Join-Path $x108 "CURRENT_BRODY_OPERATOR_EXECUTION_RECEIPT_READONLY.txt")

if ($receipt["STATUS"] -ne "BRODY_OPERATOR_EXECUTION_RECEIPT_READONLY_V1_PASS") {
  throw "BAD_OPERATOR_EXECUTION_RECEIPT_STATUS=$($receipt["STATUS"])"
}

if (!(Test-Path $receipt["RUN_PS1"])) {
  throw "MISSING_OPERATOR_EXECUTION_RECEIPT_RUNNER=$($receipt["RUN_PS1"])"
}

powershell -NoProfile -ExecutionPolicy Bypass -File $receipt["RUN_PS1"] -Root $Root
if ($LASTEXITCODE -ne 0) {
  throw "OPERATOR_EXECUTION_RECEIPT_FAILED_DURING_CLEAN_CLOSE"
}

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_RECEIPT_CLEAN_CLOSE"
}

Write-Host "BRODY_OPERATOR_EXECUTION_RECEIPT_CLEAN_CLOSE_READONLY_V1_PASS"
