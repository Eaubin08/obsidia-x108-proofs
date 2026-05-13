param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$x108 = Join-Path $Root "obsidia-x108-proofs"
$smokePy = Join-Path $x108 "periphery\brody_memory_readonly\brody_local_command_gate_readonly\smoke_brody_local_command_gate_readonly_v1.py"

if (!(Test-Path $smokePy)) {
  throw "MISSING_LOCAL_COMMAND_GATE_SMOKE=$smokePy"
}

& python $smokePy

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_LOCAL_COMMAND_GATE_SMOKE_FAILED_EXIT_CODE=$LASTEXITCODE"
}

Write-Host "BRODY_LOCAL_COMMAND_GATE_READONLY_V1_PASS"
