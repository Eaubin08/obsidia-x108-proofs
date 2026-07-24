param(
  [string]$Repo = "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B",
  [int]$Port = 8000
)

Set-Location $Repo
chcp 65001 | Out-Null

$env:PYTHONPATH = $Repo
$env:PYTHONIOENCODING = "utf-8"
$env:OBSIDIA_TERMINAL_COLOR = "1"

Write-Host "`n=== OBSIDIA / X108 — START API $Port ===" -ForegroundColor Cyan
Write-Host "Repo=$Repo" -ForegroundColor Gray
Write-Host "Command=python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port $Port" -ForegroundColor Gray

python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port $Port
