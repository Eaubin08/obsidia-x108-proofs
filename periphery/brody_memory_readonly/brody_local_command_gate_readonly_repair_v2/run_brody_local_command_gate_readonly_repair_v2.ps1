param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$x108 = Join-Path $Root "obsidia-x108-proofs"
$gateDir = Join-Path $x108 "periphery\brody_memory_readonly\brody_local_command_gate_readonly"
$gateRunner = Join-Path $gateDir "run_brody_local_command_gate_readonly_v1.ps1"
$gatePy = Join-Path $gateDir "brody_local_command_gate_readonly_v1.py"
$smokePy = Join-Path $gateDir "smoke_brody_local_command_gate_readonly_v1.py"

foreach ($p in @($gateRunner, $gatePy, $smokePy)) {
  if (!(Test-Path $p)) { throw "MISSING_FILE=$p" }
}

powershell -NoProfile -ExecutionPolicy Bypass -File $gateRunner -Root $Root
if ($LASTEXITCODE -ne 0) { throw "LOCAL_COMMAND_GATE_RUNNER_FAILED_AFTER_REPAIR_V2" }

$tmp = Join-Path $env:TEMP "brody_local_command_gate_repair_v2_check.py"

@'
import sys
from pathlib import Path

gate_dir = Path(r"__GATE_DIR__")
sys.path.insert(0, str(gate_dir))

from brody_local_command_gate_readonly_v1 import evaluate_command

checks = [
    ("git -C obsidia-x108-proofs push", "GIT_MUTATION_COMMAND_HUMAN_ONLY"),
    ("git -C obsidia-x108-proofs commit -m test", "GIT_MUTATION_COMMAND_HUMAN_ONLY"),
    ("Remove-Item -Recurse -Force .\\tmp", "FILESYSTEM_MUTATION_COMMAND_HUMAN_ONLY"),
    ("rm -rf ./tmp", "FILESYSTEM_MUTATION_COMMAND_HUMAN_ONLY"),
]

for command, expected in checks:
    out = evaluate_command({
        "command": command,
        "claimed_purpose": "repair_v2_direct_check",
        "target_repo": "obsidia-x108-proofs",
    })

    assert out["classification"] == expected, out
    assert out["brody_execute_allowed"] is False, out
    assert out["executed"] is False, out
    assert out["decision_authority"] == "KX108_ONLY", out
    assert out["memory_decision"] is False, out
    assert out["emits_act"] is False, out
    assert out["emits_verdict"] is False, out
    assert out["x108_runtime_binding"] is False, out
    assert out["x108_merge"] is False, out

print("BRODY_LOCAL_COMMAND_GATE_READONLY_V1_REPAIR_V2_PASS")
'@.Replace("__GATE_DIR__", $gateDir.Replace("\", "\\")) | Set-Content -Encoding UTF8 $tmp

python $tmp
if ($LASTEXITCODE -ne 0) { throw "LOCAL_COMMAND_GATE_REPAIR_V2_DIRECT_CHECK_FAILED" }

Write-Host "BRODY_LOCAL_COMMAND_GATE_READONLY_V1_REPAIR_V2_PASS"
