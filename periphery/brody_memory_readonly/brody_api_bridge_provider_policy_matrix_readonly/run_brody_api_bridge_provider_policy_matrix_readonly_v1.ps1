param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$ptr = Join-Path $Root "CURRENT_BRODY_API_BRIDGE_PROVIDER_POLICY_MATRIX_READONLY_V1.txt"

if (!(Test-Path $ptr)) {
  throw "MISSING_PROVIDER_POLICY_MATRIX_POINTER=$ptr"
}

$kv = @{}
Get-Content $ptr | ForEach-Object {
  if ($_ -match "^\s*([^=]+)=(.*)$") {
    $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
  }
}

if ($kv["STATUS"] -ne "BRODY_API_BRIDGE_PROVIDER_POLICY_MATRIX_READONLY_V1_PASS") {
  throw "BAD_POLICY_MATRIX_STATUS=$($kv["STATUS"])"
}
if ($kv["MATRIX_ENABLED"] -ne "false") { throw "MATRIX_ENABLED_NOT_FALSE" }
if ($kv["ALL_CELLS_BLOCKED"] -ne "true") { throw "ALL_CELLS_BLOCKED_NOT_TRUE" }
if ($kv["NETWORK_ALLOWED_ANY"] -ne "false") { throw "NETWORK_ALLOWED_ANY_NOT_FALSE" }
if ($kv["API_CALL_ALLOWED_ANY"] -ne "false") { throw "API_CALL_ALLOWED_ANY_NOT_FALSE" }
if ($kv["SCRAPE_ALLOWED_ANY"] -ne "false") { throw "SCRAPE_ALLOWED_ANY_NOT_FALSE" }
if ($kv["SECRETS_ALLOWED_ANY"] -ne "false") { throw "SECRETS_ALLOWED_ANY_NOT_FALSE" }
if ($kv["GRAPHITI_WRITE_ALLOWED_ANY"] -ne "false") { throw "GRAPHITI_WRITE_ALLOWED_ANY_NOT_FALSE" }
if ($kv["MEMORY_INTAKE_ALLOWED_ANY"] -ne "false") { throw "MEMORY_INTAKE_ALLOWED_ANY_NOT_FALSE" }
if ($kv["MEMORY_DECISION_ALLOWED_ANY"] -ne "false") { throw "MEMORY_DECISION_ALLOWED_ANY_NOT_FALSE" }
if ($kv["EMITS_ACT_ALLOWED_ANY"] -ne "false") { throw "EMITS_ACT_ALLOWED_ANY_NOT_FALSE" }
if ($kv["EMITS_VERDICT_ALLOWED_ANY"] -ne "false") { throw "EMITS_VERDICT_ALLOWED_ANY_NOT_FALSE" }
if ($kv["X108_RUNTIME_BINDING_ALLOWED_ANY"] -ne "false") { throw "X108_RUNTIME_BINDING_ALLOWED_ANY_NOT_FALSE" }
if ($kv["KERNEL_MUTATION_ALLOWED_ANY"] -ne "false") { throw "KERNEL_MUTATION_ALLOWED_ANY_NOT_FALSE" }
if ($kv["X108_MERGE_ALLOWED_ANY"] -ne "false") { throw "X108_MERGE_ALLOWED_ANY_NOT_FALSE" }
if ($kv["DECISION_AUTHORITY"] -ne "KX108_ONLY") { throw "BAD_DECISION_AUTHORITY=$($kv["DECISION_AUTHORITY"])" }

$smokePy = $kv["SMOKE_PY"]
$matrixDir = $kv["MATRIX_DIR"]

if (!(Test-Path $smokePy)) { throw "MISSING_SMOKE_PY=$smokePy" }
if (!(Test-Path $matrixDir)) { throw "MISSING_MATRIX_DIR=$matrixDir" }

Push-Location $matrixDir
try {
  python $smokePy
}
finally {
  Pop-Location
}

Write-Host "BRODY_API_BRIDGE_PROVIDER_POLICY_MATRIX_READONLY_V1_PASS"
