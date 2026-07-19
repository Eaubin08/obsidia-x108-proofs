# === OBSIDIA LIVE STACK COST METRICS V0 ===
# Lance la stack puis mesure les vraies routes avec cost_event.
# Ne commit pas les reports locaux.

$ErrorActionPreference = "Continue"

$ROOT = if ($env:OBSIDIA_REPO_ROOT) { $env:OBSIDIA_REPO_ROOT } else { Split-Path -Parent (Split-Path -Parent $PSScriptRoot) }
$X108 = "$ROOT\obsidia-x108-proofs_REMOTE_A5F21C6B"
$RT = "$X108\runtime_terrain_bank_trading_gps"
$SHELL = "$ROOT\obsidiashell-main"
$UI_DIR = "$X108\apps\obsidia-workbench"

$API = "http://127.0.0.1:8000"
$KERNEL = "http://127.0.0.1:3001"
$KERNEL_URL = "http://127.0.0.1:3001/kernel/ragnarok"
$GRAPH = "http://127.0.0.1:8011"
$UI = "http://127.0.0.1:5173"

$RUNNER = "$X108\scripts\performance\run_with_cost_event_v0.py"

function Stop-ObsidiaLiveStack {
  Write-Host "`n=== STOP OLD LIVE STACK ===" -ForegroundColor Cyan

  Get-CimInstance Win32_Process |
    Where-Object {
      $_.CommandLine -match "server.kernel.sealed.cjs" -or
      $_.CommandLine -match "apps.obsidia_api.main:app" -or
      $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
      $_.CommandLine -match "connectors\\bank_normal_flow.py" -or
      $_.CommandLine -match "connectors\\trading_live.py" -or
      $_.CommandLine -match "connectors\\aviation_robo.py" -or
      $_.CommandLine -match "npm run dev" -or
      $_.CommandLine -match "vite"
    } |
    ForEach-Object {
      Write-Host "Stopping PID=$($_.ProcessId)" -ForegroundColor Yellow
      Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }

  foreach ($port in @(3001, 8000, 8011, 5173)) {
    $pids = netstat -ano |
      Select-String ":$port\s" |
      Where-Object { $_.Line -match "LISTENING" } |
      ForEach-Object { ($_ -split "\s+")[-1] } |
      Sort-Object -Unique

    foreach ($pid in $pids) {
      if ($pid -and $pid -ne "0") {
        Write-Host "Killing port $port PID=$pid" -ForegroundColor Yellow
        Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
      }
    }
  }

  Start-Sleep -Seconds 2
}

function Wait-Port {
  param(
    [int]$Port,
    [int]$TimeoutSec = 45
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    $hit = netstat -ano | Select-String ":$Port\s" | Where-Object { $_.Line -match "LISTENING" }
    if ($hit) {
      Write-Host "PORT_READY=$Port" -ForegroundColor Green
      return $true
    }
    Start-Sleep -Seconds 1
  }

  Write-Host "PORT_NOT_READY=$Port" -ForegroundColor Red
  return $false
}

function Wait-Http {
  param(
    [string]$Url,
    [int]$TimeoutSec = 45
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    try {
      $null = Invoke-RestMethod $Url -TimeoutSec 5
      Write-Host "HTTP_READY=$Url" -ForegroundColor Green
      return $true
    } catch {
      Start-Sleep -Seconds 1
    }
  }

  Write-Host "HTTP_NOT_READY=$Url" -ForegroundColor Yellow
  return $false
}

function Run-Costed {
  param(
    [string]$Family,
    [string]$Route,
    [string]$RequestText,
    [string]$CommandLine,
    [int]$TimeoutSec = 60,
    [switch]$AllowTimeout
  )

  Write-Host "`n=== COSTED: $Family $Route ===" -ForegroundColor Cyan

  $args = @(
    $RUNNER,
    "--family", $Family,
    "--route", $Route,
    "--request-text", $RequestText,
    "--timeout-sec", "$TimeoutSec"
  )

  if ($AllowTimeout) {
    $args += "--allow-timeout"
  }

  $args += @("--", "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $CommandLine)

  python @args
  $exit = $LASTEXITCODE

  if ($exit -ne 0) {
    Write-Host "COSTED_EXIT=$exit route=$Route" -ForegroundColor Yellow
  }

  return $exit
}

Set-Location $X108

Stop-ObsidiaLiveStack

Write-Host "`n=== START NEO4J DOCKER 7475/7688 ===" -ForegroundColor Cyan
try {
  docker start deploy-neo4j-1 | Out-Host
} catch {
  Write-Host "Neo4j Docker start skipped/failed. Continuing." -ForegroundColor Yellow
}
Start-Sleep -Seconds 3

Write-Host "`n=== START KERNEL RAGNAROK 3001 ===" -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$RT'; [Console]::Title='RAGNAROK KERNEL 3001 - LIVE COST METRICS'; node .\server.kernel.sealed.cjs"
)
$kernelReady = Wait-Port -Port 3001 -TimeoutSec 45

Write-Host "`n=== START API OBSIDIA/BRODY 8000 ===" -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$X108'; [Console]::Title='OBSIDIA API 8000 - LIVE COST METRICS'; `$env:PYTHONPATH='$X108'; `$env:OBSIDIA_KERNEL_URL='$KERNEL_URL'; python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
)
$apiPortReady = Wait-Port -Port 8000 -TimeoutSec 60
$apiReady = Wait-Http -Url "$API/" -TimeoutSec 45

