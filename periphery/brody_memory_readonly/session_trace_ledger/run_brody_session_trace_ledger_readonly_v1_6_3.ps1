param(
  [Parameter(Mandatory=$true)][string]$Event,
  [string]$Body = "",
  [string]$Source = "",
  [string]$Tags = ""
)

$ErrorActionPreference = "Stop"

$pyArgs = @(
  "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-engine-candidate\zip1_sandbox_mutable\ZIP1_X108_MUTABLE_20260508_183610\periphery\brody_obsidien_v1_6_3_session_trace_ledger_readonly\brody_session_trace_ledger_readonly_v1_6_3.py",
  "--root", "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-engine-candidate",
  "--ledger-root", "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-engine-candidate\_session_trace_ledgers",
  "--event", $Event,
  "--body", $Body,
  "--source", $Source,
  "--tags", $Tags
)

& python @pyArgs

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_SESSION_TRACE_LEDGER_PYTHON_FAILED"
}
