param(
  [Parameter(Mandatory=$true)]
  [string]$OutDir
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = Join-Path $ScriptDir "brody_readonly_session_test_v1.py"

if (!(Test-Path $Py)) {
  throw "MISSING_READONLY_SESSION_TEST_PY=$Py"
}

python $Py --out-dir $OutDir

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_READONLY_SESSION_TEST_FAILED"
}
