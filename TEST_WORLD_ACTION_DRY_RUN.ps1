# TEST_WORLD_ACTION_DRY_RUN.ps1
# Runs world action gateway and dry-run stub tests.
# Invariant: egress_allowed=False, dry_run_only=True always.

Write-Host "=== Obsidia X-108 — World Action Dry-Run ===" -ForegroundColor Cyan

Set-Location $PSScriptRoot

Write-Host "`n[1/3] Gateway pipeline tests..." -ForegroundColor Yellow
python -m pytest tests/integration/test_v4_world_call_gateway_pipeline.py -v
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`n[2/3] No-ticket/no-world-call tests..." -ForegroundColor Yellow
python -m pytest tests/periphery/test_no_ticket_no_world_call.py -v
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`n[3/3] Demo connector: world_action_dry_run_flow..." -ForegroundColor Yellow
python "Demo-obsidia-x108-proof/connectors/world_action_dry_run_flow.py"
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`n=== ALL PASSED — egress_allowed=False always ===" -ForegroundColor Green
