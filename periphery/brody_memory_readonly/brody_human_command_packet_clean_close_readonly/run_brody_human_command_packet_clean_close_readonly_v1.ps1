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

$packet = Read-Kv -Path (Join-Path $x108 "CURRENT_BRODY_HUMAN_COMMAND_PACKET_READONLY.txt")

if ($packet["STATUS"] -ne "BRODY_HUMAN_COMMAND_PACKET_READONLY_V1_PASS") {
  throw "BAD_HUMAN_COMMAND_PACKET_STATUS=$($packet["STATUS"])"
}

if (!(Test-Path $packet["RUN_PS1"])) {
  throw "MISSING_HUMAN_COMMAND_PACKET_RUNNER=$($packet["RUN_PS1"])"
}

powershell -NoProfile -ExecutionPolicy Bypass -File $packet["RUN_PS1"] -Root $Root
if ($LASTEXITCODE -ne 0) {
  throw "HUMAN_COMMAND_PACKET_FAILED_DURING_CLEAN_CLOSE"
}

python (Join-Path $x108 "proofs\verify_all.py")
if ($LASTEXITCODE -ne 0) {
  throw "VERIFY_ALL_FAILED_DURING_HUMAN_COMMAND_PACKET_CLEAN_CLOSE"
}

Write-Host "BRODY_HUMAN_COMMAND_PACKET_CLEAN_CLOSE_READONLY_V1_PASS"
