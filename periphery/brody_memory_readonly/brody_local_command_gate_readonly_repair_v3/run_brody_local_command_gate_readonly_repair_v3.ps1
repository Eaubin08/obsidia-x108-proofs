param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$x108 = Join-Path $Root "obsidia-x108-proofs"
$gateDir = Join-Path $x108 "periphery\brody_memory_readonly\brody_local_command_gate_readonly"
$runner = Join-Path $gateDir "run_brody_local_command_gate_readonly_v1.ps1"
$smokePy = Join-Path $gateDir "smoke_brody_local_command_gate_readonly_v1.py"
$repairV2Runner = Join-Path $x108 "periphery\brody_memory_readonly\brody_local_command_gate_readonly_repair_v2\run_brody_local_command_gate_readonly_repair_v2.ps1"

foreach ($p in @($runner, $smokePy, $repairV2Runner)) {
  if (!(Test-Path $p)) { throw "MISSING_FILE=$p" }
}

powershell -NoProfile -ExecutionPolicy Bypass -File $runner -Root $Root
if ($LASTEXITCODE -ne 0) { throw "MAIN_LOCAL_COMMAND_GATE_RUNNER_FAILED_REPAIR_V3" }

powershell -NoProfile -ExecutionPolicy Bypass -File $repairV2Runner -Root $Root
if ($LASTEXITCODE -ne 0) { throw "REPAIR_V2_RUNNER_FAILED_REPAIR_V3" }

Write-Host "BRODY_LOCAL_COMMAND_GATE_READONLY_V1_REPAIR_V3_PASS"
