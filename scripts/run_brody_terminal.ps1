param(
  [string]$Base = "http://127.0.0.1:8012",
  [string]$SessionId = "brody_terminal_local"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "BRODY_TERMINAL_READONLY"
Write-Host "BASE=$Base"
Write-Host "SESSION_ID=$SessionId"
Write-Host "Commands: :quit, :boundary, :who"

while ($true) {
  $msg = Read-Host "brody>"
  if ($msg -eq ":quit") { break }

  if ($msg -eq ":boundary") {
    Write-Host "decision_authority=KX108_ONLY"
    Write-Host "emits_act=false"
    Write-Host "emits_verdict=false"
    Write-Host "memory_write=false"
    Write-Host "graphiti_write=false"
    continue
  }

  if ($msg -eq ":who") {
    $msg = "Qui es-tu Brody ? Réponds en français naturel, readonly, sans action."
  }

  $payload = @{
    message = $msg
    session_id = $SessionId
    compact = $false
    debug = $true
  } | ConvertTo-Json -Depth 20

  $bytes = [System.Text.Encoding]::UTF8.GetBytes($payload)

  try {
    $r = Invoke-WebRequest -Uri "$Base/api/brody/chat" -Method POST -ContentType "application/json; charset=utf-8" -Body $bytes -TimeoutSec 60
    $r.Content
  } catch {
    Write-Host "BRODY_TERMINAL_ERROR: $($_.Exception.Message)"
  }
}
