# TEST_INTERFACE_READY_MEMORY.ps1 — Interface state packet + view contracts tests
Set-Location $PSScriptRoot\..
python -m pytest tests/periphery/test_interface_state_packet.py `
               tests/periphery/test_graphiti_readonly_bridge.py `
               tests/non_sovereignty/test_graphiti_no_write.py `
               -v --tb=short
python connectors/interface_ready_memory_flow.py
