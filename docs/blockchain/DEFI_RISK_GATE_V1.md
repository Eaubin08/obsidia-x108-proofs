# DeFi Risk Gate V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Evaluates risk of DeFi protocol interactions.
**Module:** `periphery/blockchain/defi_risk_gate.py`
**Gate:** HOLD (default)

## Role

The DeFi Risk Gate evaluates the risk profile of any proposed DeFi interaction — lending, borrowing, staking, liquidity provision, yield farming. All DeFi actions are held for review by default.

## Inputs

- `protocol_id: str` — DeFi protocol identifier
- `action_type: str` — LEND, BORROW, STAKE, PROVIDE_LIQUIDITY, etc.
- `pool_address: str | None` — liquidity pool address
- `token_pair: tuple[str, str] | None` — token pair
- `amount_usd: float` — amount in USD

## Outputs

- `DefiRiskDecision` with fields:
  - `gate: str` — HOLD or BLOCK
  - `risk_score: float` — 0.0 to 1.0
  - `risk_flags: list[str]`
  - `real_defi_action_allowed: bool` — always False

## Forbidden Actions

| Action | Status |
|--------|--------|
| Any DeFi action | HOLD — requires review |
| Real DeFi execution | BLOCKED — real_defi_action_allowed=False |

## Relation to Gencoin

Gencoin is not a DeFi token. It does not participate in lending, staking, or liquidity pools. Any DeFi action involving Gencoin is blocked at the token policy layer first.

## Tests

- Existing test coverage in `tests/periphery/test_blockchain_*.py`

## Status

**DRY_RUN_ONLY** — No real DeFi interaction. All actions require review.
