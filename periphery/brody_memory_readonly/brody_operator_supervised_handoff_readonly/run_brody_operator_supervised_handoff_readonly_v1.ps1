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

$ioLoop = Read-Kv -Path (Join-Path $x108 "CURRENT_BRODY_OPERATOR_IO_LOOP_CLEAN_CLOSE_READONLY.txt")

if ($ioLoop["STATUS"] -ne "BRODY_OPERATOR_IO_LOOP_CLEAN_CLOSE_READONLY_V1_PASS") {
  throw "BAD_IO_LOOP_CLEAN_CLOSE_STATUS=$($ioLoop["STATUS"])"
}

if (!(Test-Path $ioLoop["RUN_PS1"])) {
  throw "MISSING_IO_LOOP_CLEAN_CLOSE_RUNNER=$($ioLoop["RUN_PS1"])"
}

powershell -NoProfile -ExecutionPolicy Bypass -File $ioLoop["RUN_PS1"] -Root $Root
if ($LASTEXITCODE -ne 0) {
  throw "IO_LOOP_CLEAN_CLOSE_FAILED_DURING_SUPERVISED_HANDOFF"
}

$handoffJson = Join-Path $x108 "periphery\brody_memory_readonly\brody_operator_supervised_handoff_readonly\BRODY_OPERATOR_SUPERVISED_HANDOFF_READONLY_V1.json"

if (!(Test-Path $handoffJson)) {
  throw "MISSING_HANDOFF_JSON=$handoffJson"
}

$handoff = Get-Content $handoffJson -Raw | ConvertFrom-Json

if ($handoff.status -ne "BRODY_OPERATOR_SUPERVISED_HANDOFF_READONLY_V1_PASS") { throw "BAD_HANDOFF_STATUS=$($handoff.status)" }
if ($handoff.brody_execute_allowed -ne $false) { throw "BRODY_EXECUTE_ALLOWED_NOT_FALSE" }
if ($handoff.brody_authorize_allowed -ne $false) { throw "BRODY_AUTHORIZE_ALLOWED_NOT_FALSE" }
if ($handoff.human_operator_required -ne $true) { throw "HUMAN_OPERATOR_REQUIRED_NOT_TRUE" }
if ($handoff.command_executed -ne $false) { throw "COMMAND_EXECUTED_NOT_FALSE" }
if ($handoff.execution_verified -ne $false) { throw "EXECUTION_VERIFIED_NOT_FALSE" }
if ($handoff.memory_decision -ne $false) { throw "MEMORY_DECISION_NOT_FALSE" }
if ($handoff.allowed_to_decide -ne $false) { throw "ALLOWED_TO_DECIDE_NOT_FALSE" }
if ($handoff.emits_act -ne $false) { throw "EMITS_ACT_NOT_FALSE" }
if ($handoff.emits_verdict -ne $false) { throw "EMITS_VERDICT_NOT_FALSE" }
if ($handoff.decision_authority -ne "KX108_ONLY") { throw "BAD_DECISION_AUTHORITY=$($handoff.decision_authority)" }
if ($handoff.kernel_mutation -ne $false) { throw "KERNEL_MUTATION_NOT_FALSE" }
if ($handoff.x108_runtime_binding -ne $false) { throw "X108_RUNTIME_BINDING_NOT_FALSE" }
if ($handoff.x108_merge -ne $false) { throw "X108_MERGE_NOT_FALSE" }

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_SUPERVISED_HANDOFF"
}

Write-Host "BRODY_OPERATOR_SUPERVISED_HANDOFF_READONLY_V1_PASS"
