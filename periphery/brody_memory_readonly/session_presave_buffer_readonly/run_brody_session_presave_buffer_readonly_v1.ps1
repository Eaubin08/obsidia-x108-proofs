param(
  [string]$OutDir = "",
  [string]$Label = "MANUAL_PRESAVE",
  [int]$Limit = 200
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..\..")
$workspaceRoot = Split-Path -Parent $repoRoot

if ($OutDir -eq "") {
  $ts = Get-Date -Format "yyyyMMdd_HHmmss"
  $OutDir = Join-Path $workspaceRoot "_local_audits\BRODY_SESSION_PRESAVE_BUFFER_READONLY_V1_$ts"
}

New-Item -ItemType Directory -Force $OutDir | Out-Null

$py = Join-Path $scriptDir "brody_session_presave_buffer_readonly_v1.py"

python $py `
  --out-dir $OutDir `
  --label $Label `
  --limit $Limit

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_SESSION_PRESAVE_BUFFER_READONLY_FAILED"
}
