param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$ptr = Join-Path $Root "CURRENT_BRODY_API_BRIDGE_BUILD_EPOCH_OPEN_READONLY_V1.txt"

if (!(Test-Path $ptr)) {
  throw "MISSING_BUILD_EPOCH_POINTER=$ptr"
}

$kv = @{}
Get-Content $ptr | ForEach-Object {
  if ($_ -match "^\s*([^=]+)=(.*)$") {
    $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
  }
}

if ($kv["STATUS"] -ne "BRODY_API_BRIDGE_BUILD_EPOCH_OPEN_READONLY_V1_PASS") {
  throw "BAD_BUILD_EPOCH_STATUS=$($kv["STATUS"])"
}

if ($kv["BUILD_EPOCH_OPEN"] -ne "true") { throw "BUILD_EPOCH_OPEN_NOT_TRUE" }
if ($kv["MUTABLE_CANDIDATE_BUILD_ALLOWED"] -ne "true") { throw "MUTABLE_CANDIDATE_BUILD_ALLOWED_NOT_TRUE" }
if ($kv["PROOF_FREEZE_REMAINS_VALID"] -ne "true") { throw "PROOF_FREEZE_REMAINS_VALID_NOT_TRUE" }
if ($kv["RERUN_LIVE_DRIFT_GUARD_BEFORE_CLAIM"] -ne "true") { throw "RERUN_LIVE_DRIFT_GUARD_BEFORE_CLAIM_NOT_TRUE" }
if ($kv["RUNTIME_ENABLED"] -ne "false") { throw "RUNTIME_ENABLED_NOT_FALSE" }
if ($kv["EXTERNAL_ACCESS_ENABLED"] -ne "false") { throw "EXTERNAL_ACCESS_ENABLED_NOT_FALSE" }
if ($kv["MEMORY_DECISION"] -ne "false") { throw "MEMORY_DECISION_NOT_FALSE" }
if ($kv["ALLOWED_TO_DECIDE"] -ne "false") { throw "ALLOWED_TO_DECIDE_NOT_FALSE" }
if ($kv["EMITS_ACT"] -ne "false") { throw "EMITS_ACT_NOT_FALSE" }
if ($kv["EMITS_VERDICT"] -ne "false") { throw "EMITS_VERDICT_NOT_FALSE" }
if ($kv["DECISION_AUTHORITY"] -ne "KX108_ONLY") { throw "BAD_DECISION_AUTHORITY=$($kv["DECISION_AUTHORITY"])" }
if ($kv["KERNEL_MUTATION"] -ne "false") { throw "KERNEL_MUTATION_NOT_FALSE" }
if ($kv["X108_RUNTIME_BINDING"] -ne "false") { throw "X108_RUNTIME_BINDING_NOT_FALSE" }
if ($kv["X108_MERGE"] -ne "false") { throw "X108_MERGE_NOT_FALSE" }

Write-Host "BRODY_API_BRIDGE_BUILD_EPOCH_OPEN_READONLY_V1_PASS"
