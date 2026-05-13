param(
  [Parameter(Mandatory=$true)]
  [string]$OutDir
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$x108 = Resolve-Path (Join-Path $scriptDir "..\..\..")
$root = Resolve-Path (Join-Path $x108 "..")

$py = Join-Path $scriptDir "brody_memory_pipeline_freeze_report_readonly_v1.py"

python $py --root "$root" --x108 "$x108" --out-dir "$OutDir"

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_MEMORY_PIPELINE_FREEZE_REPORT_READONLY_FAILED"
}
