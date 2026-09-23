# Bridge Risk Gate V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Blocks cross-chain bridge transfers, especially to/from mainnet.
**Module:** `periphery/blockchain/bridge_risk_gate.py`
**Gate:** BLOCK (mainnet), HOLD (unaudited bridges)

## Role

The Bridge Risk Gate evaluates the risk of cross-chain bridge operations. All mainnet bridge transfers are absolutely blocked. Unaudited bridges and unverified liquidity trigger HOLD.

## Inputs

- `bridge_id: str` — bridge identifier
- `source_chain: str` — source chain
- `dest_chain: str` — destination chain
- `bridge_audited: bool` — whether the bridge has been audited
- `liquidity_verified: bool` — whether bridge liquidity is verified

## Outputs

- `BridgeRiskDecision` with fields:
  - `gate: str` — BLOCK, HOLD, or ALLOW
  - `risk_score: float` — 0.5 to 1.0
  - `risk_flags: list[str]`
  - `real_bridge_allowed: bool` — always False

## Risk Escalation

| Condition | Flag | Risk Score | Gate |
|-----------|------|------------|------|
| source or dest = mainnet/ethereum/1 | MAINNET_BRIDGE_BLOCKED_V4 | 1.0 | BLOCK |
| bridge_audited=False | BRIDGE_RISK_UNEVALUATED | 0.8 | HOLD |
| liquidity_verified=False | BRIDGE_LIQUIDITY_UNVERIFIED | 0.6 | HOLD |
| No flags | — | 0.5 | ALLOW |

## Forbidden Actions

| Action | Condition | Status |
|--------|-----------|--------|
| Mainnet bridge transfer | source/dest = ethereum/1 | BLOCKED |
| Unaudited bridge | bridge_audited=False | HOLD |
| Real bridge execution | Always | BLOCKED — real_bridge_allowed=False |

## Tests

- `tests/periphery/test_bridge_risk_gate.py`

## Status

**DRY_RUN_ONLY** — No real bridge transfers. Mainnet bridges absolutely blocked.
