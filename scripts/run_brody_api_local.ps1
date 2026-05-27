param(
  [int]$Port = 8012,
  [string]$HostAddr = "127.0.0.1"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ROOT = Split-Path $PSScriptRoot -Parent
Set-Location $ROOT

Write-Host "BRODY_API_LOCAL_START"
Write-Host "ROOT=$ROOT"
Write-Host "URL=http://$HostAddr`:$Port"
Write-Host "APP=apps.obsidia_api.main:app"

python -m uvicorn apps.obsidia_api.main:app --host $HostAddr --port $Port
