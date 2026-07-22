param(
  [string]$Repo = "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B",
  [int]$LatestN = 50
)

Set-Location $Repo

Write-Host "`n=== OBSIDIA / X108 — STATUS STACK ===" -ForegroundColor Cyan

powershell -ExecutionPolicy Bypass -File "$Repo\scripts\runtime\check_obsidia_stack.ps1" -LatestN $LatestN
