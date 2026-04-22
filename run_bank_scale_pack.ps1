# run_bank_scale_pack.ps1
param(
    [ValidateSet(1000,10000,100000)]
    [int]$Size = 1000,
    [int]$Workers = 6
)

$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:PYTHONWARNINGS = "ignore"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [Console]::OutputEncoding
chcp 65001 | Out-Null

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT

Write-Host "=== P2 BANK / SCALE RUNNER ===" -ForegroundColor Cyan
python .\sigma\tools\run_bank_scale_pack.py --size $Size --workers $Workers
if ($LASTEXITCODE -ne 0) { exit 1 }

if ($Size -eq 1000) {
    Write-Host "`n=== P2 BANK / SCALE TESTS ===" -ForegroundColor Cyan
    python -W ignore -m pytest .\sigma\tests\test_bank_scale_pack.py -v
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

Write-Host "`n=== DONE / P2 BANK / SCALE PACK ===" -ForegroundColor Green
