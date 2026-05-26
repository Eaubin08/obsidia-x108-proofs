# TEST_BRODY_MEMORY_READONLY.ps1 — Brody + Memory readonly layer tests
Set-Location $PSScriptRoot\..
python -m pytest tests/periphery/test_brody_runtime_readonly.py `
               tests/periphery/test_brody_response_contract.py `
               tests/periphery/test_memory_source_registry.py `
               tests/non_sovereignty/test_brody_no_decision.py `
               tests/non_sovereignty/test_brody_no_act.py `
               tests/non_sovereignty/test_memory_promotion_not_automatic.py `
               -v --tb=short
