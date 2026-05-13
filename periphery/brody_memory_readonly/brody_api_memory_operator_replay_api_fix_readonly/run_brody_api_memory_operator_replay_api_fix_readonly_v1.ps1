param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$x108 = Join-Path $Root "obsidia-x108-proofs"
$proofDir = Join-Path $x108 "periphery\brody_memory_readonly\brody_api_memory_operator_replay_api_fix_readonly"
$report = Join-Path $proofDir "reports\api_fix_report.json"
$endpointDir = Join-Path $proofDir "api_endpoints"

if (!(Test-Path $report)) {
  throw "MISSING_API_FIX_REPORT=$report"
}

if (!(Test-Path $endpointDir)) {
  throw "MISSING_API_FIX_ENDPOINT_DIR=$endpointDir"
}

$files = Get-ChildItem $endpointDir -File -Filter "*.json"
if ($files.Count -lt 10) {
  throw "API_FIX_ENDPOINT_CAPTURE_TOO_SMALL=$($files.Count)"
}

$data = Get-Content $report -Raw | ConvertFrom-Json

if ($data.status -ne "BRODY_API_MEMORY_OPERATOR_REPLAY_API_FIX_READONLY_V1_PASS") {
  throw "BAD_API_FIX_REPORT_STATUS=$($data.status)"
}

if ($data.endpoint_count -lt 10) {
  throw "BAD_API_FIX_ENDPOINT_COUNT=$($data.endpoint_count)"
}

if ($data.decision_authority -ne "KX108_ONLY") {
  throw "BAD_DECISION_AUTHORITY=$($data.decision_authority)"
}

if ($data.memory_decision -ne $false) { throw "MEMORY_DECISION_NOT_FALSE" }
if ($data.allowed_to_decide -ne $false) { throw "ALLOWED_TO_DECIDE_NOT_FALSE" }
if ($data.emits_act -ne $false) { throw "EMITS_ACT_NOT_FALSE" }
if ($data.emits_verdict -ne $false) { throw "EMITS_VERDICT_NOT_FALSE" }
if ($data.x108_runtime_binding -ne $false) { throw "X108_RUNTIME_BINDING_NOT_FALSE" }
if ($data.x108_merge -ne $false) { throw "X108_MERGE_NOT_FALSE" }

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_API_FIX"
}

Write-Host "BRODY_API_MEMORY_OPERATOR_REPLAY_API_FIX_READONLY_V1_PASS"
