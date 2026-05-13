param(
  [string]$OutDir = "",
  [switch]$AcceptSuggested,
  [string]$DecisionFile = ""
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..\..")
$workspaceRoot = Split-Path -Parent $repoRoot

if ($OutDir -eq "") {
  $ts = Get-Date -Format "yyyyMMdd_HHmmss"
  $OutDir = Join-Path $workspaceRoot "_local_audits\BRODY_GRAPHITI_REVIEW_DECISION_APPLY_READONLY_V1_$ts"
}

New-Item -ItemType Directory -Force $OutDir | Out-Null

$py = Join-Path $scriptDir "brody_graphiti_review_decision_apply_readonly_v1.py"

$argsList = @(
  $py,
  "--workspace-root", $workspaceRoot,
  "--out-dir", $OutDir
)

if ($AcceptSuggested) {
  $argsList += "--accept-suggested"
}

if ($DecisionFile -ne "") {
  $argsList += @("--decision-file", $DecisionFile)
}

python @argsList

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_GRAPHITI_REVIEW_DECISION_APPLY_READONLY_FAILED"
}
