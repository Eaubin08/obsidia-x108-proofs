# Brody No-Decision Policy V1

**Status:** ABSOLUTE INVARIANT
**Role:** Brody provides context and analysis but never makes governance decisions.
**Gate:** ADVISORY_ONLY — never ALLOW, never ACT

## The Invariant

**Brody répond. Brody ne décide pas.** Every Brody response is advisory — it provides context, analysis, suggestions, and information. It never issues a binding decision, never approves an action, and never overrides X108.

## Enforcement

- `decision_authority = "KX108_ONLY"` in every response
- `emits_verdict = False` in every response
- `emits_act = False` in every response
- `advisory_only = True` in the Brody Response Contract

## Why

Brody is a context engine. Context is signal. Signal is not decision. The architecture separates:

```
Brody  →  context (signal)
Sigma  →  aggregation (BLOCK > HOLD > ALLOW recommendation)
X108   →  decision (sole sovereign authority)
OS3    →  proof (cryptographic verification)
```

## What Brody CAN Do

- Answer questions
- Provide analysis
- Route language
- Reference context packets
- Suggest HOLD/BLOCK flags (as advisory input to Sigma)

## What Brody CANNOT Do

- Issue ALLOW/BLOCK/ACT
- Decide on action approval
- Override X108
- Write to memory
- Mutate kernel state
- Emit verdicts

## Tests

- `tests/non_sovereignty/test_brody_no_decision.py` (4 assertions)
- `tests/non_sovereignty/test_brody_no_act.py`

## Status

**BRODY_NO_DECISION_PASS** — Absolute invariant.
