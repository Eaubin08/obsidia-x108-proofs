# P2 Bank Security Fuzz Extended Scope

## Status

P2 BANK / SECURITY FUZZ / EXTENDED HOSTILE-INPUT PACK

## Purpose

This layer extends the first hostile-input pack with a broader deterministic fuzz corpus.

Covered:
- missing required fields
- unknown fields
- type confusion
- boundary values
- invalid paths
- replay stability
- mutation grid over suspicious profiles
- extreme valid hostile pressure

## Main rule

No malformed or hostile input should drift into unsafe ALLOW.
