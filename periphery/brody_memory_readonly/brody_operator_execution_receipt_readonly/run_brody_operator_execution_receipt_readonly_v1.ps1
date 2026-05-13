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

$protocol = Read-Kv -Path (Join-Path $x108 "CURRENT_BRODY_OPERATOR_EXECUTION_PROTOCOL_READONLY.txt")

if ($protocol["STATUS"] -ne "BRODY_OPERATOR_EXECUTION_PROTOCOL_READONLY_V1_PASS") {
  throw "BAD_OPERATOR_PROTOCOL_STATUS=$($protocol["STATUS"])"
}

if (!(Test-Path $protocol["RUN_PS1"])) {
  throw "MISSING_OPERATOR_PROTOCOL_RUNNER=$($protocol["RUN_PS1"])"
}

powershell -NoProfile -ExecutionPolicy Bypass -File $protocol["RUN_PS1"] -Root $Root
if ($LASTEXITCODE -ne 0) {
  throw "OPERATOR_PROTOCOL_FAILED_DURING_RECEIPT"
}

$receiptJson = Join-Path $x108 "periphery\brody_memory_readonly\brody_operator_execution_receipt_readonly\BRODY_OPERATOR_EXECUTION_RECEIPT_READONLY_V1.json"

if (!(Test-Path $receiptJson)) {
  throw "MISSING_RECEIPT_JSON=$receiptJson"
}

$receipt = Get-Content $receiptJson -Raw | ConvertFrom-Json

if ($receipt.status -ne "BRODY_OPERATOR_EXECUTION_RECEIPT_READONLY_V1_PASS") {
  throw "BAD_RECEIPT_STATUS=$($receipt.status)"
}

if ($receipt.receipt_schema_only -ne $true) { throw "RECEIPT_SCHEMA_ONLY_NOT_TRUE" }
if ($receipt.actual_execution_receipt_present -ne $false) { throw "ACTUAL_EXECUTION_RECEIPT_PRESENT_NOT_FALSE" }
if ($receipt.human_output_pasted -ne $false) { throw "HUMAN_OUTPUT_PASTED_NOT_FALSE" }
if ($receipt.command_executed -ne $false) { throw "COMMAND_EXECUTED_NOT_FALSE" }
if ($receipt.execution_claimed -ne $false) { throw "EXECUTION_CLAIMED_NOT_FALSE" }
if ($receipt.execution_verified -ne $false) { throw "EXECUTION_VERIFIED_NOT_FALSE" }
if ($receipt.brody_execute_allowed -ne $false) { throw "BRODY_EXECUTE_ALLOWED_NOT_FALSE" }
if ($receipt.brody_authorize_allowed -ne $false) { throw "BRODY_AUTHORIZE_ALLOWED_NOT_FALSE" }
if ($receipt.human_operator_required -ne $true) { throw "HUMAN_OPERATOR_REQUIRED_NOT_TRUE" }
if ($receipt.memory_decision -ne $false) { throw "MEMORY_DECISION_NOT_FALSE" }
if ($receipt.allowed_to_decide -ne $false) { throw "ALLOWED_TO_DECIDE_NOT_FALSE" }
if ($receipt.emits_act -ne $false) { throw "EMITS_ACT_NOT_FALSE" }
if ($receipt.emits_verdict -ne $false) { throw "EMITS_VERDICT_NOT_FALSE" }
if ($receipt.decision_authority -ne "KX108_ONLY") { throw "BAD_DECISION_AUTHORITY=$($receipt.decision_authority)" }
if ($receipt.kernel_mutation -ne $false) { throw "KERNEL_MUTATION_NOT_FALSE" }
if ($receipt.x108_runtime_binding -ne $false) { throw "X108_RUNTIME_BINDING_NOT_FALSE" }
if ($receipt.x108_merge -ne $false) { throw "X108_MERGE_NOT_FALSE" }

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_RECEIPT"
}

Write-Host "BRODY_OPERATOR_EXECUTION_RECEIPT_READONLY_V1_PASS"
