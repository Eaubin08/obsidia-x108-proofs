param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$x108 = Join-Path $Root "obsidia-x108-proofs"
$ptr = Join-Path $x108 "CURRENT_BRODY_X108_ONLY_BUILD_MODE_READONLY.txt"

if (!(Test-Path $x108)) { throw "MISSING_X108_REPO=$x108" }
if (!(Test-Path $ptr)) { throw "MISSING_X108_ONLY_BUILD_MODE_POINTER=$ptr" }

$kv = @{}
Get-Content $ptr | ForEach-Object {
  if ($_ -match "^\s*([^=]+)=(.*)$") {
    $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
  }
}

if ($kv["STATUS"] -ne "BRODY_X108_ONLY_BUILD_MODE_READONLY_V1_PASS") { throw "BAD_STATUS=$($kv["STATUS"])" }
if ($kv["BUILD_TARGET"] -ne "obsidia-x108-proofs") { throw "BAD_BUILD_TARGET=$($kv["BUILD_TARGET"])" }
if ($kv["CANDIDATE_BUILD_TARGET"] -ne "false") { throw "CANDIDATE_BUILD_TARGET_NOT_FALSE" }
if ($kv["X108_PROOF_NATIVE_BUILD"] -ne "true") { throw "X108_PROOF_NATIVE_BUILD_NOT_TRUE" }
if ($kv["DECISION_AUTHORITY"] -ne "KX108_ONLY") { throw "BAD_DECISION_AUTHORITY=$($kv["DECISION_AUTHORITY"])" }

Write-Host "BRODY_X108_ONLY_BUILD_MODE_READONLY_V1_PASS"
