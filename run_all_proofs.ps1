# run_all_proofs.ps1 — Lance tous les tests de preuve Obsidia X-108
$env:PYTHONIOENCODING = "utf-8"
$env:PATH += ";$env:USERPROFILE\bin;C:\Program Files\OpenSSL-Win64\bin"
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$TLC  = "$env:USERPROFILE\tla2tools.jar"
$LOGS = "$ROOT\formal\tla\tlc_results"
cd $ROOT

Write-Host "=== TLC X108_MC ===" -ForegroundColor Cyan
java -jar $TLC -config formal\tla\X108_MC.cfg formal\tla\X108_MC.tla 2>&1 | Tee-Object $LOGS\X108_MC_results.log | Select-String "No error|Error|states generated"

Write-Host "=== TLC DistributedX108 ===" -ForegroundColor Cyan
java -jar $TLC -config formal\tla\DistributedX108_MC.cfg formal\tla\DistributedX108.tla 2>&1 | Tee-Object $LOGS\DistributedX108_results.log | Select-String "No error|Error|states generated"

Write-Host "=== LEAN ===" -ForegroundColor Cyan
cd proofs\lean; lake build 2>&1 | Tee-Object $LOGS\lean_build.log; cd $ROOT

Write-Host "=== verify_all ===" -ForegroundColor Cyan
python proofs\verify_all.py 2>&1 | Tee-Object $LOGS\verify_all.log

Write-Host "=== verify_decision ===" -ForegroundColor Cyan
cd proofs
python verify_decision.py examples\bank_normal.json
python verify_decision.py examples\bank_suspicious.json
python verify_decision.py examples\scenarios\complete_decision_flow.json
cd $ROOT

Write-Host "=== DONE ===" -ForegroundColor Green
