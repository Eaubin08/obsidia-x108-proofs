# BALANCE_ADMISSIBILITY_OPERATOR_SPEC

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- periphery/gencoin_sandbox/balance_operator.py\n- periphery/gencoin_sandbox/regime_truth_gate.py

Source Status: SOURCE_ORGANIZED

Scope: Opérateur d'admissibilité de la balance.

Allowed:
- regime_truth_gate vérifie la validité du régime

Forbidden:
- Gate = décision ALLOW

Inputs: Domain sources
Outputs: Spec contractuelle
Metrics: N/A
Invariants: KX108_ONLY pour toute décision
X108 Boundary: KX108_ONLY
Tests Required: À définir en Plan 3
Proof Expected: Python test
Runtime Status: RUNTIME_CODE (sandbox)
Claim-Scope Notes: Voir 00_SCOPE_DISCIPLINE/ pour limites publiques
Open Questions: À préciser en Plan 3
