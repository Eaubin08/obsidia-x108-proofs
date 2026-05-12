param(
  [string]$TriageRecordsJsonl = "",
  [Parameter(Mandatory=$true)]
  [string]$OutDir,
  [int]$MaxCandidates = 200
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path (Split-Path (Split-Path $scriptDir -Parent) -Parent) -Parent
$root = Split-Path $repoRoot -Parent

if ($TriageRecordsJsonl -eq "") {
  $validatePointer = Join-Path $root "CURRENT_BRODY_AUTO_TRIAGE_MEMORY_INTAKE_READONLY_V1_VALIDATE.txt"
  if (!(Test-Path $validatePointer)) {
    throw "MISSING_AUTO_TRIAGE_VALIDATE_POINTER=$validatePointer"
  }

  $line = Get-Content $validatePointer | Where-Object { $_ -like "TRIAGE_RECORDS_JSONL=*" } | Select-Object -First 1
  if (!$line) {
    throw "MISSING_TRIAGE_RECORDS_JSONL_IN_POINTER=$validatePointer"
  }

  $TriageRecordsJsonl = ($line -replace "^TRIAGE_RECORDS_JSONL=", "").Trim()
}

if (!(Test-Path $TriageRecordsJsonl)) {
  throw "MISSING_TRIAGE_RECORDS_JSONL=$TriageRecordsJsonl"
}

$py = Join-Path $scriptDir "brody_candidate_export_for_graphiti_readonly_v1.py"

python $py `
  --triage-records-jsonl $TriageRecordsJsonl `
  --out-dir $OutDir `
  --max-candidates $MaxCandidates

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_CANDIDATE_EXPORT_FOR_GRAPHITI_READONLY_FAILED"
}
