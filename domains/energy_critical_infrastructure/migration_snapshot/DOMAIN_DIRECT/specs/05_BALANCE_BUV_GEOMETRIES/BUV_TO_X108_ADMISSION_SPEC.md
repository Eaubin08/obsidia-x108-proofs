# BUV_TO_X108_ADMISSION_SPEC

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- periphery/gencoin_sandbox/balance_operator.py\n- periphery/x108_ingress/readonly_context_ingress.py

Source Status: SOURCE_ORGANIZED

Scope: Admission du score BUV dans le contexte X108.

Allowed:
- balance_score = entrée X108 comme signal de pondération

Forbidden:
- Balance → ALLOW automatique

Inputs: Domain sources
Outputs: Spec contractuelle
Metrics: N/A
Invariants: KX108_ONLY pour toute décision
X108 Boundary: KX108_ONLY
Tests Required: À définir en Plan 3
Proof Expected: Python test
Runtime Status: RUNTIME_CODE
Claim-Scope Notes: Voir 00_SCOPE_DISCIPLINE/ pour limites publiques
Open Questions: À préciser en Plan 3
