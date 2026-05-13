param(
  [Parameter(Mandatory=$true)]
  [string]$OutDir
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = Join-Path $ScriptDir "brody_memory_scheduler_readonly_v1.py"

if (!(Test-Path $Py)) {
  throw "MISSING_SCHEDULER_PY=$Py"
}

python $Py --out-dir $OutDir

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_MEMORY_SCHEDULER_READONLY_FAILED"
}