Write-Host "`n=== START GRAPHITI / OBSIDIASHELL 8011 ===" -ForegroundColor Cyan
if (Test-Path $SHELL) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$SHELL'; [Console]::Title='GRAPHITI 8011 - LIVE COST METRICS'; `$env:PYTHONPATH='$SHELL'; python -m uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011 --log-level warning"
  )
  $graphPortReady = Wait-Port -Port 8011 -TimeoutSec 45
  $graphReady = Wait-Http -Url "$GRAPH/graph/v20/frozen/status" -TimeoutSec 45
} else {
  Write-Host "SHELL path missing: $SHELL" -ForegroundColor Yellow
  $graphReady = $false
}

Write-Host "`n=== START UI WORKBENCH 5173 ===" -ForegroundColor Cyan
if (Test-Path $UI_DIR) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$UI_DIR'; [Console]::Title='UI 5173 - LIVE COST METRICS'; npm run dev -- --host 127.0.0.1 --port 5173"
  )
  $uiPortReady = Wait-Port -Port 5173 -TimeoutSec 60
} else {
  Write-Host "UI path missing: $UI_DIR" -ForegroundColor Yellow
  $uiPortReady = $false
}

Write-Host "`n=== OPENAPI LIVE ROUTE CHECK ===" -ForegroundColor Cyan
try {
  $openapi = Invoke-RestMethod "$API/openapi.json" -TimeoutSec 20
  $openapi.paths.PSObject.Properties |
    Where-Object { $_.Name -match "/api/live/kernel/adapters|/api/brody/chat" } |
    Select-Object Name |
    Format-Table -AutoSize
} catch {
  Write-Host "OPENAPI CHECK FAILED" -ForegroundColor Yellow
}

Write-Host "`n=== RUN LIVE COST METRICS ===" -ForegroundColor Green

Run-Costed `
  -Family "RUNTIME_API" `
  -Route "/" `
  -RequestText "API root live cost metric" `
  -CommandLine "Invoke-RestMethod '$API/' -TimeoutSec 20 | ConvertTo-Json -Depth 8" `
  -TimeoutSec 30 | Out-Host

Run-Costed `
  -Family "BRODY_CHAT" `
  -Route "/api/brody/chat" `
  -RequestText "Brody live chat cost metric" `
  -CommandLine "`$BodyObj=@{message='Test Brody live cost metric.';mode='live_cost_metrics_v0';compact=`$true}; `$BodyJson=`$BodyObj|ConvertTo-Json -Depth 10 -Compress; Invoke-RestMethod -Uri '$API/api/brody/chat' -Method POST -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes(`$BodyJson)) -TimeoutSec 30 | ConvertTo-Json -Depth 8" `
  -TimeoutSec 45 | Out-Host

if ($graphReady) {
  Run-Costed `
    -Family "BRODY_MEMORY" `
    -Route "/graph/v20/frozen/status" `
    -RequestText "Graphiti live status cost metric" `
    -CommandLine "Invoke-RestMethod '$GRAPH/graph/v20/frozen/status' -TimeoutSec 20 | ConvertTo-Json -Depth 8" `
    -TimeoutSec 30 | Out-Host
}

if ($uiPortReady) {
  Run-Costed `
    -Family "RUNTIME_API" `
    -Route "UI_WORKBENCH_5173" `
    -RequestText "UI workbench live cost metric" `
    -CommandLine "(Invoke-WebRequest '$UI' -UseBasicParsing -TimeoutSec 20).StatusCode" `
    -TimeoutSec 30 | Out-Host
}

Run-Costed `
  -Family "DOMAIN_BANK" `
  -Route "/api/live/kernel/adapters/bank" `
  -RequestText "Bank connector live cost metric" `
  -CommandLine "cd '$X108'; `$env:PYTHONPATH='$X108'; `$env:OBSIDIA_API_BASE='$API'; python .\connectors\bank_normal_flow.py" `
  -TimeoutSec 75 `
  -AllowTimeout | Out-Host

Run-Costed `
  -Family "DOMAIN_TRADING" `
  -Route "/api/live/kernel/adapters/trading" `
  -RequestText "Trading connector live cost metric" `
  -CommandLine "cd '$X108'; `$env:PYTHONPATH='$X108'; `$env:OBSIDIA_API_BASE='$API'; python .\connectors\trading_live.py" `
  -TimeoutSec 75 `
  -AllowTimeout | Out-Host

Run-Costed `
  -Family "DOMAIN_GPS_AVIATION" `
  -Route "/api/live/kernel/adapters/gps" `
  -RequestText "GPS Aviation connector live cost metric" `
  -CommandLine "cd '$X108'; `$env:PYTHONPATH='$X108'; `$env:OBSIDIA_API_BASE='$API'; python .\connectors\aviation_robo.py" `
  -TimeoutSec 75 `
  -AllowTimeout | Out-Host

Write-Host "`n=== FINAL LIVE PORTS ===" -ForegroundColor Cyan
netstat -ano | Select-String ":3001|:8000|:8011|:5173|:7475|:7688" | Out-Host

Write-Host "`n=== LATEST COST EVENTS ===" -ForegroundColor Cyan
Get-Content "$X108\.local_reports\REQUEST_COST_EVENTS\cost_events.jsonl" -Tail 20

Write-Host "`nLIVE_STACK_COST_METRICS_DONE" -ForegroundColor Green
