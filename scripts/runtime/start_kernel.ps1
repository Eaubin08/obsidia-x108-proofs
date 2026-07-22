param(
  [string]$Repo = "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"
)

Set-Location $Repo
chcp 65001 | Out-Null

$env:PYTHONPATH = $Repo
$env:PYTHONIOENCODING = "utf-8"
$env:OBSIDIA_TERMINAL_COLOR = "1"

Write-Host "`n=== OBSIDIA / X108 — START KERNEL 3001 ===" -ForegroundColor Cyan
Write-Host "Repo=$Repo" -ForegroundColor Gray
Write-Host "Command=node runtime_terrain_bank_trading_gps\server.kernel.sealed.cjs" -ForegroundColor Gray

node runtime_terrain_bank_trading_gps\server.kernel.sealed.cjs
