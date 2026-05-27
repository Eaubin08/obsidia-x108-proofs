param(
  [string]$Base = "http://127.0.0.1:8012"
)

$ErrorActionPreference = "Stop"

$ROOT = Split-Path $PSScriptRoot -Parent
$OUT = Join-Path $ROOT "_BRODY_RECONNECT_WORK\PHASE_5E_GRAPHITI_PROXY_SMOKE"
New-Item -ItemType Directory -Force -Path $OUT | Out-Null

Write-Host "GRAPHITI_V20_PROXY_SMOKE"
Write-Host "BASE=$Base"

$paths = @(
  "/api/graphiti/status",
  "/api/graphiti/readiness",
  "/api/graphiti/metrics",
  "/api/graphiti/context?q=Brody&limit=5",
  "/api/graphiti/search?q=Brody&limit=5"
)

foreach ($p in $paths) {
  Write-Host "`n--- GET $p ---"
  $safe = $p.Trim('/').Replace('/','_').Replace('?','_').Replace('&','_').Replace('=','_')
  $r = Invoke-RestMethod "$Base$p" -Method GET -TimeoutSec 10
  $r | ConvertTo-Json -Depth 50 | Tee-Object "$OUT\GET_$safe.json"

  $json = $r | ConvertTo-Json -Depth 50
  if ($json -notmatch "KX108_ONLY") {
    throw "Missing KX108_ONLY in $p"
  }
  if ($json -match '"emits_act"\s*:\s*true|"emits_verdict"\s*:\s*true|"graphiti_write"\s*:\s*true|"neo4j_write"\s*:\s*true') {
    throw "Readonly boundary violation in $p"
  }
}

Write-Host "`nGRAPHITI_V20_PROXY_SMOKE_DONE"
