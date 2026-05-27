param(
  [string]$Base = "http://127.0.0.1:8012"
)

$ErrorActionPreference = "Stop"

$ROOT = Split-Path $PSScriptRoot -Parent
$OUT = Join-Path $ROOT "_BRODY_RECONNECT_WORK\PHASE_4A_REVISED_SMOKE"
New-Item -ItemType Directory -Force -Path $OUT | Out-Null

Write-Host "BRODY_CONNECTORS_STATUS_SMOKE"
Write-Host "BASE=$Base"

$paths = @(
  "/api/memory/status",
  "/api/memory/sources",
  "/api/graphiti/status",
  "/api/graphiti/metrics",
  "/api/graphiti/readiness"
)

foreach ($p in $paths) {
  Write-Host "`n--- GET $p ---"
  try {
    $r = Invoke-RestMethod "$Base$p" -Method GET -TimeoutSec 20
    $r | ConvertTo-Json -Depth 20 | Tee-Object "$OUT\GET_$($p.Trim('/').Replace('/','_')).json"
  } catch {
    Write-Host "CONNECTOR_STATUS_FAIL $p :: $($_.Exception.Message)"
  }
}

Write-Host "`nDocker context:"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}" 2>$null | Tee-Object "$OUT\docker_ps.txt"

Write-Host "`nGit context:"
git status -sb | Tee-Object "$OUT\git_status_short.txt"
git log -1 --oneline | Tee-Object "$OUT\git_head.txt"
