param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$x108 = Join-Path $Root "obsidia-x108-proofs"
$proofDir = Join-Path $x108 "periphery\brody_memory_readonly\brody_api_memory_operator_replay_readonly"
$smokePy = Join-Path $proofDir "smoke_brody_api_memory_operator_replay_readonly_v1.py"
$manifest = Join-Path $proofDir "BRODY_API_MEMORY_OPERATOR_REPLAY_READONLY_MANIFEST.json"

if (!(Test-Path $smokePy)) {
  throw "MISSING_REPLAY_SMOKE=$smokePy"
}

if (!(Test-Path $manifest)) {
  throw "MISSING_REPLAY_MANIFEST=$manifest"
}

python $smokePy
if ($LASTEXITCODE -ne 0) {
  throw "BRODY_API_MEMORY_OPERATOR_REPLAY_SMOKE_FAILED"
}

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_API_MEMORY_OPERATOR_REPLAY"
}

Write-Host "BRODY_API_MEMORY_OPERATOR_REPLAY_READONLY_V1_PASS"
