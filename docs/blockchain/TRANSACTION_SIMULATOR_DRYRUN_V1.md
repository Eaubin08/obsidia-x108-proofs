# Transaction Simulator — Dry-Run Only V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Simulates blockchain transactions without ever broadcasting to any chain.
**Module:** `periphery/blockchain/transaction_simulator.py`
**Runtime:** DRY_RUN_ONLY

## Role

The Transaction Simulator evaluates what WOULD happen if a transaction were sent — gas estimates, risk scores, cost projections — but NEVER broadcasts to any chain. It is a pure simulation tool.

## Inputs

- `tx_id: str` — transaction identifier
- `chain_id: str` — target chain (ethereum, polygon, etc.)
- `action_type: str` — transaction type (READ_ONLY, DEPLOY, TRANSFER, etc.)
- `value_eth: float` — transaction value in ETH (default 0.0)
- `gas_limit: int` — gas limit (default 21000)

## Outputs

- `TransactionSimulationResult` with fields:
  - `simulated: bool` — always True
  - `broadcast_attempted: bool` — always False
  - `real_tx_sent: bool` — always False
  - `estimated_gas: int` — gas estimate
  - `estimated_cost_usd: float` — cost projection
  - `risk_score: float` — 0.0 to 1.0
  - `risk_flags: list[str]` — detected risks
  - `simulation_status: str` — always "DRY_RUN_ONLY"

## Risk Escalation

| Condition | Risk Flag | Risk Score |
|-----------|-----------|------------|
| action_type = DEPLOY | CONTRACT_DEPLOY_HIGH_RISK | 0.9 |
| value_eth > 1.0 | HIGH_VALUE_TRANSFER | 0.7 |
| chain_id = mainnet/ethereum/1 | MAINNET_BLOCKED_V4 | 1.0 |

## Forbidden Actions

| Action | Status |
|--------|--------|
| broadcast_attempted | NEVER — always False |
| real_tx_sent | NEVER — always False |
| Mainnet transaction | BLOCKED — risk_score=1.0 |
| Contract deploy | HIGH_RISK — risk_score=0.9 |

## Relation to OS3

The simulation result feeds into the OS3 proof chain — input hash (tx params), output hash (simulation result), trace hash (execution path), merkle root.

## Tests

- `tests/periphery/test_transaction_simulator_dryrun.py`
- `tests/non_sovereignty/test_no_real_chain_tx.py`

## Status

**DRY_RUN_ONLY** — Never broadcasts. Never sends. Simulation only.
