param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$ptr = Join-Path $Root "CURRENT_BRODY_API_BRIDGE_CANDIDATE_DRIFT_GUARD_READONLY_V1.txt"

if (!(Test-Path $ptr)) {
  throw "MISSING_DRIFT_GUARD_POINTER=$ptr"
}

$kv = @{}
Get-Content $ptr | ForEach-Object {
  if ($_ -match "^\s*([^=]+)=(.*)$") {
    $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
  }
}

if ($kv["STATUS"] -ne "BRODY_API_BRIDGE_CANDIDATE_DRIFT_GUARD_READONLY_V1_PASS") {
  throw "BAD_DRIFT_GUARD_STATUS=$($kv["STATUS"])"
}

if ($kv["DRIFT_COUNT"] -ne "0") { throw "DRIFT_COUNT_NOT_ZERO=$($kv["DRIFT_COUNT"])" }
if ($kv["CANDIDATE_SIDE_UNTRACKED"] -ne "true") { throw "CANDIDATE_SIDE_UNTRACKED_NOT_TRUE" }
if ($kv["PROOF_SIDE_POINTER_ONLY"] -ne "true") { throw "PROOF_SIDE_POINTER_ONLY_NOT_TRUE" }
if ($kv["DECISION_AUTHORITY"] -ne "KX108_ONLY") { throw "BAD_DECISION_AUTHORITY=$($kv["DECISION_AUTHORITY"])" }

Write-Host "BRODY_API_BRIDGE_CANDIDATE_DRIFT_GUARD_READONLY_V1_PASS"
