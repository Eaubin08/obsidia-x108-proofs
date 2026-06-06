# P56D — Sigma Post-Guard Veto Boundary

## Status

SIGMA_POST_GUARD_VETO_BOUNDARY_APPLIED

## Problem

Sigma is applied after GuardX108 and can mutate the output dictionary.

## Resolution

Sigma remains an advanced proof layer, but its authority is explicitly bounded.

## Rule

SIGMA_POST_GUARD_VETO_ONLY

Sigma may:
- add sigma_step
- add sigma_report
- preserve pre_sigma_market_verdict
- preserve pre_sigma_severity
- downgrade to HOLD_STABILITY_ALERT if unstable

Sigma may not:
- authorize ACT
- promote HOLD/BLOCK
- hide the override
- replace GuardX108 authority

## Result

The proof runner remains advanced while preserving core rigor.
