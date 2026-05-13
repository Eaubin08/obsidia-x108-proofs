param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$ptr = Join-Path $Root "CURRENT_BRODY_API_BRIDGE_RUNTIME_AUTHORIZATION_LEDGER_READONLY_V1.txt"

if (!(Test-Path $ptr)) {
  throw "MISSING_RUNTIME_AUTHORIZATION_LEDGER_POINTER=$ptr"
}

$kv = @{}
Get-Content $ptr | ForEach-Object {
  if ($_ -match "^\s*([^=]+)=(.*)$") {
    $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
  }
}

if ($kv["STATUS"] -ne "BRODY_API_BRIDGE_RUNTIME_AUTHORIZATION_LEDGER_READONLY_V1_PASS") {
  throw "BAD_LEDGER_STATUS=$($kv["STATUS"])"
}
if ($kv["CHAIN_OK"] -ne "true") { throw "CHAIN_OK_NOT_TRUE" }
if ($kv["RUNTIME_AUTHORIZED_ANY"] -ne "false") { throw "RUNTIME_AUTHORIZED_ANY_NOT_FALSE" }
if ($kv["RUNTIME_ENABLED_ANY"] -ne "false") { throw "RUNTIME_ENABLED_ANY_NOT_FALSE" }
if ($kv["EXECUTION_ALLOWED_ANY"] -ne "false") { throw "EXECUTION_ALLOWED_ANY_NOT_FALSE" }
if ($kv["NETWORK_EXECUTED_ANY"] -ne "false") { throw "NETWORK_EXECUTED_ANY_NOT_FALSE" }
if ($kv["API_CALL_EXECUTED_ANY"] -ne "false") { throw "API_CALL_EXECUTED_ANY_NOT_FALSE" }
if ($kv["SCRAPE_EXECUTED_ANY"] -ne "false") { throw "SCRAPE_EXECUTED_ANY_NOT_FALSE" }
if ($kv["SECRETS_PRINTED_ANY"] -ne "false") { throw "SECRETS_PRINTED_ANY_NOT_FALSE" }
if ($kv["GRAPHITI_WRITE_ANY"] -ne "false") { throw "GRAPHITI_WRITE_ANY_NOT_FALSE" }
if ($kv["GRAPHITI_INDEX_WRITE_ANY"] -ne "false") { throw "GRAPHITI_INDEX_WRITE_ANY_NOT_FALSE" }
if ($kv["NEO4J_WRITE_EXECUTED_ANY"] -ne "false") { throw "NEO4J_WRITE_EXECUTED_ANY_NOT_FALSE" }
if ($kv["MEMORY_INTAKE_ANY"] -ne "false") { throw "MEMORY_INTAKE_ANY_NOT_FALSE" }
if ($kv["MEMORY_DECISION_ANY"] -ne "false") { throw "MEMORY_DECISION_ANY_NOT_FALSE" }
if ($kv["EMITS_ACT_ANY"] -ne "false") { throw "EMITS_ACT_ANY_NOT_FALSE" }
if ($kv["EMITS_VERDICT_ANY"] -ne "false") { throw "EMITS_VERDICT_ANY_NOT_FALSE" }
if ($kv["KERNEL_MUTATION_ANY"] -ne "false") { throw "KERNEL_MUTATION_ANY_NOT_FALSE" }
if ($kv["X108_RUNTIME_BINDING_ANY"] -ne "false") { throw "X108_RUNTIME_BINDING_ANY_NOT_FALSE" }
if ($kv["X108_MERGE_ANY"] -ne "false") { throw "X108_MERGE_ANY_NOT_FALSE" }
if ($kv["DECISION_AUTHORITY"] -ne "KX108_ONLY") { throw "BAD_DECISION_AUTHORITY=$($kv["DECISION_AUTHORITY"])" }

$smokePy = $kv["SMOKE_PY"]
$ledgerDir = $kv["LEDGER_DIR"]

if (!(Test-Path $smokePy)) { throw "MISSING_SMOKE_PY=$smokePy" }
if (!(Test-Path $ledgerDir)) { throw "MISSING_LEDGER_DIR=$ledgerDir" }

Push-Location $ledgerDir
try {
  python $smokePy
}
finally {
  Pop-Location
}

Write-Host "BRODY_API_BRIDGE_RUNTIME_AUTHORIZATION_LEDGER_READONLY_V1_PASS"
