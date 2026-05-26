# V5B — Start Obsidia API on port 8000
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "=== Obsidia X-108 API V5B ===" -ForegroundColor Cyan
Write-Host "Starting on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Endpoints:" -ForegroundColor Yellow
Write-Host "  GET  /api/status" -ForegroundColor White
Write-Host "  POST /api/brody/chat" -ForegroundColor White
Write-Host "  POST /api/translation/trace" -ForegroundColor White
Write-Host "  POST /api/context/from-message" -ForegroundColor White
Write-Host "  GET  /api/memory" -ForegroundColor White
Write-Host "  GET  /api/gencoin" -ForegroundColor White
Write-Host ""

python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000 --reload
