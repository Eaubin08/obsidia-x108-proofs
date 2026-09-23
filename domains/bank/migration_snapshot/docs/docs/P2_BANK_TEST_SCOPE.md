# P2 Bank Test Scope

## Status

P2 BANK TEST PACK OPENING

## Purpose

This document defines the first real robustness pack for P2 Bank.

P2 Bank opening already proved:
- a first governed business world exists
- canonical bank scenarios can be executed
- public outputs are readable

This pack adds stronger technical evidence for market-facing discussions.

## What this pack tests

### 1. Canonical baselines
The 3 canonical public bank cases remain valid:
- normal
- suspicious
- blocked hard

### 2. Temporal maturity behavior
The direct path must not become softer when temporal maturity is reduced on the same risky profile.

### 3. Risk escalation monotonicity
When selected risk variables worsen, the sovereign gate must not become softer.

### 4. Trust degradation monotonicity
When trust indicators degrade, the sovereign gate must not become softer.

### 5. Batch reproducibility
A multi-case batch must remain executable and produce structured outputs.

### 6. Output integrity
Decision / trace / attestation / Sigma fields must remain present.

## Why this matters for market conversations

This pack is useful for explaining that the public bank world is not only a demo.
It already shows:
- refusal before action
- deterministic repeatability
- temporal governance
- monotonic reaction under worsening risk
- traceability and attestation fields
- reproducible batch execution

## What this pack does not claim

This pack does not claim:
- legal certification
- formal AI Act compliance
- banking regulatory approval
- production deployment readiness
- real customer data validation

## Files added

- `docs/P2_BANK_TEST_SCOPE.md`
- `sigma/tests/test_bank_market_pack.py`
- `run_bank_test_pack.ps1`