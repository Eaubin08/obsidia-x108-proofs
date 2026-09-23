# P56A-C0 — Gamma Impact Audit Verdict

## Status

AUDIT_COMPLETE_PATCH_NOT_APPLIED

## Finding

OS2 currently uses gamma = 0.5.

OS3 currently uses gamma = 1.0.

This is not accepted as a harmless layer difference anymore.

## Impact

The impact scan shows that OS2 gamma is not only documentary.

It appears in:
- _tmp_core_import/OBSIDIA_CORE_ONLY_FULL_MACHINERY/engine/obsidia_os2/metrics.py
- _tmp_core_import/OBSIDIA_CORE_ONLY_FULL_MACHINERY/engine/obsidia_os2_metrics.py
- proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_os2/metrics.py
- obsidia_runtime/engine_final.py imports and calls compute_metrics_core_fixed
- tests/test_invariants_against_engine.py calls compute_metrics_core_fixed

OS3 uses:
- gamma = 1.0
- strong triangle detection
- radial hexagon scoring
- full asymmetry penalty

## Decision candidate

OS3 is the metric authority.

Target:
- OS2 gamma must align to OS3 gamma.
- target_os2_gamma = 1.0
- target_os3_gamma = 1.0

## Fusion status

FUSION_BLOCKED_UNTIL_GAMMA_PATCH

## Required controlled patch

Patch only after explicit validation:
1. update tracked proof OS2 metric gamma 0.5 -> 1.0
2. update core source pack copy / parent core separately if needed
3. update old P56A docs that still say LAYER_DIFFERENCE_NOT_CONFLICT
4. add regression tests proving no gamma=0.5 remains in OS2 tracked proof
5. run full tests / manifest / forbidden content

## Forbidden

- no silent normalization
- no fusion before patch
- no keeping gamma 0.5 as accepted state
- no calling this non-conflict
