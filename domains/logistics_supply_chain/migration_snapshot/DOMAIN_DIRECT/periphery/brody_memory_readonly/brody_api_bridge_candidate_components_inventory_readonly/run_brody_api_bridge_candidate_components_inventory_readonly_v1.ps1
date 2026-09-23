param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$ptr = Join-Path $Root "CURRENT_BRODY_API_BRIDGE_CANDIDATE_COMPONENTS_INVENTORY_READONLY_V1.txt"

if (!(Test-Path $ptr)) {
  throw "MISSING_CANDIDATE_COMPONENTS_INVENTORY_POINTER=$ptr"
}

$kv = @{}
Get-Content $ptr | ForEach-Object {
  if ($_ -match "^\s*([^=]+)=(.*)$") {
    $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
  }
}

if ($kv["STATUS"] -ne "BRODY_API_BRIDGE_CANDIDATE_COMPONENTS_INVENTORY_READONLY_V1_PASS") {
  throw "BAD_INVENTORY_STATUS=$($kv["STATUS"])"
}

if ($kv["CANDIDATE_SIDE_UNTRACKED"] -ne "true") { throw "CANDIDATE_SIDE_UNTRACKED_NOT_TRUE" }
if ($kv["PROOF_SIDE_POINTER_ONLY"] -ne "true") { throw "PROOF_SIDE_POINTER_ONLY_NOT_TRUE" }
if ([int]$kv["COMPONENT_COUNT"] -lt 6) { throw "COMPONENT_COUNT_TOO_LOW=$($kv["COMPONENT_COUNT"])" }
if ([int]$kv["FILE_COUNT"] -lt 12) { throw "FILE_COUNT_TOO_LOW=$($kv["FILE_COUNT"])" }

if ($kv["RUNTIME_ENABLED"] -ne "false") { throw "RUNTIME_ENABLED_NOT_FALSE" }
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

$inventoryJson = $kv["INVENTORY_JSON"]
if (!(Test-Path $inventoryJson)) {
  throw "MISSING_INVENTORY_JSON=$inventoryJson"
}

$inventory = Get-Content $inventoryJson -Raw | ConvertFrom-Json
if ($inventory.status -ne "BRODY_API_BRIDGE_CANDIDATE_COMPONENTS_INVENTORY_READONLY_V1_PASS") {
  throw "BAD_INVENTORY_JSON_STATUS=$($inventory.status)"
}

foreach ($f in $inventory.files) {
  if (!(Test-Path $f.full_path)) {
    throw "MISSING_INVENTORIED_FILE=$($f.full_path)"
  }

  $hash = (Get-FileHash $f.full_path -Algorithm SHA256).Hash
  if ($hash -ne $f.sha256) {
    throw "HASH_MISMATCH=$($f.relative_path)"
  }
}

Write-Host "BRODY_API_BRIDGE_CANDIDATE_COMPONENTS_INVENTORY_READONLY_V1_PASS"
