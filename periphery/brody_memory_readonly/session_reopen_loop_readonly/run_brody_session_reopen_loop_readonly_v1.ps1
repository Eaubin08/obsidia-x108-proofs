param(
  [Parameter(Mandatory=$true)]
  [string]$OutDir,

  [string]$Neo4jUri = "bolt://localhost:7688",

  [int]$Limit = 100
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = Join-Path $ScriptDir "brody_session_reopen_loop_readonly_v1.py"

if (!(Test-Path $Py)) {
  throw "MISSING_SESSION_REOPEN_LOOP_PY=$Py"
}

python $Py `
  --out-dir $OutDir `
  --neo4j-uri $Neo4jUri `
  --limit $Limit

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_SESSION_REOPEN_LOOP_READONLY_FAILED"
}
