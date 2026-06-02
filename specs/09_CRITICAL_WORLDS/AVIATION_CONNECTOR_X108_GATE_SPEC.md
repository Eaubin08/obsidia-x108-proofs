# AVIATION_CONNECTOR_X108_GATE_SPEC
Status: RUNTIME_CODE
Authority: KX108_ONLY
Source Paths:
- connectors/aviation_robo.py
Source Status: RUNTIME_CODE
Scope: Connector aviation — gate X108 obligatoire.
Allowed:
- POST local (127.0.0.1) uniquement\n- WORLD_ACTION_DRY_RUN_READY — pas d'actuateur
Forbidden:
- Connector aviation en défense réelle\n- Connector sans gate X108
Inputs: Domain sources
Outputs: Spec contractuelle
Metrics: N/A
Invariants: KX108_ONLY pour toute décision
X108 Boundary: KX108_ONLY
Tests Required: À définir en Plan 3
Proof Expected: Python test
Runtime Status: RUNTIME_CODE + DRY_RUN
Claim-Scope Notes: Voir 00_SCOPE_DISCIPLINE/
Open Questions: À préciser en Plan 3
