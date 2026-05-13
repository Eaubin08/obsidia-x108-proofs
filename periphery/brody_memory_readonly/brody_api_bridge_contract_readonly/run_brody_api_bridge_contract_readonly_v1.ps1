param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$ptr = Join-Path $Root "CURRENT_BRODY_API_BRIDGE_CONTRACT_READONLY_V1.txt"

if (!(Test-Path $ptr)) {
  throw "MISSING_BRODY_API_BRIDGE_CONTRACT_POINTER=$ptr"
}

$kv = @{}
Get-Content $ptr | ForEach-Object {
  if ($_ -match "^\s*([^=]+)=(.*)$") {
    $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
  }
}

if ($kv["STATUS"] -ne "BRODY_API_BRIDGE_CONTRACT_READONLY_V1_PASS") {
  throw "BAD_CONTRACT_STATUS=$($kv["STATUS"])"
}

if ($kv["CONTRACT_MODE"] -ne "READONLY_CONTRACT_ONLY") {
  throw "BAD_CONTRACT_MODE=$($kv["CONTRACT_MODE"])"
}

if ($kv["RUNTIME_BINDING_ALLOWED"] -ne "false") {
  throw "RUNTIME_BINDING_ALLOWED_NOT_FALSE"
}

if ($kv["API_CALL_ALLOWED_NOW"] -ne "false") {
  throw "API_CALL_ALLOWED_NOW_NOT_FALSE"
}

if ($kv["SCRAPE_ALLOWED_NOW"] -ne "false") {
  throw "SCRAPE_ALLOWED_NOW_NOT_FALSE"
}

if ($kv["NETWORK_CALL_ALLOWED_NOW"] -ne "false") {
  throw "NETWORK_CALL_ALLOWED_NOW_NOT_FALSE"
}

if ($kv["SECRETS_ALLOWED_TO_PRINT"] -ne "false") {
  throw "SECRETS_ALLOWED_TO_PRINT_NOT_FALSE"
}

if ($kv["HUMAN_AUTHORIZATION_REQUIRED"] -ne "true") {
  throw "HUMAN_AUTHORIZATION_REQUIRED_NOT_TRUE"
}

if ($kv["DECISION_AUTHORITY"] -ne "KX108_ONLY") {
  throw "BAD_DECISION_AUTHORITY=$($kv["DECISION_AUTHORITY"])"
}

if ($kv["MEMORY_DECISION"] -ne "false") { throw "MEMORY_DECISION_NOT_FALSE" }
if ($kv["ALLOWED_TO_DECIDE"] -ne "false") { throw "ALLOWED_TO_DECIDE_NOT_FALSE" }
if ($kv["EMITS_ACT"] -ne "false") { throw "EMITS_ACT_NOT_FALSE" }
if ($kv["EMITS_VERDICT"] -ne "false") { throw "EMITS_VERDICT_NOT_FALSE" }
if ($kv["KERNEL_MUTATION"] -ne "false") { throw "KERNEL_MUTATION_NOT_FALSE" }
if ($kv["X108_RUNTIME_BINDING"] -ne "false") { throw "X108_RUNTIME_BINDING_NOT_FALSE" }
if ($kv["X108_MERGE"] -ne "false") { throw "X108_MERGE_NOT_FALSE" }
if ($kv["GRAPHITI_INDEX_WRITE"] -ne "false") { throw "GRAPHITI_INDEX_WRITE_NOT_FALSE" }
if ($kv["NEO4J_WRITE_EXECUTED"] -ne "false") { throw "NEO4J_WRITE_EXECUTED_NOT_FALSE" }
if ($kv["MEMORY_INTAKE"] -ne "false") { throw "MEMORY_INTAKE_NOT_FALSE" }

Write-Host "BRODY_API_BRIDGE_CONTRACT_READONLY_V1_PASS"
