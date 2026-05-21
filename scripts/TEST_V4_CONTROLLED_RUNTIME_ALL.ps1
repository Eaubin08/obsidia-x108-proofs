# TEST_V4_CONTROLLED_RUNTIME_ALL.ps1 — V4 controlled runtime tests
Set-Location $PSScriptRoot\..
Write-Host "=== V4 Controlled Runtime Tests ===" -ForegroundColor Cyan

python -m pytest tests/periphery/test_blockchain_action_classifier.py `
               tests/periphery/test_wallet_security_gate.py `
               tests/periphery/test_transaction_simulator_dryrun.py `
               tests/periphery/test_smart_contract_risk_gate.py `
               tests/periphery/test_token_policy.py `
               tests/periphery/test_oracle_freshness_gate.py `
               tests/periphery/test_bridge_risk_gate.py `
               tests/periphery/test_signature_boundary_no_signing.py `
               tests/periphery/test_gencoin_not_token_policy.py `
               tests/periphery/test_consciousness_regime_classifier.py `
               tests/periphery/test_consciousness_no_claim_policy.py `
               tests/periphery/test_collective_sandbox_summary.py `
               tests/non_sovereignty/test_no_private_key_access.py `
               tests/non_sovereignty/test_no_wallet_connection.py `
               tests/non_sovereignty/test_no_real_chain_tx.py `
               tests/non_sovereignty/test_no_smart_contract_deploy.py `
               tests/non_sovereignty/test_no_token_mint.py `
               -v --tb=short

Write-Host "=== Done ===" -ForegroundColor Cyan
