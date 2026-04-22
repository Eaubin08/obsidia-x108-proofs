# run_all_proofs.ps1 - Lance les preuves publiques Obsidia X-108 (P1)
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:PYTHONWARNINGS = "ignore"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [Console]::OutputEncoding
chcp 65001 | Out-Null
$env:PATH += ";$env:USERPROFILE\bin;C:\Program Files\OpenSSL-Win64\bin"

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$TLC  = "$env:USERPROFILE\tla2tools.jar"
$LOGS = "$ROOT\formal\tla\tlc_results"

New-Item -ItemType Directory -Force -Path $LOGS | Out-Null
Set-Location $ROOT

if (Test-Path $TLC) {
    Write-Host "=== TLC X108_MC ===" -ForegroundColor Cyan
    java -jar $TLC -config formal\tla\X108_MC.cfg formal\tla\X108_MC.tla 2>&1 | Tee-Object $LOGS\X108_MC_results.log | Select-String "No error|Error|states generated"

    Write-Host "=== TLC DistributedX108 ===" -ForegroundColor Cyan
    java -jar $TLC -config formal\tla\DistributedX108_MC.cfg formal\tla\DistributedX108.tla 2>&1 | Tee-Object $LOGS\DistributedX108_results.log | Select-String "No error|Error|states generated"
}
else {
    Write-Host "=== TLC ===" -ForegroundColor Yellow
    Write-Host "tla2tools.jar not found in $TLC"
}

Write-Host "=== LEAN ===" -ForegroundColor Cyan
Set-Location "$ROOT\proofs\lean"
lake build 2>&1 | Tee-Object $LOGS\lean_build.log
Set-Location $ROOT

Write-Host "=== verify_all ===" -ForegroundColor Cyan
python proofs\verify_all.py 2>&1 | Tee-Object $LOGS\verify_all.log

Write-Host "=== verify_decision ===" -ForegroundColor Cyan
Set-Location "$ROOT\proofs"
python verify_decision.py examples\bank_normal.json
python verify_decision.py examples\bank_suspicious.json
python verify_decision.py examples\scenarios\complete_decision_flow.json
Set-Location $ROOT

Write-Host "=== SIGMA PUBLIC ===" -ForegroundColor Cyan
python sigma\run_pipeline.py bank sigma\examples\bank_normal.json 2>&1 | Tee-Object $LOGS\sigma_bank_normal.log
python sigma\run_pipeline.py bank sigma\examples\bank_suspicious.json 2>&1 | Tee-Object $LOGS\sigma_bank_suspicious.log
python sigma\sigma_monitor.py --json 2>&1 | Tee-Object $LOGS\sigma_monitor.log
python -W ignore -m pytest sigma\tests -v 2>&1 | Tee-Object $LOGS\sigma_tests.log

Write-Host "=== QA RFC3161 / TLC / SIGMA ===" -ForegroundColor Cyan
python qa\cross-platform\test_rfc3161_cross_platform.py 2>&1 | Tee-Object $LOGS\qa_rfc3161.log
python -W ignore -m pytest qa\cross-platform\test_rfc3161_anchor_schema.py -v 2>&1 | Tee-Object $LOGS\qa_rfc3161_anchor_schema.log

Write-Host "=== DONE ===" -ForegroundColor Green