# X108_IRREVERSIBLE_ACTION_BOUNDARY

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `periphery/action_lifecycle.py` (WORLD_ACTION_DRY_RUN_READY)
- `periphery/world_action_gateway.py`
- `periphery/engine_gates/world_action_gateway.py`

Source Status: RUNTIME_CODE + DRY_RUN

Scope: Définir la frontière des actions irréversibles et les gardes X108 associés.

Allowed:
- "Toute action irréversible passe par WORLD_ACTION_DRY_RUN_READY avant déclenchement"
- "WORLD_ACTION_DRY_RUN_READY = prête pour revue humaine — pas déclenchée"

Forbidden:
- "Les actions irréversibles peuvent être déclenchées sans X108 ALLOW + gate humain"

Inputs: X108 gate = ALLOW + OS3ProofTicket valide
Outputs: WorldAction candidate (DRY_RUN uniquement en Plan 2)
Metrics: N/A
Invariants: Action irréversible → X108 ALLOW + gate humain obligatoire
X108 Boundary: KX108_ONLY
Tests Required: test_no_actuator_without_decisionticket
Proof Expected: Python test
Runtime Status: DRY_RUN (aucun actuateur en Plan 2)
Claim-Scope Notes: Aucune action réelle dans le monde en Plan 2.
Open Questions: Quel actuateur en Plan 3 ?
