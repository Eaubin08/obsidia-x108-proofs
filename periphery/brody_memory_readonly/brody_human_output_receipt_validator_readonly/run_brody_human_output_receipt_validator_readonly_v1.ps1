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

$baseline = Read-Kv -Path (Join-Path $x108 "CURRENT_BRODY_OPERATOR_EXECUTION_LINE_BASELINE_FREEZE_READONLY.txt")

if ($baseline["STATUS"] -ne "BRODY_OPERATOR_EXECUTION_LINE_BASELINE_FREEZE_READONLY_V1_PASS") {
  throw "BAD_OPERATOR_LINE_BASELINE_STATUS=$($baseline["STATUS"])"
}

$dir = Join-Path $x108 "periphery\brody_memory_readonly\brody_human_output_receipt_validator_readonly"
$validatorPy = Join-Path $dir "brody_human_output_receipt_validator_readonly_v1.py"
$smokePy = Join-Path $dir "smoke_brody_human_output_receipt_validator_readonly_v1.py"

foreach ($p in @($validatorPy, $smokePy)) {
  if (!(Test-Path $p)) { throw "MISSING_FILE=$p" }
}

python -m py_compile $validatorPy
if ($LASTEXITCODE -ne 0) { throw "VALIDATOR_PY_COMPILE_FAILED" }

python -m py_compile $smokePy
if ($LASTEXITCODE -ne 0) { throw "SMOKE_PY_COMPILE_FAILED" }

python $smokePy
if ($LASTEXITCODE -ne 0) { throw "HUMAN_OUTPUT_RECEIPT_VALIDATOR_SMOKE_FAILED" }

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) { throw "VERIFY_ALL_FAILED_DURING_HUMAN_OUTPUT_RECEIPT_VALIDATOR" }

Write-Host "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_PASS"
