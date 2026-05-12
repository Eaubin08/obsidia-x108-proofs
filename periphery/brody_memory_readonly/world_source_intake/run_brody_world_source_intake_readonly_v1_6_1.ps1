param(
  [Parameter(Mandatory=$true)][string]$Source,
  [string]$Label = "SOURCE"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..")).Path
$py = Join-Path $scriptDir "brody_world_source_intake_readonly_v1_6_1.py"
$outRoot = Join-Path $repoRoot "_world_intake"

& python $py --source "$Source" --out-root "$outRoot" --label "$Label"

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_WORLD_SOURCE_INTAKE_V1_6_1_FAILED"
}
