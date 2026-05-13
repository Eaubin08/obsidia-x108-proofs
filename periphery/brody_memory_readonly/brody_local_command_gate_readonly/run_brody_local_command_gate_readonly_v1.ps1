param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$x108 = Join-Path $Root "obsidia-x108-proofs"
$ptr = Join-Path $x108 "CURRENT_BRODY_LOCAL_COMMAND_GATE_READONLY.txt"

if (!(Test-Path $x108)) { throw "MISSING_X108_REPO=$x108" }
if (!(Test-Path $ptr)) { throw "MISSING_LOCAL_COMMAND_GATE_POINTER=$ptr" }

$kv = @{}
Get-Content $ptr | ForEach-Object {
  if ($_ -match "^\s*([^=]+)=(.*)$") {
    $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
  }
}

if ($kv["STATUS"] -ne "BRODY_LOCAL_COMMAND_GATE_READONLY_V1_PASS") { throw "BAD_STATUS=$($kv["STATUS"])" }
if ($kv["BUILD_TARGET"] -ne "obsidia-x108-proofs") { throw "BAD_BUILD_TARGET=$($kv["BUILD_TARGET"])" }
if ($kv["BRODY_EXECUTE_ALLOWED"] -ne "false") { throw "BRODY_EXECUTE_ALLOWED_NOT_FALSE" }
if ($kv["COMMAND_EXECUTED"] -ne "false") { throw "COMMAND_EXECUTED_NOT_FALSE" }
if ($kv["HUMAN_OPERATOR_REQUIRED"] -ne "true") { throw "HUMAN_OPERATOR_REQUIRED_NOT_TRUE" }
if ($kv["DECISION_AUTHORITY"] -ne "KX108_ONLY") { throw "BAD_DECISION_AUTHORITY=$($kv["DECISION_AUTHORITY"])" }
if ($kv["MEMORY_DECISION"] -ne "false") { throw "MEMORY_DECISION_NOT_FALSE" }
if ($kv["ALLOWED_TO_DECIDE"] -ne "false") { throw "ALLOWED_TO_DECIDE_NOT_FALSE" }
if ($kv["EMITS_ACT"] -ne "false") { throw "EMITS_ACT_NOT_FALSE" }
if ($kv["EMITS_VERDICT"] -ne "false") { throw "EMITS_VERDICT_NOT_FALSE" }
if ($kv["KERNEL_MUTATION"] -ne "false") { throw "KERNEL_MUTATION_NOT_FALSE" }
if ($kv["X108_RUNTIME_BINDING"] -ne "false") { throw "X108_RUNTIME_BINDING_NOT_FALSE" }
if ($kv["X108_MERGE"] -ne "false") { throw "X108_MERGE_NOT_FALSE" }
if ($kv["GRAPHITI_INDEX_WRITE"] -ne "false") { throw "GRAPHITI_INDEX_WRITE_NOT_FALSE" }
if ($kv["MEMORY_INTAKE"] -ne "false") { throw "MEMORY_INTAKE_NOT_FALSE" }

$smokePy = $kv["SMOKE_PY"]
if (!(Test-Path $smokePy)) { throw "MISSING_SMOKE_PY=$smokePy" }

python $smokePy

Write-Host "BRODY_LOCAL_COMMAND_GATE_READONLY_V1_PASS"
