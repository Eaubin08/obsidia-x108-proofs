param(
  [string]$HostAddr = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

$ROOT = Split-Path $PSScriptRoot -Parent
$APP = Join-Path $ROOT "apps\obsidia-workbench"

if (-not (Test-Path $APP)) {
  throw "Missing apps/obsidia-workbench"
}

Set-Location $APP

Write-Host "OBSIDIA_WORKBENCH_LOCAL_START"
Write-Host "ROOT=$ROOT"
Write-Host "APP=$APP"

if (-not (Test-Path "node_modules")) {
  Write-Host "node_modules missing; running npm ci"
  npm ci
}

npm run dev -- --host $HostAddr
