# P56A-C0 — Gamma Conflict Audit Only

Status: CONFLICT_OPEN

## Facts

OS2:
- gamma = 0.5
- formula = S = alpha*T + beta*H - gamma*A
- path core temp = C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\_tmp_core_import\OBSIDIA_CORE_ONLY_FULL_MACHINERY\engine\obsidia_os2\metrics.py
- path proof = C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\proofs\V18_3_1\engine_buildable_0_9_3_1\obsidia_os2\metrics.py

OS3:
- gamma = 1.0
- formula = S = alpha*tmean + beta*hstar - gamma*A
- path core temp = C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\_tmp_core_import\OBSIDIA_CORE_ONLY_FULL_MACHINERY\engine\os3\metrics.py
- path proof = C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\proofs\V18_3_1\engine_buildable_0_9_3_1\obsidia_structural_core\metrics.py

## Problem

Same metric name gamma, different value.

## Audit conclusion

This is not resolved.
No source patch authorized.
Fusion remains blocked until explicit design decision.

## Possible resolutions, not applied

1. Normalize OS2 gamma to 1.0
2. Rename metrics by scope:
   - os2_gamma_proxy = 0.5
   - os3_gamma_structural = 1.0
3. Keep as-is but document formal reason and add tests
4. Block fusion

## Current decision

NO_DECISION_YET
FUSION_BLOCKED_ON_C0_GAMMA
