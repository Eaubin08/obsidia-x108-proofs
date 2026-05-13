param(
  [Parameter(Mandatory=$true)]
  [string]$OutDir
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = Join-Path $ScriptDir "brody_memory_pipeline_freeze_v2_readonly.py"

python $Py --out-dir $OutDir

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_FAILED"
}
