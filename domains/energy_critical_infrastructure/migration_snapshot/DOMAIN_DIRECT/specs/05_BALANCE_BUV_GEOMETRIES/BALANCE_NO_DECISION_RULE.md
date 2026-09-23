# BALANCE_NO_DECISION_RULE

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- periphery/gencoin_sandbox/balance_operator.py

Source Status: SOURCE_ORGANIZED

Scope: Règle absolue : Balance ne décide pas.

Allowed:
- Balance produit un score — KX108 décide

Forbidden:
- Balance produit ALLOW/HOLD/BLOCK

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
