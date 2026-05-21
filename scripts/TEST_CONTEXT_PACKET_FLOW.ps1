# TEST_CONTEXT_PACKET_FLOW.ps1 — Context packet + X-108 boundary tests
Set-Location $PSScriptRoot\..
python -m pytest tests/periphery/test_context_packet_builder.py `
               tests/periphery/test_x108_readonly_context_ingress.py `
               -v --tb=short
python connectors/context_packet_flow.py
