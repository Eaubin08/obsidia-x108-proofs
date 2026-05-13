param(
  [string]$OutDir = "",
  [string]$TerminalRunner = "",
  [string]$QueriesJson = ""
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Resolve-Path (Join-Path $scriptDir "..\..\..")
$py = Join-Path $scriptDir "brody_memory_replay_query_regression_readonly_v1.py"

if ($TerminalRunner -eq "") {
  $TerminalRunner = Join-Path $repo "periphery\brody_memory_readonly\terminal_structural_dialogue_readonly\run_brody_terminal_structural_dialogue_readonly_v1.ps1"
}

if ($OutDir -eq "") {
  $ts = Get-Date -Format "yyyyMMdd_HHmmss"
  $OutDir = Join-Path $repo "_local_replay\BRODY_MEMORY_REPLAY_QUERY_REGRESSION_READONLY_$ts"
}

$argsList = @(
  $py,
  "--terminal-runner", $TerminalRunner,
  "--out-dir", $OutDir
)

if ($QueriesJson -ne "") {
  $argsList += @("--queries-json", $QueriesJson)
}

python @argsList

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_MEMORY_REPLAY_QUERY_REGRESSION_READONLY_FAILED"
}
