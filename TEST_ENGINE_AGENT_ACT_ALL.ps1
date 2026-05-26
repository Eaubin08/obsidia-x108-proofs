# TEST_ENGINE_AGENT_ACT_ALL.ps1
# Runs all non-sovereignty agent ACT constraint tests.
# Invariant: can_emit_act=False for ALL peripheral agents.

Write-Host "=== Obsidia X-108 — Engine Agent ACT Constraints ===" -ForegroundColor Cyan

Set-Location $PSScriptRoot

Write-Host "`n[1/4] Agents cannot emit ACT..." -ForegroundColor Yellow
python -m pytest tests/non_sovereignty/test_agents_cannot_emit_act.py -v
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`n[2/4] Feedback memory no write..." -ForegroundColor Yellow
python -m pytest tests/non_sovereignty/test_feedback_memory_no_write_v3.py -v
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`n[3/4] Gencoin no authority..." -ForegroundColor Yellow
python -m pytest tests/non_sovereignty/test_gencoin_no_authority_v3.py -v
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`n[4/4] World action no real ACT..." -ForegroundColor Yellow
python -m pytest tests/non_sovereignty/test_world_action_no_real_act_v4.py -v
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`n=== ALL PASSED — can_emit_act=False invariant verified ===" -ForegroundColor Green
