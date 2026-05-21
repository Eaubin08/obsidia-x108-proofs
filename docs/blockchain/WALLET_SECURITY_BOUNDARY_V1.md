# Wallet Security Boundary V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Absolute block on wallet connection, private key access, seed phrase exposure.
**Module:** `periphery/blockchain/wallet_security_gate.py`
**Gate:** BLOCK (absolute)

## Role

The Wallet Security Gate is the first and most critical blockchain security module. It blocks any request involving private keys, seed phrases, mnemonics, or wallet connections before they reach any other layer.

## Inputs

- `request_id: str` — unique request identifier
- `request_type: str` — the type of wallet request
- `payload: dict | None` — optional request payload

## Outputs

- `WalletSecurityDecision` with fields:
  - `blocked: bool` — True if request is blocked
  - `private_key_requested: bool` — True if private key was in request
  - `seed_phrase_requested: bool` — True if seed phrase was in request
  - `wallet_connect_requested: bool` — True if wallet connect was requested
  - `real_wallet_access_allowed: bool` — ALWAYS False in V4

## Blocked Keywords (absolute)

```
private_key, privatekey, secret_key, secretkey,
seed_phrase, seedphrase, mnemonic, keystore,
wallet_connect, walletconnect
```

## Forbidden Actions

| Request contains | Result |
|-----------------|--------|
| private_key / secret_key | BLOCK — PRIVATE_KEY_REQUESTED_ABSOLUTE_BLOCK |
| seed_phrase / mnemonic | BLOCK — SEED_PHRASE_REQUESTED_ABSOLUTE_BLOCK |
| wallet_connect / connect_wallet | BLOCK — WALLET_CONNECT_BLOCKED_V4 |
| None of above | ALLOW — WALLET_READ_ADVISORY_ONLY (but real_wallet_access_allowed=False) |

## Relation to X108

The wallet gate runs before X108 evaluation. A blocked wallet request never reaches X108. This is a hard security boundary, not a governance decision.

## Relation to OS3

Blocked wallet requests are logged as evidence refs in the OS3 proof chain with reason codes.

## Relation to SovereignTicket

A wallet connect request without a SovereignTicket is blocked at the gateway level before reaching the wallet security gate.

## Relation to Gencoin

Wallet access is never required for Gencoin. Gencoin operates entirely off-chain as a ledger-only system.

## Tests

- `tests/periphery/test_wallet_security_gate.py`
- `tests/non_sovereignty/test_no_private_key_access.py`
- `tests/non_sovereignty/test_no_wallet_connection.py`

## Status

**BLOCK (absolute)** — No real wallet access. No key storage. No signing. Ever.
