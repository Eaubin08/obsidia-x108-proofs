# ENTROPY_TO_X108_HOLD_RULE

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- periphery/math_core/governed_state.py\n- periphery/action_lifecycle.py

Source Status: SOURCE_ORGANIZED

Scope: Règle : haute entropie → X108 HOLD.

Allowed:
- X108 retourne HOLD si entropy > threshold

Forbidden:
- Entropie haute = ALLOW automatique

Inputs: Sources domain
Outputs: Spec contractuelle
Metrics: N/A
Invariants: KX108_ONLY pour toute décision
X108 Boundary: KX108_ONLY
Tests Required: À définir en Plan 3
Proof Expected: Python test
Runtime Status: RUNTIME_CODE
Claim-Scope Notes: Voir 00_SCOPE_DISCIPLINE/ pour limites publiques
Open Questions: À préciser en Plan 3
