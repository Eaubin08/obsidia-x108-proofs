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

$handoff = Read-Kv -Path (Join-Path $x108 "CURRENT_BRODY_OPERATOR_SUPERVISED_HANDOFF_READONLY.txt")

if ($handoff["STATUS"] -ne "BRODY_OPERATOR_SUPERVISED_HANDOFF_READONLY_V1_PASS") {
  throw "BAD_SUPERVISED_HANDOFF_STATUS=$($handoff["STATUS"])"
}

if (!(Test-Path $handoff["RUN_PS1"])) {
  throw "MISSING_SUPERVISED_HANDOFF_RUNNER=$($handoff["RUN_PS1"])"
}

powershell -NoProfile -ExecutionPolicy Bypass -File $handoff["RUN_PS1"] -Root $Root
if ($LASTEXITCODE -ne 0) {
  throw "SUPERVISED_HANDOFF_FAILED_DURING_CLEAN_CLOSE"
}

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_SUPERVISED_HANDOFF_CLEAN_CLOSE"
}

Write-Host "BRODY_OPERATOR_SUPERVISED_HANDOFF_CLEAN_CLOSE_READONLY_V1_PASS"
