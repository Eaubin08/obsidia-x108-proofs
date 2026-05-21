# Signature Boundary — No Signing V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Absolute block on all cryptographic signing requests.
**Module:** `periphery/blockchain/signature_boundary.py`
**Gate:** BLOCK (absolute for all signing)

## Role

The Signature Boundary blocks any request involving cryptographic signing — SIGN_MESSAGE, ETH_SIGN, PERSONAL_SIGN, SIGN_TYPED_DATA, EIP712_SIGN, or any operation containing "SIGN" in the signature type. This is an absolute security boundary.

## Inputs

- `request_id: str` — unique request identifier
- `signature_type: str` — the type of signature requested

## Outputs

- `SignatureBoundaryDecision` with fields:
  - `blocked: bool` — True if signing is blocked
  - `signing_attempted: bool` — True if a signing operation was detected
  - `key_exposed: bool` — True if a key was exposed (should never be True)

## Always-Blocked Signature Types

```
SIGN_MESSAGE, SIGN_TRANSACTION, ETH_SIGN, PERSONAL_SIGN,
SIGN_TYPED_DATA, WALLET_SIGN, EIP712_SIGN
```

Plus any signature type containing "SIGN" (case-insensitive).

## Additional Protection: assert_no_private_key_in_payload

A separate function scans payloads for private key, seed phrase, or keystore keywords and raises `AssertionError` if found. This is a defense-in-depth measure beyond the signature boundary itself.

## Forbidden Actions

| Signature Type | Result |
|---------------|--------|
| SIGN_MESSAGE | BLOCK |
| ETH_SIGN / PERSONAL_SIGN | BLOCK |
| SIGN_TYPED_DATA / EIP712_SIGN | BLOCK |
| Any type containing "SIGN" | BLOCK |
| Non-signature type | ALLOW (advisory) |

## Relation to X108

The signature boundary is an absolute block — X108 has no discretion to override it. This is a security invariant, not a governance decision.

## Tests

- `tests/periphery/test_signature_boundary_no_signing.py`
- `tests/non_sovereignty/test_no_private_key_access.py`

## Status

**BLOCK (absolute)** — No signing. Ever.
