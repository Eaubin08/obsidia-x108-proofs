param(
  [string]$Once = "",
  [string]$SessionDir = "",
  [string]$SessionId = ""
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$brodyMemoryDir = Split-Path -Parent $scriptDir
$peripheryDir = Split-Path -Parent $brodyMemoryDir
$x108 = Split-Path -Parent $peripheryDir
$coreRoot = Split-Path -Parent $x108

$terminalRunner = Join-Path $brodyMemoryDir "terminal_structural_dialogue_readonly\run_brody_terminal_structural_dialogue_readonly_v1.ps1"
$ledgerPy = Join-Path $scriptDir "brody_session_memory_ledger_readonly_v2.py"

if (!(Test-Path $terminalRunner)) {
  throw "MISSING_TERMINAL_RUNNER=$terminalRunner"
}

if (!(Test-Path $ledgerPy)) {
  throw "MISSING_LEDGER_PY=$ledgerPy"
}

if ($SessionId -eq "") {
  $SessionId = "BRODY_SESSION_" + (Get-Date -Format "yyyyMMdd_HHmmss")
}

if ($SessionDir -eq "") {
  $SessionDir = Join-Path $coreRoot "_local_audits\$SessionId"
}

New-Item -ItemType Directory -Force $SessionDir | Out-Null

function Invoke-BrodyLedgerOnce {
  param(
    [Parameter(Mandatory=$true)]
    [string]$InputText
  )

  $safeSeq = Get-Date -Format "yyyyMMdd_HHmmss_ffff"
  $rawPath = Join-Path $SessionDir "brody_response_raw_$safeSeq.json"

  $raw = powershell -ExecutionPolicy Bypass -File $terminalRunner -Once $InputText
  $rawText = ($raw | Out-String).Trim()
  $rawText | Set-Content -Encoding UTF8 $rawPath

  python $ledgerPy --user $InputText --response-raw $rawPath --session-dir $SessionDir --session-id $SessionId

  if ($LASTEXITCODE -ne 0) {
    throw "BRODY_SESSION_MEMORY_LEDGER_READONLY_V2_FAILED"
  }
}

if ($Once -ne "") {
  Invoke-BrodyLedgerOnce -InputText $Once
  exit 0
}

Write-Host "BRODY ledger terminal ouvert. :quit pour sortir."
Write-Host "SESSION_ID=$SessionId"
Write-Host "SESSION_DIR=$SessionDir"

while ($true) {
  $inputText = Read-Host "toi"
  if ($inputText -eq ":quit") {
    break
  }
  if ($inputText.Trim() -eq "") {
    continue
  }

  Write-Host ""
  Write-Host "brody ledger >"
  Invoke-BrodyLedgerOnce -InputText $inputText
  Write-Host ""
}
