param(
  [string]$OutDir = "",
  [string]$Label = "PROJECT_INTAKE_CAPTURE",
  [int]$SinceHours = 72,
  [int]$Limit = 500,
  [int]$MaxBytes = 26214400
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..\..")
$workspaceRoot = Split-Path -Parent $repoRoot

if ($OutDir -eq "") {
  $ts = Get-Date -Format "yyyyMMdd_HHmmss"
  $OutDir = Join-Path $workspaceRoot "_local_audits\BRODY_PROJECT_INTAKE_CAPTURE_BUFFER_READONLY_V1_$ts"
}

New-Item -ItemType Directory -Force $OutDir | Out-Null

$py = Join-Path $scriptDir "brody_project_intake_capture_buffer_readonly_v1.py"

python $py `
  --out-dir $OutDir `
  --label $Label `
  --since-hours $SinceHours `
  --limit $Limit `
  --max-bytes $MaxBytes

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_PROJECT_INTAKE_CAPTURE_BUFFER_READONLY_FAILED"
}
