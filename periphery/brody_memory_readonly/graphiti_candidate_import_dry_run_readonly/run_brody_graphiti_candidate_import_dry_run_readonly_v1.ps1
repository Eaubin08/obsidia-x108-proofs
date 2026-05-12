param(
  [string]$CandidatesJsonl = "",
  [string]$OutDir = "",
  [int]$MaxRecords = 200
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Resolve-Path (Join-Path $scriptDir "..\..\..")
$root = Resolve-Path (Join-Path $repo "..")
$py = Join-Path $scriptDir "brody_graphiti_candidate_import_dry_run_readonly_v1.py"

if ($CandidatesJsonl -eq "") {
  $ptr = Join-Path $root "CURRENT_BRODY_CANDIDATE_EXPORT_FOR_GRAPHITI_READONLY_V1_REMOTE_CLOSE.txt"
  if (!(Test-Path $ptr)) {
    throw "MISSING_REMOTE_CLOSE_POINTER=$ptr"
  }

  $kv = @{}
  Get-Content $ptr | ForEach-Object {
    if ($_ -match "^(.*?)=(.*)$") {
      $kv[$matches[1]] = $matches[2]
    }
  }

  $CandidatesJsonl = $kv["CANDIDATES_JSONL"]
}

if ($CandidatesJsonl -eq "" -or !(Test-Path $CandidatesJsonl)) {
  throw "MISSING_CANDIDATES_JSONL=$CandidatesJsonl"
}

if ($OutDir -eq "") {
  $ts = Get-Date -Format "yyyyMMdd_HHmmss"
  $OutDir = Join-Path $root "_local_audits\BRODY_GRAPHITI_CANDIDATE_IMPORT_DRY_RUN_READONLY_V1_$ts"
}

New-Item -ItemType Directory -Force $OutDir | Out-Null

python $py --candidates-jsonl $CandidatesJsonl --out-dir $OutDir --max-records $MaxRecords

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_GRAPHITI_CANDIDATE_IMPORT_DRY_RUN_READONLY_FAILED"
}
