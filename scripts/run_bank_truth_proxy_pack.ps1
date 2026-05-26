# run_bank_truth_proxy_pack.ps1
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:PYTHONWARNINGS = "ignore"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [Console]::OutputEncoding
chcp 65001 | Out-Null

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT

Write-Host "=== P2 BANK / TRUTH PROXY RUNNER ===" -ForegroundColor Cyan
python .\sigma\tools\run_bank_truth_proxy_pack.py
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n=== P2 BANK / TRUTH PROXY TESTS ===" -ForegroundColor Cyan
python -W ignore -m pytest .\sigma\tests\test_bank_truth_proxy_pack.py -v
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n=== DONE / P2 BANK / TRUTH PROXY PACK ===" -ForegroundColor Green
