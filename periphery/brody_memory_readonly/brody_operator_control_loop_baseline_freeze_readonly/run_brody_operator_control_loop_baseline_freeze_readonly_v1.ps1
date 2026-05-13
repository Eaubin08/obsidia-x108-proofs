param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"
$x108 = Join-Path $Root "obsidia-x108-proofs"

function Read-Kv {
  param([string]$Path)

  if (!(Test-Path $Path)) { throw "MISSING_POINTER=$Path" }

  $kv = @{}
  Get-Content $Path | ForEach-Object {
    if ($_ -match "^\s*([^=]+)=(.*)$") {
      $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
    }
  }

  return $kv
}

$ioLoop = Read-Kv -Path (Join-Path $x108 "CURRENT_BRODY_OPERATOR_IO_LOOP_CLEAN_CLOSE_READONLY.txt")
$handoff = Read-Kv -Path (Join-Path $x108 "CURRENT_BRODY_OPERATOR_HANDOFF_LINE_CLEAN_CLOSE_READONLY.txt")

if ($ioLoop["STATUS"] -ne "BRODY_OPERATOR_IO_LOOP_CLEAN_CLOSE_READONLY_V1_PASS") {
  throw "BAD_IO_LOOP_CLEAN_CLOSE_STATUS=$($ioLoop["STATUS"])"
}

if ($handoff["STATUS"] -ne "BRODY_OPERATOR_HANDOFF_LINE_CLEAN_CLOSE_READONLY_V1_PASS") {
  throw "BAD_HANDOFF_LINE_CLEAN_CLOSE_STATUS=$($handoff["STATUS"])"
}

foreach ($runnerPath in @($ioLoop["RUN_PS1"], $handoff["RUN_PS1"])) {
  if (!(Test-Path $runnerPath)) {
    throw "MISSING_CHILD_RUNNER=$runnerPath"
  }

  powershell -NoProfile -ExecutionPolicy Bypass -File $runnerPath -Root $Root
  if ($LASTEXITCODE -ne 0) {
    throw "CHILD_RUNNER_FAILED=$runnerPath"
  }
}

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_CONTROL_LOOP_BASELINE"
}

Write-Host "BRODY_OPERATOR_CONTROL_LOOP_BASELINE_FREEZE_READONLY_V1_PASS"
