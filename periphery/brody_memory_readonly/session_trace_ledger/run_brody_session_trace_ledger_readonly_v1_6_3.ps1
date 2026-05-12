param(
  [Parameter(Mandatory=$true)][string]$Event,
  [string]$Body = "",
  [string]$Source = "",
  [string]$Tags = ""
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..")).Path
$py = Join-Path $scriptDir "brody_session_trace_ledger_readonly_v1_6_3.py"
$ledgerRoot = Join-Path $repoRoot "_session_trace_ledgers"

& python $py `
  --root "$repoRoot" `
  --ledger-root "$ledgerRoot" `
  --event "$Event" `
  --body "$Body" `
  --source "$Source" `
  --tags "$Tags"

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_SESSION_TRACE_LEDGER_V1_6_3_FAILED"
}
