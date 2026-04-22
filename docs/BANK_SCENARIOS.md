# Bank Scenarios

## Purpose

This file defines the canonical P2 Bank scenarios using the current public bank schema.

## Source anchors

These scenarios are derived from:
- `docs/sources/obsidia-engine-proof-core/REAL_CASES.md`
- `docs/sources/bank-robo/README.md`
- `docs/sources/bank-robo/bankingEngine.ts`

## Scenario 1 — Normal

File:
- `sigma/examples/bank_normal.json`

Profile:
- known counterparty
- mature elapsed time
- low contradiction profile
- low fraud profile

Expected reading:
- direct path admissible
- `x108_gate = ALLOW`
- Sigma stable

## Scenario 2 — Suspicious

File:
- `sigma/examples/bank_suspicious.json`

Profile:
- immature elapsed time
- high contradiction pressure
- high fraud pressure
- unstable trust profile

Expected reading:
- no direct authorization path
- current validated public build should not return `ALLOW`
- Sigma stable

## Scenario 3 — Blocked Hard

File:
- `sigma/examples/bank_blocked.json`

Profile:
- extreme contradiction profile
- extreme fraud pressure
- near-zero trust profile
- extreme temporal immaturity
- strongest public refusal profile in P2 Bank

Expected reading:
- `x108_gate = BLOCK`
- `severity = S4`
- Sigma stable

## Reading discipline

Do not reduce the interpretation to `market_verdict` alone.
The sovereign interpretation remains:
- `x108_gate`
