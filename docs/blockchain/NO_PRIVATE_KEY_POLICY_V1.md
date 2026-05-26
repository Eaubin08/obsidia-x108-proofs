# No Private Key Policy V1

**Status:** FIRST_CLASS_X108_MODULE — ABSOLUTE INVARIANT
**Role:** Absolute prohibition on storing, reading, requesting, or accessing any private key, seed phrase, or mnemonic.
**Modules:** `wallet_security_gate.py`, `signature_boundary.py`
**Gate:** BLOCK (absolute)

## The Invariant

**No private key, seed phrase, mnemonic, or keystore is ever stored, read, requested, or accessed by any Obsidia X-108 module.** This is an absolute security invariant with no exceptions and no override path.

## Enforcement Points

### Wallet Security Gate
Blocks any request containing: `private_key`, `secret_key`, `seed_phrase`, `mnemonic`, `keystore`, `wallet_connect`

### Signature Boundary
Blocks any signing request and separately scans payloads via `assert_no_private_key_in_payload()` for: `private_key`, `secret_key`, `seed_phrase`, `mnemonic`, `keystore`

### Non-Sovereignty Tests
- `test_no_private_key_access.py` — verifies no module can access private keys
- `test_no_wallet_connection.py` — verifies wallet connect is blocked
- `test_signature_boundary_blocks_all_signing.py` — verifies all signing is blocked

## Forbidden Actions

| Action | Blocked By | Gate |
|--------|-----------|------|
| private_key in request | wallet_security_gate | BLOCK |
| seed_phrase in request | wallet_security_gate | BLOCK |
| wallet_connect request | wallet_security_gate | BLOCK |
| SIGN_MESSAGE | signature_boundary | BLOCK |
| ETH_SIGN / PERSONAL_SIGN | signature_boundary | BLOCK |
| Private key in payload | assert_no_private_key_in_payload | AssertionError |

## Override

**NONE.** There is no mechanism for any module, agent, or human to override these blocks. They are absolute security invariants, not governance decisions.

## Tests

- `tests/non_sovereignty/test_no_private_key_access.py`
- `tests/non_sovereignty/test_no_wallet_connection.py`
- `tests/non_sovereignty/test_signature_boundary_blocks_all_signing.py`

## Status

**NO_PRIVATE_KEY_ACCESS_PASS** — Absolute invariant. Never broken.
