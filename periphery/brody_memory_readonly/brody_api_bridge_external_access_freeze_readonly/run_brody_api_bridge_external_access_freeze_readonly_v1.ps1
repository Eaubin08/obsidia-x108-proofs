param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$ptr = Join-Path $Root "CURRENT_BRODY_API_BRIDGE_EXTERNAL_ACCESS_FREEZE_READONLY_V1.txt"

if (!(Test-Path $ptr)) {
  throw "MISSING_EXTERNAL_ACCESS_FREEZE_POINTER=$ptr"
}

$kv = @{}
Get-Content $ptr | ForEach-Object {
  if ($_ -match "^\s*([^=]+)=(.*)$") {
    $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
  }
}

if ($kv["STATUS"] -ne "BRODY_API_BRIDGE_EXTERNAL_ACCESS_FREEZE_READONLY_V1_PASS") {
  throw "BAD_EXTERNAL_ACCESS_FREEZE_STATUS=$($kv["STATUS"])"
}
if ($kv["RUNTIME_ENABLED"] -ne "false") { throw "RUNTIME_ENABLED_NOT_FALSE" }
if ($kv["RUNTIME_AUTHORIZED"] -ne "false") { throw "RUNTIME_AUTHORIZED_NOT_FALSE" }
if ($kv["RUNTIME_BINDING_ALLOWED"] -ne "false") { throw "RUNTIME_BINDING_ALLOWED_NOT_FALSE" }
if ($kv["EXTERNAL_ACCESS_ENABLED"] -ne "false") { throw "EXTERNAL_ACCESS_ENABLED_NOT_FALSE" }
if ($kv["NETWORK_EXECUTED"] -ne "false") { throw "NETWORK_EXECUTED_NOT_FALSE" }
if ($kv["API_CALL_EXECUTED"] -ne "false") { throw "API_CALL_EXECUTED_NOT_FALSE" }
if ($kv["SCRAPE_EXECUTED"] -ne "false") { throw "SCRAPE_EXECUTED_NOT_FALSE" }
if ($kv["SECRETS_PRINTED"] -ne "false") { throw "SECRETS_PRINTED_NOT_FALSE" }
if ($kv["GRAPHITI_WRITE"] -ne "false") { throw "GRAPHITI_WRITE_NOT_FALSE" }
if ($kv["GRAPHITI_INDEX_WRITE"] -ne "false") { throw "GRAPHITI_INDEX_WRITE_NOT_FALSE" }
if ($kv["NEO4J_WRITE_EXECUTED"] -ne "false") { throw "NEO4J_WRITE_EXECUTED_NOT_FALSE" }
if ($kv["MEMORY_INTAKE"] -ne "false") { throw "MEMORY_INTAKE_NOT_FALSE" }
if ($kv["MEMORY_DECISION"] -ne "false") { throw "MEMORY_DECISION_NOT_FALSE" }
if ($kv["ALLOWED_TO_DECIDE"] -ne "false") { throw "ALLOWED_TO_DECIDE_NOT_FALSE" }
if ($kv["EMITS_ACT"] -ne "false") { throw "EMITS_ACT_NOT_FALSE" }
if ($kv["EMITS_VERDICT"] -ne "false") { throw "EMITS_VERDICT_NOT_FALSE" }
if ($kv["DECISION_AUTHORITY"] -ne "KX108_ONLY") { throw "BAD_DECISION_AUTHORITY=$($kv["DECISION_AUTHORITY"])" }
if ($kv["KERNEL_MUTATION"] -ne "false") { throw "KERNEL_MUTATION_NOT_FALSE" }
if ($kv["X108_RUNTIME_BINDING"] -ne "false") { throw "X108_RUNTIME_BINDING_NOT_FALSE" }
if ($kv["X108_MERGE"] -ne "false") { throw "X108_MERGE_NOT_FALSE" }

$smokePy = $kv["SMOKE_PY"]
$freezeDir = $kv["FREEZE_DIR"]

if (!(Test-Path $smokePy)) { throw "MISSING_SMOKE_PY=$smokePy" }
if (!(Test-Path $freezeDir)) { throw "MISSING_FREEZE_DIR=$freezeDir" }

Push-Location $freezeDir
try {
  python $smokePy
}
finally {
  Pop-Location
}

Write-Host "BRODY_API_BRIDGE_EXTERNAL_ACCESS_FREEZE_READONLY_V1_PASS"
