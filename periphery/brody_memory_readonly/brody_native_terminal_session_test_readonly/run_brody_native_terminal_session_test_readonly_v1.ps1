param(
  [Parameter(Mandatory=$true)]
  [string]$OutDir,

  [Parameter(Mandatory=$true)]
  [string]$CandidateRepo,

  [Parameter(Mandatory=$true)]
  [string]$CandidateRunner
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $CandidateRepo)) {
  throw "MISSING_CANDIDATE_REPO=$CandidateRepo"
}

if (!(Test-Path $CandidateRunner)) {
  throw "MISSING_CANDIDATE_RUNNER=$CandidateRunner"
}

New-Item -ItemType Directory -Force $OutDir | Out-Null

$transcript = Join-Path $OutDir "BRODY_NATIVE_TERMINAL_TRANSCRIPT.txt"
$summaryJson = Join-Path $OutDir "BRODY_NATIVE_TERMINAL_SESSION_TEST_SUMMARY.json"
$reportMd = Join-Path $OutDir "BRODY_NATIVE_TERMINAL_SESSION_TEST_REPORT.md"

$runError = ""
$exitCode = $null
$startedAt = (Get-Date).ToUniversalTime().ToString("o")

Start-Transcript -Path $transcript -Force | Out-Null

Push-Location $CandidateRepo
try {
  Write-Host "`n=== BRODY / LLM OBSIDIEN NATIVE TERMINAL RUNTIME ==="
  Write-Host "CANDIDATE_REPO=$CandidateRepo"
  Write-Host "CANDIDATE_RUNNER=$CandidateRunner"
  & powershell -NoProfile -ExecutionPolicy Bypass -File $CandidateRunner
  $exitCode = $LASTEXITCODE
  if ($null -eq $exitCode) { $exitCode = 0 }
}
catch {
  $runError = $_.Exception.Message
  $exitCode = 999
}
finally {
  Pop-Location
  Stop-Transcript | Out-Null
}

$finishedAt = (Get-Date).ToUniversalTime().ToString("o")
$pass = ($exitCode -eq 0)

$status = if ($pass) {
  "BRODY_NATIVE_TERMINAL_SESSION_TEST_READONLY_V1_PASS"
} else {
  "BRODY_NATIVE_TERMINAL_SESSION_TEST_READONLY_V1_FAIL"
}

$summary = [ordered]@{
  status = $status
  started_at = $startedAt
  finished_at = $finishedAt
  candidate_repo = $CandidateRepo
  candidate_runner = $CandidateRunner
  exit_code = $exitCode
  error = $runError
  transcript = $transcript
  proof_wrapper = $true
  brody_runtime = "obsidia-engine-candidate"
  brody_llm_obsidien = $true
  terminal_native_run = $true
  readonly = $true
  response_only = $true
  graphiti_query_read = $false
  graphiti_index_write = $false
  neo4j_write_executed = $false
  memory_intake = $false
  memory_decision = $false
  allowed_to_decide = $false
  emits_act = $false
  emits_verdict = $false
  kernel_mutation = $false
  x108_runtime_binding = $false
  x108_merge = $false
  decision_authority = "KX108_ONLY"
  ui = $false
  brody_role = "NATIVE_TERMINAL_SESSION_TEST_READONLY"
  memory_role = "GUIDE_CONTEXT_NAVIGATION_ONLY"
  next = "REVIEW_TRANSCRIPT_THEN_COMMIT_OR_PATCH"
}

$summary | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 $summaryJson

@"
# BRODY NATIVE TERMINAL SESSION TEST READONLY V1

- status: $status
- exit_code: $exitCode
- transcript: $transcript
- candidate_runner: $CandidateRunner

## Boundary

- Runtime: Brody / LLM Obsidien native terminal.
- Proof wrapper: obsidia-x108-proofs.
- Graphiti write: false.
- Neo4j write: false.
- Memory intake: false.
- Memory decision: false.
- Emits ACT: false.
- Emits verdict: false.
- Kernel mutation: false.
- X108 runtime binding: false.
- X108 merge: false.
- Decision authority: KX108_ONLY.

## Next

REVIEW_TRANSCRIPT_THEN_COMMIT_OR_PATCH
"@ | Set-Content -Encoding UTF8 $reportMd

$summary | ConvertTo-Json -Depth 20

if (!$pass) {
  throw "BRODY_NATIVE_TERMINAL_SESSION_TEST_READONLY_V1_FAILED"
}
