param(
  [string]$Base = "http://127.0.0.1:8012"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ROOT = Split-Path $PSScriptRoot -Parent
$OUT = Join-Path $ROOT "_BRODY_RECONNECT_WORK\PHASE_4A_REVISED_SMOKE"
New-Item -ItemType Directory -Force -Path $OUT | Out-Null

Write-Host "BRODY_ROUTES_SMOKE"
Write-Host "BASE=$Base"

$openapi = Invoke-RestMethod "$Base/openapi.json" -Method GET -TimeoutSec 20
$routes = $openapi.paths.PSObject.Properties.Name | Sort-Object
$routes | Set-Content -Encoding UTF8 "$OUT\openapi_routes.txt"

$expected = @(
  "/api/brody/chat",
  "/api/context/from-message",
  "/api/memory",
  "/api/memory/status",
  "/api/memory/sources",
  "/api/memory/candidates",
  "/api/memory/candidate/from-message",
  "/api/memory/candidate-ledger",
  "/api/memory/promotion-policy",
  "/api/graphiti/status",
  "/api/graphiti/context",
  "/api/graphiti/search",
  "/api/graphiti/metrics",
  "/api/graphiti/readiness",
  "/api/periphery/brody/context-query",
  "/api/periphery/brody/language-route",
  "/api/periphery/brody/double-brain-route",
  "/api/periphery/brody/diffusion-mix"
)

$missing = @()
foreach ($r in $expected) {
  if ($routes -notcontains $r) {
    $missing += $r
  }
}

if ($missing.Count -gt 0) {
  $missing | Set-Content -Encoding UTF8 "$OUT\missing_routes.txt"
  Write-Host "BRODY_ROUTES_SMOKE_FAIL"
  $missing
  exit 2
}

Write-Host "BRODY_ROUTES_SMOKE_OK"
$routes | Where-Object { $_ -match "brody|memory|graphiti|context" }
