param(
  [Parameter(Mandatory=$true)][string]$WorldPointer,
  [string]$GraphitiPointer = "",
  [string]$Label = "X108_GRAPHITI_READY_V164"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..")).Path
$outRoot = Join-Path $repoRoot "_graphiti_ready_exports"

New-Item -ItemType Directory -Force $outRoot | Out-Null

$pyArgs = @(
  (Join-Path $scriptDir "brody_graphiti_ready_export_readonly_v1_6_4.py"),
  "--root", $repoRoot,
  "--world-pointer", $WorldPointer,
  "--out-root", $outRoot,
  "--label", $Label
)

if ($GraphitiPointer -and (Test-Path -LiteralPath $GraphitiPointer)) {
  $pyArgs += @("--graphiti-pointer", $GraphitiPointer)
}

& python @pyArgs

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_GRAPHITI_READY_EXPORT_FAILED"
}
