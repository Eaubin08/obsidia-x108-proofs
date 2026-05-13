param(
  [string]$ReviewRecordsJsonl = "",
  [string]$OutDir = "",
  [int]$Limit = 200,
  [switch]$Apply,
  [string]$Confirm = ""
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..\..")
$workspaceRoot = Split-Path -Parent $repoRoot

if ($ReviewRecordsJsonl -eq "") {
  $validatePointer = Join-Path $workspaceRoot "CURRENT_BRODY_GRAPHITI_CANDIDATE_REVIEW_GATE_READONLY_V1_VALIDATE.txt"
  if (!(Test-Path $validatePointer)) {
    throw "MISSING_REVIEW_GATE_VALIDATE_POINTER=$validatePointer"
  }

  $kv = @{}
  Get-Content $validatePointer | ForEach-Object {
    if ($_ -match "^(.*?)=(.*)$") {
      $kv[$matches[1]] = $matches[2]
    }
  }

  $ReviewRecordsJsonl = $kv["REVIEW_RECORDS_JSONL"]
}

if (!(Test-Path $ReviewRecordsJsonl)) {
  throw "MISSING_REVIEW_RECORDS_JSONL=$ReviewRecordsJsonl"
}

if ($OutDir -eq "") {
  $ts = Get-Date -Format "yyyyMMdd_HHmmss"
  $OutDir = Join-Path $workspaceRoot "_local_audits\BRODY_GRAPHITI_IMPORT_APPLY_GUARDED_MANUAL_ONLY_V1_RUN_$ts"
}

New-Item -ItemType Directory -Force $OutDir | Out-Null

$py = Join-Path $scriptDir "brody_graphiti_import_apply_guarded_manual_only_v1.py"

$argsList = @(
  $py,
  "--review-records-jsonl", $ReviewRecordsJsonl,
  "--out-dir", $OutDir,
  "--limit", "$Limit"
)

if ($Apply) {
  $argsList += "--apply"
  $argsList += @("--confirm", $Confirm)
}

python @argsList

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_GRAPHITI_IMPORT_APPLY_GUARDED_MANUAL_ONLY_FAILED"
}
