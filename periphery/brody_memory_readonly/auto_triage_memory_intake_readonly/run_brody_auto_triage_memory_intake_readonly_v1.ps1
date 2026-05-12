param(
  [string]$SessionLedgerJsonl = "",
  [string]$OutDir = "",
  [int]$MaxRecords = 200
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $scriptDir "brody_auto_triage_memory_intake_readonly_v1.py"

$x108 = (Resolve-Path (Join-Path $scriptDir "..\..\..")).Path
$root = (Resolve-Path (Join-Path $x108 "..")).Path

if ($SessionLedgerJsonl -eq "") {
  $validatePtr = Join-Path $root "CURRENT_BRODY_SESSION_MEMORY_LEDGER_READONLY_V2_VALIDATE.txt"
  if (!(Test-Path $validatePtr)) {
    throw "MISSING_CURRENT_BRODY_SESSION_MEMORY_LEDGER_READONLY_V2_VALIDATE"
  }

  $line = Get-Content $validatePtr | Where-Object { $_ -like "SESSION_LEDGER_JSONL=*" } | Select-Object -First 1
  if (!$line) {
    throw "MISSING_SESSION_LEDGER_JSONL_POINTER"
  }

  $SessionLedgerJsonl = $line.Substring("SESSION_LEDGER_JSONL=".Length)
}

if (!(Test-Path $SessionLedgerJsonl)) {
  throw "SESSION_LEDGER_JSONL_NOT_FOUND=$SessionLedgerJsonl"
}

if ($OutDir -eq "") {
  $ts = Get-Date -Format "yyyyMMdd_HHmmss"
  $OutDir = Join-Path $root "_local_audits\BRODY_AUTO_TRIAGE_MEMORY_INTAKE_READONLY_V1_$ts"
}

New-Item -ItemType Directory -Force $OutDir | Out-Null

python $py `
  --session-ledger-jsonl $SessionLedgerJsonl `
  --out-dir $OutDir `
  --max-records $MaxRecords

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_AUTO_TRIAGE_MEMORY_INTAKE_READONLY_FAILED"
}
