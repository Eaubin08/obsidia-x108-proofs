# TEST_FEEDBACK_MEMORY_CANDIDATE.ps1
# Runs feedback memory bridge tests.
# Invariant: memory_write_allowed=False always.

Write-Host "=== Obsidia X-108 — Feedback Memory Candidate ===" -ForegroundColor Cyan

Set-Location $PSScriptRoot

Write-Host "`n[1/2] Feedback memory readonly tests..." -ForegroundColor Yellow
python -m pytest tests/periphery/test_feedback_memory_bridge_readonly.py tests/non_sovereignty/test_feedback_memory_no_write_v3.py -v
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`n[2/2] Demo connector: feedback_memory_candidate_flow..." -ForegroundColor Yellow
python "Demo-obsidia-x108-proof/connectors/feedback_memory_candidate_flow.py"
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`n=== ALL PASSED — memory_write_allowed=False always ===" -ForegroundColor Green
