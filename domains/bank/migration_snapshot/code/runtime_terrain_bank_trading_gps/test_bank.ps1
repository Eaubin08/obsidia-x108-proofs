$json = Get-Content -Path "payload_bank.json" -Raw
Write-Host "🚀 Envoi du fichier payload_bank.json..." -ForegroundColor Cyan
Invoke-RestMethod -Method Post -Uri "http://localhost:3001/kernel/ragnarok" -ContentType "application/json" -Body $json | ConvertTo-Json
