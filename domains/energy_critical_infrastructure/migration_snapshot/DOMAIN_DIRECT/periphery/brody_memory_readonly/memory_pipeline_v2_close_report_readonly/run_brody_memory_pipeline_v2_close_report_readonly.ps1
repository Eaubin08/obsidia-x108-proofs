param(
  [Parameter(Mandatory=$true)]
  [string]$OutDir
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $scriptDir "brody_memory_pipeline_v2_close_report_readonly.py"

python $py --out-dir $OutDir

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_FAILED"
}
