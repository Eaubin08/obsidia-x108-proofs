# Blockchain Security Layer V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** First line of defense for any action touching a blockchain.
**Gate:** BLOCK (absolute for private key, seed phrase, wallet connect, signing)
**Runtime:** DRY_RUN_ONLY

## Role

The Blockchain Security Layer classifies every action that touches a blockchain domain and routes it through appropriate security gates. No blockchain action executes without passing through this layer.

## Inputs

- `ActionCandidate` (from `periphery.common`)
- Domain context (bank, trading, crypto, etc.)

## Outputs

- `BlockchainActionDecision` — classified action with gate recommendation
- Module-specific decisions (WalletSecurityDecision, TransactionSimulationResult, etc.)

## Forbidden Actions

| Action | Module | Gate |
|--------|--------|------|
| PRIVATE_KEY_REQUESTED | wallet_security_gate | BLOCK (absolute) |
| SEED_PHRASE_REQUESTED | wallet_security_gate | BLOCK (absolute) |
| WALLET_CONNECT_REQUESTED | wallet_security_gate | BLOCK (absolute) |
| SIGN_MESSAGE / ETH_SIGN | signature_boundary | BLOCK (absolute) |
| DEPLOY (without audit) | smart_contract_risk_gate | BLOCK |
| TOKEN_MINT | token_policy | BLOCK |
| BRIDGE_TRANSFER (mainnet) | bridge_risk_gate | BLOCK |

## Module Chain

```
ActionCandidate
  → BlockchainActionClassifier (classifies: CHAIN_READ_ONLY | WALLET_CONNECT_REQUEST | ...)
  → Domain-specific gate (wallet / tx / contract / token / bridge / oracle)
  → Sigma aggregator (BLOCK > HOLD > ALLOW)
  → X108 (sole decision authority)
  → OS3 proof ticket (input/output/trace/merkle hashes)
```

## Tests

- `tests/periphery/test_blockchain_action_classifier.py`
- `tests/periphery/test_wallet_security_gate.py`
- `tests/periphery/test_transaction_simulator_dryrun.py`
- `tests/periphery/test_signature_boundary_no_signing.py`
- `tests/periphery/test_smart_contract_risk_gate.py`
- `tests/periphery/test_token_policy.py`
- `tests/periphery/test_oracle_freshness_gate.py`
- `tests/periphery/test_bridge_risk_gate.py`
- `tests/non_sovereignty/test_no_private_key_access.py`
- `tests/non_sovereignty/test_no_wallet_connection.py`
- `tests/non_sovereignty/test_no_real_chain_tx.py`
- `tests/non_sovereignty/test_no_smart_contract_deploy.py`
- `tests/non_sovereignty/test_no_token_mint.py`
- `demos/local_flows/blockchain_security_dryrun_flow.py`

## Sovereignty

- `real_chain_action_allowed = False` — enforced in every module
- No module emits ACT
- No module stores private keys
- Decision authority: KX108_ONLY

## Status

**DRY_RUN_ONLY** — All blockchain operations are simulated. No real chain interaction.
