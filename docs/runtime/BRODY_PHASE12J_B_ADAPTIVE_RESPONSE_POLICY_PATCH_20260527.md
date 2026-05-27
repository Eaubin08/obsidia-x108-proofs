# BRODY_PHASE12J_B_ADAPTIVE_RESPONSE_POLICY_PATCH_20260527

Status: PASS_READY_FOR_REVIEW

## Scope

Expose Brody adaptive answer sizing as an auditable readonly policy.

## 12J-A finding

Brody already produced acceptable answer sizes on the first adaptive sizing audit.

But the sizing was behavioral, not explicitly exposed as a policy snapshot.

## Patched

- apps/obsidia_api/brody_adaptive_response_policy.py
- apps/obsidia_api/brody_true_voice_adapter.py
- tools/brody_chat.py

## Added visible calculation

- response_size
- density
- context_need
- sigma_pressure
- reason

## Exposed in

- true_voice_snapshot.adaptive_response_policy
- terminal block: ADAPTIVE RESPONSE POLICY / SIGMA

## Boundary

Readonly only.

The policy does not decide, act, write memory, write Graphiti, mutate kernel, or mutate X108.

## Validation

- BOM=false
- py_compile passed
- targeted pytest passed
- live policy check passed
- terminal visibility check passed

## Decision

Brody answer sizing is now explicit and auditable as a peripheral/sigma-like policy.
