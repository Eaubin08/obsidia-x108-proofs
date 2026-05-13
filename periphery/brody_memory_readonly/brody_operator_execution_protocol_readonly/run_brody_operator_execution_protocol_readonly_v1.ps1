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

$packetClose = Read-Kv -Path (Join-Path $x108 "CURRENT_BRODY_HUMAN_COMMAND_PACKET_CLEAN_CLOSE_READONLY.txt")

if ($packetClose["STATUS"] -ne "BRODY_HUMAN_COMMAND_PACKET_CLEAN_CLOSE_READONLY_V1_PASS") {
  throw "BAD_PACKET_CLEAN_CLOSE_STATUS=$($packetClose["STATUS"])"
}

if (!(Test-Path $packetClose["RUN_PS1"])) {
  throw "MISSING_PACKET_CLEAN_CLOSE_RUNNER=$($packetClose["RUN_PS1"])"
}

powershell -NoProfile -ExecutionPolicy Bypass -File $packetClose["RUN_PS1"] -Root $Root
if ($LASTEXITCODE -ne 0) {
  throw "PACKET_CLEAN_CLOSE_FAILED_DURING_OPERATOR_PROTOCOL"
}

$protocolJson = Join-Path $x108 "periphery\brody_memory_readonly\brody_operator_execution_protocol_readonly\BRODY_OPERATOR_EXECUTION_PROTOCOL_READONLY_V1.json"

if (!(Test-Path $protocolJson)) {
  throw "MISSING_OPERATOR_PROTOCOL_JSON=$protocolJson"
}

$protocol = Get-Content $protocolJson -Raw | ConvertFrom-Json

if ($protocol.status -ne "BRODY_OPERATOR_EXECUTION_PROTOCOL_READONLY_V1_PASS") {
  throw "BAD_OPERATOR_PROTOCOL_STATUS=$($protocol.status)"
}

if ($protocol.brody_execute_allowed -ne $false) { throw "BRODY_EXECUTE_ALLOWED_NOT_FALSE" }
if ($protocol.brody_authorize_allowed -ne $false) { throw "BRODY_AUTHORIZE_ALLOWED_NOT_FALSE" }
if ($protocol.human_operator_required -ne $true) { throw "HUMAN_OPERATOR_REQUIRED_NOT_TRUE" }
if ($protocol.command_executed -ne $false) { throw "COMMAND_EXECUTED_NOT_FALSE" }
if ($protocol.memory_decision -ne $false) { throw "MEMORY_DECISION_NOT_FALSE" }
if ($protocol.allowed_to_decide -ne $false) { throw "ALLOWED_TO_DECIDE_NOT_FALSE" }
if ($protocol.emits_act -ne $false) { throw "EMITS_ACT_NOT_FALSE" }
if ($protocol.emits_verdict -ne $false) { throw "EMITS_VERDICT_NOT_FALSE" }
if ($protocol.decision_authority -ne "KX108_ONLY") { throw "BAD_DECISION_AUTHORITY=$($protocol.decision_authority)" }
if ($protocol.kernel_mutation -ne $false) { throw "KERNEL_MUTATION_NOT_FALSE" }
if ($protocol.x108_runtime_binding -ne $false) { throw "X108_RUNTIME_BINDING_NOT_FALSE" }
if ($protocol.x108_merge -ne $false) { throw "X108_MERGE_NOT_FALSE" }

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_OPERATOR_PROTOCOL"
}

Write-Host "BRODY_OPERATOR_EXECUTION_PROTOCOL_READONLY_V1_PASS"
