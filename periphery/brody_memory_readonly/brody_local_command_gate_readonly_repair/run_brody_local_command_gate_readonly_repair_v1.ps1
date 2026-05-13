param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$x108 = Join-Path $Root "obsidia-x108-proofs"
$gateRunner = Join-Path $x108 "periphery\brody_memory_readonly\brody_local_command_gate_readonly\run_brody_local_command_gate_readonly_v1.ps1"
$gatePy = Join-Path $x108 "periphery\brody_memory_readonly\brody_local_command_gate_readonly\brody_local_command_gate_readonly_v1.py"

if (!(Test-Path $gateRunner)) { throw "MISSING_GATE_RUNNER=$gateRunner" }
if (!(Test-Path $gatePy)) { throw "MISSING_GATE_PY=$gatePy" }

powershell -NoProfile -ExecutionPolicy Bypass -File $gateRunner -Root $Root
if ($LASTEXITCODE -ne 0) { throw "LOCAL_COMMAND_GATE_RUNNER_FAILED_AFTER_REPAIR" }

$tmp = Join-Path $env:TEMP "brody_local_command_gate_repair_check.py"
@'
import sys
from pathlib import Path

gate_dir = Path(r"__GATE_DIR__")
sys.path.insert(0, str(gate_dir))

from brody_local_command_gate_readonly_v1 import evaluate_command

out = evaluate_command({
    "command": "git -C obsidia-x108-proofs push",
    "claimed_purpose": "repair_check",
    "target_repo": "obsidia-x108-proofs",
})

assert out["classification"] == "GIT_MUTATION_COMMAND_HUMAN_ONLY", out
assert out["brody_execute_allowed"] is False
assert out["executed"] is False
assert out["decision_authority"] == "KX108_ONLY"
assert out["memory_decision"] is False
assert out["emits_act"] is False
assert out["emits_verdict"] is False
assert out["x108_runtime_binding"] is False
assert out["x108_merge"] is False

print("BRODY_LOCAL_COMMAND_GATE_READONLY_V1_REPAIR_PASS")
'@.Replace("__GATE_DIR__", (Split-Path $gatePy -Parent).Replace("\", "\\")) | Set-Content -Encoding UTF8 $tmp

python $tmp
if ($LASTEXITCODE -ne 0) { throw "LOCAL_COMMAND_GATE_REPAIR_DIRECT_CHECK_FAILED" }

Write-Host "BRODY_LOCAL_COMMAND_GATE_READONLY_V1_REPAIR_PASS"
