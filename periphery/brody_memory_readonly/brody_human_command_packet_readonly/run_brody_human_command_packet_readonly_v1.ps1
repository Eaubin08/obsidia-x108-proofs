param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"
$x108 = Join-Path $Root "obsidia-x108-proofs"

$packetDir = Join-Path $x108 "periphery\brody_memory_readonly\brody_human_command_packet_readonly"
$packetPy = Join-Path $packetDir "brody_human_command_packet_readonly_v1.py"
$smokePy = Join-Path $packetDir "smoke_brody_human_command_packet_readonly_v1.py"
$baselinePtr = Join-Path $x108 "CURRENT_BRODY_X108_CURRENT_STATE_BASELINE_FREEZE_READONLY.txt"

foreach ($p in @($packetPy, $smokePy, $baselinePtr)) {
  if (!(Test-Path $p)) { throw "MISSING_FILE=$p" }
}

python -m py_compile $packetPy
if ($LASTEXITCODE -ne 0) { throw "PACKET_PY_COMPILE_FAILED" }

python -m py_compile $smokePy
if ($LASTEXITCODE -ne 0) { throw "SMOKE_PY_COMPILE_FAILED" }

python $smokePy
if ($LASTEXITCODE -ne 0) { throw "HUMAN_COMMAND_PACKET_SMOKE_FAILED" }

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) { throw "VERIFY_ALL_FAILED_DURING_HUMAN_COMMAND_PACKET" }

Write-Host "BRODY_HUMAN_COMMAND_PACKET_READONLY_V1_PASS"
