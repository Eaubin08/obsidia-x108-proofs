# Gencoin — Not a Token Policy V1

**Status:** FIRST_CLASS_X108_MODULE — ABSOLUTE INVARIANT
**Role:** Declares and enforces that Gencoin is a ledger-only system, never a blockchain token.
**Module:** `periphery/blockchain/token_policy.py` (Gencoin clause)
**Gate:** BLOCK (absolute)

## The Invariant

**Gencoin is NOT a real token.** It operates as an append-only ledger within the X-108 governance perimeter. Value is assigned post-proof, never through minting. No smart contract, no blockchain deployment, no token standard (ERC-20, etc.).

## Enforcement

In `token_policy.py`, the `is_gencoin` flag triggers an absolute block:

```python
if is_gencoin:
    return TokenPolicyDecision(
        gate="BLOCK",
        reason="GENCOIN_IS_NOT_A_REAL_TOKEN_LEDGER_ONLY",
        mint_allowed=False,
        real_token_created=False,
        smart_contract_created=False,
    )
```

## How Gencoin Works (Instead)

1. **Action passes X108 → ALLOW gate**
2. **OS3 proof ticket is generated**
3. **ProofOfGovernance validates**
4. **Gencoin ledger appends** the action with computed value
5. **Value = 0 if**: X108 ≠ ALLOW, OS3 invalid, FALSE_ON dominant, assisted dominant, truth low

## What Gencoin Is NOT

| NOT | Because |
|-----|---------|
| ERC-20 token | No smart contract, no blockchain deployment |
| Cryptocurrency | No minting, no mining, no trading |
| DeFi asset | No liquidity pools, no staking, no lending |
| Transferable token | Ledger-only, no wallet-to-wallet transfers |
| Speculative asset | Value is proof-derived, not market-derived |

## Tests

- `tests/periphery/test_gencoin_not_token_policy.py`
- `tests/periphery/test_token_policy.py`
- `tests/non_sovereignty/test_no_token_mint.py`

## Status

**GENCOIN_NOT_TOKEN_PASS** — Absolute invariant. Never broken.
