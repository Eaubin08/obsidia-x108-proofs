# NO_ACTUATOR_WITHOUT_DECISIONTICKET
Status: SOURCE_ORGANIZED
Authority: KX108_ONLY
Source Paths:
- periphery/action_lifecycle.py (WORLD_ACTION_DRY_RUN_READY)\n- periphery/world_action_gateway.py
Source Status: SOURCE_ORGANIZED
Scope: Aucun actuateur sans DecisionTicket.
Allowed:
- WORLD_ACTION_DRY_RUN_READY = prêt pour revue — pas déclenché
Forbidden:
- Actuateur physique sans DecisionTicket X108
Inputs: Domain sources
Outputs: Spec contractuelle
Metrics: N/A
Invariants: KX108_ONLY pour toute décision
X108 Boundary: KX108_ONLY
Tests Required: À définir en Plan 3
Proof Expected: Python test
Runtime Status: RUNTIME_CODE
Claim-Scope Notes: Voir 00_SCOPE_DISCIPLINE/
Open Questions: À préciser en Plan 3
