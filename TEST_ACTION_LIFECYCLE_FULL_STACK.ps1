# TEST_ACTION_LIFECYCLE_FULL_STACK.ps1
# Runs the action lifecycle integration tests and demo connector.
# Obsidia X-108 — dry-run only, no real egress.

Write-Host "=== Obsidia X-108 — Action Lifecycle Full Stack ===" -ForegroundColor Cyan

Set-Location $PSScriptRoot

Write-Host "`n[1/2] Integration: Sovereign Ticket + OS3 + PoG chain..." -ForegroundColor Yellow
python -m pytest tests/integration/test_v4_sovereign_ticket_os3_pog_chain.py -v
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`n[2/2] Demo connector: action_lifecycle_full_stack_flow..." -ForegroundColor Yellow
python "Demo-obsidia-x108-proof/connectors/action_lifecycle_full_stack_flow.py"
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`n=== ALL PASSED ===" -ForegroundColor Green
