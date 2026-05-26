# RUN_V4_CONTROLLED_RUNTIME_TESTS.ps1 — Obsidia X-108 Patch V4
# V4 Controlled Runtime test suite: all dry-run only.

Write-Host "=== OBSIDIA X-108 V4 CONTROLLED RUNTIME TESTS ===" -ForegroundColor Cyan
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

python -m compileall periphery -q
if ($LASTEXITCODE -ne 0) { Write-Host "PY_COMPILE_FAIL" -ForegroundColor Red; exit 1 }
Write-Host "PY_COMPILE_PASS" -ForegroundColor Green

python -m pytest tests/periphery/test_world_action_controlled_runtime_stub.py tests/periphery/test_gencoin_sandbox_engine.py tests/periphery/test_false_on_blocks_gencoin.py tests/periphery/test_balance_operator.py tests/periphery/test_avdr_phase_mapper.py -v --tb=short
if ($LASTEXITCODE -ne 0) { Write-Host "V4_TESTS_FAIL" -ForegroundColor Red; exit 1 }
Write-Host "V4_SANDBOX_TESTS_PASS" -ForegroundColor Green

python -m pytest tests/non_sovereignty/test_world_action_no_real_act_v4.py -v --tb=short
if ($LASTEXITCODE -ne 0) { Write-Host "V4_NON_SOVEREIGNTY_FAIL" -ForegroundColor Red; exit 1 }
Write-Host "V4_NON_SOVEREIGNTY_PASS" -ForegroundColor Green

python -m pytest tests/integration/test_v4_controlled_runtime_pipeline.py -v --tb=short
if ($LASTEXITCODE -ne 0) { Write-Host "V4_INTEGRATION_FAIL" -ForegroundColor Red; exit 1 }
Write-Host "V4_CONTROLLED_RUNTIME_PASS" -ForegroundColor Green

Write-Host "`n=== V4 CONTROLLED RUNTIME TESTS PASS ===" -ForegroundColor Cyan
