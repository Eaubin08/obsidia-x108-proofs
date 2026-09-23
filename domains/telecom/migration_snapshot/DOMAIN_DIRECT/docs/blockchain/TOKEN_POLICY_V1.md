# Token Policy V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Blocks all token minting, deployment, and creation. Gencoin is explicitly NOT a token.
**Module:** `periphery/blockchain/token_policy.py`
**Gate:** BLOCK (all token creation)

## Role

The Token Policy enforces the invariant that no real tokens are created within the Obsidia X-108 perimeter. Gencoin is explicitly defined as a ledger-only system, not a blockchain token. The policy blocks MINT, DEPLOY, CREATE, and any related actions.

## Inputs

- `token_id: str` — token identifier
- `action: str` — MINT, DEPLOY, CREATE, TRANSFER, etc.
- `is_gencoin: bool` — whether this token is Gencoin

## Outputs

- `TokenPolicyDecision` with fields:
  - `gate: str` — BLOCK, HOLD, or ALLOW
  - `mint_allowed: bool` — always False for blocked actions
  - `real_token_created: bool` — always False
  - `smart_contract_created: bool` — always False
  - `is_gencoin: bool`

## Blocked Token Actions

| Action | Condition | Gate | Reason |
|--------|-----------|------|--------|
| Any | is_gencoin=True | BLOCK | GENCOIN_IS_NOT_A_REAL_TOKEN_LEDGER_ONLY |
| MINT | — | BLOCK | TOKEN_ACTION_BLOCKED_V4:MINT |
| DEPLOY | — | BLOCK | TOKEN_ACTION_BLOCKED_V4:DEPLOY |
| CREATE | — | BLOCK | TOKEN_ACTION_BLOCKED_V4:CREATE |
| Other | — | HOLD | TOKEN_ACTION_REQUIRES_REVIEW |

## Gencoin Special Policy

When `is_gencoin=True`, the gate is always BLOCK with reason `GENCOIN_IS_NOT_A_REAL_TOKEN_LEDGER_ONLY`. Gencoin operates as an append-only ledger within X108, never as a blockchain token. Value is assigned post-proof, never through minting.

## Forbidden Actions

| Action | Status |
|--------|--------|
| Token mint | BLOCKED — mint_allowed=False |
| Token deploy | BLOCKED — smart_contract_created=False |
| Real token creation | BLOCKED — real_token_created=False |
| Gencoin tokenization | BLOCKED — absolute |

## Tests

- `tests/periphery/test_token_policy.py`
- `tests/periphery/test_gencoin_not_token_policy.py`
- `tests/non_sovereignty/test_no_token_mint.py`

## Status

**BLOCK (absolute)** — No real tokens. Gencoin is a ledger, not a token.
