param(
  [string]$ApprovedImportCandidatesJsonl = "",
  [string]$OutDir = "",
  [int]$Limit = 500,
  [switch]$Apply,
  [string]$Confirm = ""
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..\..")
$workspaceRoot = Split-Path -Parent $repoRoot

if ($ApprovedImportCandidatesJsonl -eq "") {
  $validatePointer = Join-Path $workspaceRoot "CURRENT_BRODY_GRAPHITI_REVIEW_DECISION_APPLY_READONLY_V1_VALIDATE.txt"
  if (!(Test-Path $validatePointer)) {
    throw "MISSING_GRAPHITI_REVIEW_DECISION_APPLY_VALIDATE_POINTER=$validatePointer"
  }

  $kv = @{}
  Get-Content $validatePointer | ForEach-Object {
    if ($_ -match "^\s*([^=]+)=(.*)$") {
      $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
    }
  }

  $ApprovedImportCandidatesJsonl = $kv["APPROVED_IMPORT_CANDIDATES_JSONL"]
}

if (!(Test-Path $ApprovedImportCandidatesJsonl)) {
  throw "MISSING_APPROVED_IMPORT_CANDIDATES_JSONL=$ApprovedImportCandidatesJsonl"
}

if ($OutDir -eq "") {
  $ts = Get-Date -Format "yyyyMMdd_HHmmss"
  $OutDir = Join-Path $workspaceRoot "_local_audits\BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_FROM_REVIEW_DECISION_READONLY_MEMORY_ONLY_V1_$ts"
}

New-Item -ItemType Directory -Force $OutDir | Out-Null

$py = Join-Path $scriptDir "brody_graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only_v1.py"

$argsList = @(
  $py,
  "--approved-import-candidates-jsonl", $ApprovedImportCandidatesJsonl,
  "--out-dir", $OutDir,
  "--limit", "$Limit"
)

if ($Apply) {
  $argsList += "--apply"
  $argsList += @("--confirm", $Confirm)
}

python @argsList

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_FROM_REVIEW_DECISION_FAILED"
}
