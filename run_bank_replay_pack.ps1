param(
    [int]$Size = 10000,
    [int]$Workers = 6
)

$ErrorActionPreference = "Stop"

Write-Host "=== P2 BANK / REPLAY RUNNER ===" -ForegroundColor Cyan
python .\sigma\tools\run_bank_replay_pack.py --size $Size --workers $Workers
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($Size -eq 10000) {
    Write-Host "`n=== P2 BANK / REPLAY TESTS (10K) ===" -ForegroundColor Cyan
    python -W ignore -m pytest .\sigma\tests\test_bank_replay_pack_10k.py -v
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host "`n=== P2 BANK / REPLAY RESULTS DOC ===" -ForegroundColor Cyan
python .\sigma\tools\generate_bank_replay_results_doc.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== DONE / P2 BANK / REPLAY PACK ===" -ForegroundColor Green