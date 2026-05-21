# TEST_MEMORY_ALL.ps1 — Full Memory/Brody/Graphiti/Interface layer suite
Set-Location $PSScriptRoot\..
python -m pytest tests/periphery/test_brody_runtime_readonly.py `
               tests/periphery/test_brody_response_contract.py `
               tests/periphery/test_memory_source_registry.py `
               tests/periphery/test_graphiti_readonly_bridge.py `
               tests/periphery/test_interface_state_packet.py `
               tests/non_sovereignty/test_brody_no_decision.py `
               tests/non_sovereignty/test_brody_no_act.py `
               tests/non_sovereignty/test_graphiti_no_write.py `
               tests/non_sovereignty/test_memory_promotion_not_automatic.py `
               -v --tb=short
