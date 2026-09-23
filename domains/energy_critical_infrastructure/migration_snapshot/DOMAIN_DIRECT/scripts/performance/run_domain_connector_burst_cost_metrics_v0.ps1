# === OBSIDIA DOMAIN CONNECTOR BURST COST METRICS V0 ===
# Mesure live Bank / Trading / GPS sans bloquer sur un connecteur long-running.

param(
  [string]$ApiBase = "http://127.0.0.1:8000",
  [int]$BurstSeconds = 10
)

$ErrorActionPreference = "Continue"

$REPO = Resolve-Path "$PSScriptRoot\..\.."
$RUNNER = Join-Path $REPO "scripts\performance\run_with_cost_event_v0.py"

function Stop-DomainConnectorChildren {
  param([string]$Pattern)

  Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -match $Pattern } |
    ForEach-Object {
      Write-Host "Stopping child PID=$($_.ProcessId) CMD=$($_.CommandLine)" -ForegroundColor Yellow
      Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

function Run-DomainBurst {
  param(
    [string]$Family,
    [string]$Route,
    [string]$ConnectorPath,
    [string]$Pattern
  )

  Write-Host "`n=== DOMAIN BURST: $Family $Route ===" -ForegroundColor Cyan

  $cmd = @"
cd '$REPO'
`$env:PYTHONPATH='$REPO'
`$env:OBSIDIA_API_BASE='$ApiBase'
`$p = Start-Process python -ArgumentList '$ConnectorPath' -PassThru -WindowStyle Hidden
Write-Host "CONNECTOR_STARTED_PID=`$(`$p.Id)"
Start-Sleep -Seconds $BurstSeconds
try {
  if (-not `$p.HasExited) {
    Stop-Process -Id `$p.Id -Force -ErrorAction SilentlyContinue
    Write-Host "CONNECTOR_STOPPED_PID=`$(`$p.Id)"
  } else {
    Write-Host "CONNECTOR_EXITED_CODE=`$(`$p.ExitCode)"
  }
} catch {
  Write-Host "CONNECTOR_STOP_WARN=`$(`$_.Exception.Message)"
}
Get-CimInstance Win32_Process |
  Where-Object { `$_.CommandLine -match '$Pattern' } |
  ForEach-Object {
    Write-Host "CONNECTOR_CHILD_CLEANUP_PID=`$(`$_.ProcessId)"
    Stop-Process -Id `$_.ProcessId -Force -ErrorAction SilentlyContinue
  }
Write-Host "CONNECTOR_BURST_DONE family=$Family route=$Route seconds=$BurstSeconds"
"@

  python $RUNNER `
    --family $Family `
    --route $Route `
    --request-text "$Family bounded connector burst live metric" `
    --timeout-sec ($BurstSeconds + 20) `
    --allow-timeout `
    -- powershell -NoProfile -ExecutionPolicy Bypass -Command $cmd

  $exit = $LASTEXITCODE
  if ($exit -ne 0) {
    Write-Host "WARN: burst metric returned exit=$exit for $Family" -ForegroundColor Yellow
  }

  Stop-DomainConnectorChildren -Pattern $Pattern
}

Run-DomainBurst `
  -Family "DOMAIN_BANK" `
  -Route "/api/live/kernel/adapters/bank" `
  -ConnectorPath ".\connectors\bank_normal_flow.py" `
  -Pattern "connectors\\bank_normal_flow.py"

Run-DomainBurst `
  -Family "DOMAIN_TRADING" `
  -Route "/api/live/kernel/adapters/trading" `
  -ConnectorPath ".\connectors\trading_live.py" `
  -Pattern "connectors\\trading_live.py"

Run-DomainBurst `
  -Family "DOMAIN_GPS_AVIATION" `
  -Route "/api/live/kernel/adapters/gps" `
  -ConnectorPath ".\connectors\aviation_robo.py" `
  -Pattern "connectors\\aviation_robo.py"

Write-Host "`n=== LATEST COST EVENTS ===" -ForegroundColor Cyan
Get-Content "$REPO\.local_reports\REQUEST_COST_EVENTS\cost_events.jsonl" -Tail 20

Write-Host "`nDOMAIN_CONNECTOR_BURST_COST_METRICS_DONE" -ForegroundColor Green
