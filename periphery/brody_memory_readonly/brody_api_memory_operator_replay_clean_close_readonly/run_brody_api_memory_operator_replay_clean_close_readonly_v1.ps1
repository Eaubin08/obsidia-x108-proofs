param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$x108 = Join-Path $Root "obsidia-x108-proofs"

function Read-Kv {
  param([string]$Path)

  if (!(Test-Path $Path)) {
    throw "MISSING_POINTER=$Path"
  }

  $kv = @{}
  Get-Content $Path | ForEach-Object {
    if ($_ -match "^\s*([^=]+)=(.*)$") {
      $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
    }
  }

  return $kv
}

$v2 = Read-Kv -Path (Join-Path $x108 "CURRENT_BRODY_API_MEMORY_OPERATOR_REPLAY_API_FIX_V2_READONLY.txt")

if ($v2["STATUS"] -ne "BRODY_API_MEMORY_OPERATOR_REPLAY_API_FIX_V2_READONLY_V1_PASS") {
  throw "BAD_API_FIX_V2_STATUS=$($v2["STATUS"])"
}

if ($v2["ENDPOINT_COUNT"] -ne "10") {
  throw "BAD_API_FIX_V2_ENDPOINT_COUNT=$($v2["ENDPOINT_COUNT"]) EXPECTED=10"
}

if (!(Test-Path $v2["RUN_PS1"])) {
  throw "MISSING_API_FIX_V2_RUNNER=$($v2["RUN_PS1"])"
}

powershell -NoProfile -ExecutionPolicy Bypass -File $v2["RUN_PS1"] -Root $Root
if ($LASTEXITCODE -ne 0) {
  throw "API_FIX_V2_FAILED_DURING_API_REPLAY_CLEAN_CLOSE"
}

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_API_REPLAY_CLEAN_CLOSE"
}

Write-Host "BRODY_API_MEMORY_OPERATOR_REPLAY_CLEAN_CLOSE_READONLY_V1_PASS"
