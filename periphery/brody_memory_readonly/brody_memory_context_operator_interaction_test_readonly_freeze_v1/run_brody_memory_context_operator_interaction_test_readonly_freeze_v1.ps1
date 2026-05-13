param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$x108 = Join-Path $Root "obsidia-x108-proofs"
$proofDir = Join-Path $x108 "periphery\brody_memory_readonly\brody_memory_context_operator_interaction_test_readonly_freeze_v1"

$reportJson = Join-Path $proofDir "reports\BRODY_MEMORY_CONTEXT_OPERATOR_INTERACTION_TEST_READONLY_REPORT.json"
$gateReport = Join-Path $proofDir "reports\brody_command_gate_interaction_report.json"
$receiptJson = Join-Path $proofDir "operator_receipts\operator_receipt_api_status_and_git_status.json"
$endpointDir = Join-Path $proofDir "api_endpoints"

foreach ($p in @($reportJson, $gateReport, $receiptJson, $endpointDir)) {
  if (!(Test-Path $p)) {
    throw "MISSING_FREEZE_ARTIFACT=$p"
  }
}

$data = Get-Content $reportJson -Raw | ConvertFrom-Json

if ($data.status -ne "BRODY_MEMORY_CONTEXT_OPERATOR_INTERACTION_TEST_READONLY_PASS") {
  throw "BAD_REPORT_STATUS=$($data.status)"
}
if ($data.endpoint_count -lt 14) {
  throw "BAD_ENDPOINT_COUNT=$($data.endpoint_count)"
}
if ($data.negative_mutation_count -lt 3) {
  throw "BAD_NEGATIVE_MUTATION_COUNT=$($data.negative_mutation_count)"
}
if ($data.verify_all -ne "PASS") {
  throw "VERIFY_ALL_NOT_PASS_IN_REPORT=$($data.verify_all)"
}
if ($data.git_clean -ne $true) {
  throw "GIT_CLEAN_NOT_TRUE_IN_REPORT"
}
if ($data.decision_authority -ne "KX108_ONLY") {
  throw "BAD_DECISION_AUTHORITY=$($data.decision_authority)"
}

foreach ($flag in @(
  "brody_execute_allowed",
  "brody_authorize_allowed",
  "memory_decision",
  "allowed_to_decide",
  "emits_act",
  "emits_verdict",
  "graphiti_write",
  "graphiti_index_write",
  "neo4j_write_executed",
  "memory_intake",
  "kernel_mutation",
  "x108_runtime_binding",
  "x108_merge",
  "committed",
  "frozen"
)) {
  if ($data.$flag -ne $false) {
    throw "FLAG_NOT_FALSE_IN_REPORT=$flag VALUE=$($data.$flag)"
  }
}

$endpointFiles = Get-ChildItem $endpointDir -File -Filter "*.json"
if ($endpointFiles.Count -lt 14) {
  throw "ENDPOINT_CAPTURE_TOO_SMALL=$($endpointFiles.Count)"
}

$gate = Get-Content $gateReport -Raw | ConvertFrom-Json
foreach ($case in $gate.cases) {
  if ($case.brody_execute_allowed -ne $false) {
    throw "BRODY_EXECUTE_ALLOWED_NOT_FALSE_IN_GATE_CASE=$($case.name)"
  }
  if ($case.executed -ne $false) {
    throw "EXECUTED_NOT_FALSE_IN_GATE_CASE=$($case.name)"
  }
  if ($case.decision_authority -ne "KX108_ONLY") {
    throw "BAD_GATE_DECISION_AUTHORITY_IN_CASE=$($case.name)"
  }
}

$receipt = Get-Content $receiptJson -Raw | ConvertFrom-Json
if ($receipt.human_executed -ne $true) { throw "RECEIPT_HUMAN_EXECUTED_NOT_TRUE" }
if ($receipt.execution_verified -ne $false) { throw "RECEIPT_EXECUTION_VERIFIED_NOT_FALSE" }
if ($receipt.brody_execute_allowed -ne $false) { throw "RECEIPT_BRODY_EXECUTE_ALLOWED_NOT_FALSE" }
if ($receipt.brody_authorize_allowed -ne $false) { throw "RECEIPT_BRODY_AUTHORIZE_ALLOWED_NOT_FALSE" }
if ($receipt.decision_authority -ne "KX108_ONLY") { throw "RECEIPT_BAD_DECISION_AUTHORITY" }

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_MEMORY_CONTEXT_FREEZE"
}

Write-Host "BRODY_MEMORY_CONTEXT_OPERATOR_INTERACTION_TEST_READONLY_FREEZE_V1_PASS"
