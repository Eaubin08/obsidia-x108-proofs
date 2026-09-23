param(
  [string]$OutDir = ""
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..\..")
$workspaceRoot = Split-Path -Parent $repoRoot

if ($OutDir -eq "") {
  $ts = Get-Date -Format "yyyyMMdd_HHmmss"
  $OutDir = Join-Path $workspaceRoot "_local_audits\BRODY_GRAPHITI_CANDIDATE_PREP_FROM_POST_HUMAN_TRIAGE_READONLY_V1_$ts"
}

New-Item -ItemType Directory -Force $OutDir | Out-Null

$py = Join-Path $scriptDir "brody_graphiti_candidate_prep_from_post_human_triage_readonly_v1.py"

python $py `
  --workspace-root $workspaceRoot `
  --out-dir $OutDir

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_GRAPHITI_CANDIDATE_PREP_FROM_POST_HUMAN_TRIAGE_READONLY_FAILED"
}
