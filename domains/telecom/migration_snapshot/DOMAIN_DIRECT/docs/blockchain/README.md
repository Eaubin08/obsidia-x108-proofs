# Blockchain Security Layer

**Status:** FIRST_CLASS_X108_MODULE — DRY_RUN_ONLY
**Source:** `periphery/blockchain/` (11 modules)
**Tests:** `tests/periphery/test_blockchain_*.py` + `tests/non_sovereignty/test_blockchain_*.py`

## Modules

| Module | Role | Gate |
|--------|------|------|
| `blockchain_action_classifier.py` | Classifies blockchain actions (READ/CONNECT/DEPLOY/MINT) | BLOCK |
| `wallet_security_gate.py` | Blocks private key, seed phrase, wallet connect requests | BLOCK (absolute) |
| `transaction_simulator.py` | Simulates transactions — never broadcasts | DRY_RUN_ONLY |
| `signature_boundary.py` | Blocks all signing requests | BLOCK (absolute) |
| `smart_contract_risk_gate.py` | Blocks unaudited contract deployment | BLOCK |
| `token_policy.py` | Gencoin is NOT a real token; mint/deploy blocked | BLOCK |
| `bridge_risk_gate.py` | Blocks mainnet bridge transfers | BLOCK |
| `defi_risk_gate.py` | DeFi risk evaluation | HOLD |
| `oracle_freshness_gate.py` | Requires fresh oracle data (< 5 min) | HOLD |
| `chain_context.py` | Read-only chain environment descriptor | ALLOW (read) |
| `onchain_audit_packet.py` | Audit trail — append-only, never executes | DRY_RUN_ONLY |

## Sovereignty Invariants

- `real_chain_action_allowed = False` in all modules
- `real_wallet_access_allowed = False` in wallet security gate
- `real_tx_sent = False` in transaction simulator
- `real_bridge_allowed = False` in bridge risk gate
- `real_token_created = False` in token policy
- No module has decision authority (KX108_ONLY)
- No module emits ACT
- No module stores or reads private keys

## Relation to X108

All blockchain actions flow through: ActionCandidate → BlockchainActionClassifier → module-specific gate → X108 (Sigma aggregator). X108 is the sole decision authority. Periphery blockchain modules evaluate risk and recommend BLOCK/HOLD — they never ALLOW autonomously.

## Relation to OS3

Each blockchain action that passes X108 generates an OS3 proof ticket with input/output/trace/merkle hashes. The transaction simulator produces a dry-run result that feeds into the OS3 chain.

## Relation to SovereignTicket

Blockchain actions that would constitute world calls require a SovereignTicket. No SovereignTicket → no blockchain world call.

## Relation to Gencoin

Gencoin is NOT a real token. The token_policy module explicitly blocks all MINT/DEPLOY/CREATE actions for Gencoin (`is_gencoin=True` → gate=BLOCK, mint_allowed=False). Gencoin value is computed post-proof, never on-chain.

## Backlog V5

- DeFi risk gate: module exists, tests exist — needs dedicated doc
- On-chain audit packet: module exists — needs dedicated doc and tests
