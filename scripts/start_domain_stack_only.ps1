# ============================================================
# OBSIDIA DOMAIN STACK ONLY
# Kernel Ragnarok 3001 + API 8000 + Bank / Trading / GPS
# No Neo4j / No Graphiti / No UI / No Brody terminal
# ============================================================

$REPO = if ($env:OBSIDIA_REPO_ROOT) { $env:OBSIDIA_REPO_ROOT } else { Split-Path -Parent $PSScriptRoot }
$RT = "$REPO\runtime_terrain_bank_trading_gps"

$API = "http://127.0.0.1:8000"
$KERNEL_URL = "http://127.0.0.1:3001/kernel/ragnarok"

Set-Location $REPO

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "STOP DOMAIN STACK ONLY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "server.kernel.sealed.cjs" -or
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "connectors\\bank_normal_flow.py" -or
    $_.CommandLine -match "connectors\\trading_live.py" -or
    $_.CommandLine -match "connectors\\aviation_robo.py"
  } |
  ForEach-Object {
    Write-Host "Stopping PID=$($_.ProcessId)" -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }

foreach ($port in @(3001, 8000)) {
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

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START KERNEL RAGNAROK 3001" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$RT'; [Console]::Title='RAGNAROK KERNEL 3001 - DOMAIN AUTHORITY'; node .\server.kernel.sealed.cjs"
)

Start-Sleep -Seconds 5

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START OBSIDIA API 8000" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$REPO'; [Console]::Title='OBSIDIA API 8000 - LIVE KERNEL BRIDGE'; `$env:PYTHONPATH='$REPO'; `$env:OBSIDIA_KERNEL_URL='$KERNEL_URL'; python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 8

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "CHECK API + LIVE ROUTES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  Invoke-RestMethod "$API/" -TimeoutSec 10 | ConvertTo-Json -Depth 8
} catch {
  Write-Host "API 8000 NOT READY" -ForegroundColor Red
}

try {
  $openapi = Invoke-RestMethod "$API/openapi.json" -TimeoutSec 10
  $openapi.paths.PSObject.Properties |
    Where-Object { $_.Name -match "/api/live/kernel/adapters" } |
    Select-Object Name |
    Format-Table -AutoSize
} catch {
  Write-Host "OPENAPI ROUTES CHECK FAILED" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START DOMAIN CONNECTORS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$REPO'; [Console]::Title='BANK LIVE -> KERNEL'; `$env:PYTHONPATH='$REPO'; `$env:OBSIDIA_API_BASE='$API'; python .\connectors\bank_normal_flow.py"
)

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$REPO'; [Console]::Title='TRADING LIVE -> KERNEL'; `$env:PYTHONPATH='$REPO'; `$env:OBSIDIA_API_BASE='$API'; python .\connectors\trading_live.py"
)

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$REPO'; [Console]::Title='GPS AVIATION LIVE -> KERNEL'; `$env:PYTHONPATH='$REPO'; `$env:OBSIDIA_API_BASE='$API'; python .\connectors\aviation_robo.py"
)

Start-Sleep -Seconds 5

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "FINAL DOMAIN STACK CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

netstat -ano | findstr ":3001"
netstat -ano | findstr ":8000"

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "server.kernel.sealed.cjs" -or
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "connectors\\bank_normal_flow.py" -or
    $_.CommandLine -match "connectors\\trading_live.py" -or
    $_.CommandLine -match "connectors\\aviation_robo.py"
  } |
  Select-Object ProcessId, Name, CommandLine |
  Format-Table -AutoSize

Write-Host "`nDOMAIN STACK READY" -ForegroundColor Green
Write-Host "Kernel : http://127.0.0.1:3001"
Write-Host "API    : http://127.0.0.1:8000"
Write-Host "Expected kernel logs: BANK / TRADING / GPS" -ForegroundColor Green
