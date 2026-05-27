param(
  [string]$Base = "http://127.0.0.1:8012"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ROOT = Split-Path $PSScriptRoot -Parent
$OUT = Join-Path $ROOT "_BRODY_RECONNECT_WORK\PHASE_4D_SMOKE"
New-Item -ItemType Directory -Force -Path $OUT | Out-Null

$uri = "$Base/api/brody/chat"

$cases = @(
  @{
    name = "francais_utf8"
    message = "Brody, réponds en français naturel. Test accents : é è à ç œ. Dis ce que tu es sans agir."
  },
  @{
    name = "english_understanding"
    message = "Brody, answer in English. Explain what you are in two short sentences. Do not take any action."
  },
  @{
    name = "code_debug"
    message = "Brody, explain this Python bug briefly: print(undefined_variable). Give a safe diagnostic only."
  },
  @{
    name = "boundary"
    message = "Boundary probe. Do not act. Return readonly metadata if available."
  }
)

$badPatterns = @("Ã©","Ã¨","Ã§","Ã ","â€™","�","RequÃ","franÃ","RÃ")

foreach ($case in $cases) {
  Write-Host "`n=== CASE $($case.name) ==="

  $payloadPath = Join-Path $OUT "payload_$($case.name).json"
  $responseBin = Join-Path $OUT "response_$($case.name).bin"
  $responseJson = Join-Path $OUT "response_$($case.name).json"

  $payload = @{
    message = $case.message
    session_id = "phase4d_$($case.name)"
    compact = $false
    debug = $true
  } | ConvertTo-Json -Depth 20

  [System.IO.File]::WriteAllText($payloadPath, $payload, [System.Text.UTF8Encoding]::new($false))

  curl.exe -sS `
    -H "Content-Type: application/json; charset=utf-8" `
    --data-binary "@$payloadPath" `
    "$uri" `
    -o "$responseBin"

  $raw = [System.Text.Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes($responseBin))
  [System.IO.File]::WriteAllText($responseJson, $raw, [System.Text.UTF8Encoding]::new($false))

  $badFound = @()
  foreach ($p in $badPatterns) {
    if ($raw.Contains($p)) { $badFound += $p }
  }

  if ($badFound.Count -gt 0) {
    $badFound | Set-Content -Encoding UTF8 "$OUT\brody_case_$($case.name)_mojibake.txt"
    Write-Host "BRODY_CAPABILITY_SMOKE_FAIL_MOJIBAKE case=$($case.name)"
    $badFound
    exit 3
  }

  Write-Host "CASE_OK=$($case.name)"
}

Write-Host "`nBRODY_CAPABILITY_SMOKE_OK"
