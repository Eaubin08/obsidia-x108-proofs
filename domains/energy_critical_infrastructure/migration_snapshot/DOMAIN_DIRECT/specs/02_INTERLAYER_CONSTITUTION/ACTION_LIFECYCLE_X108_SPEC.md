# ACTION_LIFECYCLE_X108_SPEC

Status: RUNTIME_CODE
Authority: KX108_ONLY

Source Paths:
- `periphery/action_lifecycle.py`

Source Status: RUNTIME_CODE

Scope: Spécification contractuelle du cycle complet d'une action gouvernée Obsidia.

Allowed:
- "Le cycle comporte 10 états avec FEEDBACK_CAPTURED comme 9e état"
- "X108_EVALUATED est l'état 5 — central et non-contournable"

Forbidden:
- "Le cycle peut être raccourci en sautant X108_EVALUATED"
- "FEEDBACK_CAPTURED = état public confirmé" (décision humaine requise)

Inputs: ActionPhase.INPUT_CAPTURED
Outputs: ActionPhase.CLOSED

Metrics: N/A

Invariants:
Cycle complet (ordre strict) :
1. INPUT_CAPTURED
2. ACTION_CANDIDATE_BUILT
3. PERIPHERY_SCORED
4. SIGMA_ROUTED
5. **X108_EVALUATED** ← gate centrale
6. OS3_TICKETED
7. GENCOIN_EVALUATED
8. WORLD_ACTION_DRY_RUN_READY
9. FEEDBACK_CAPTURED *(décision public scope à valider)*
10. MEMORY_CANDIDATE_BUILT
11. CLOSED

X108 Boundary: X108_EVALUATED = gate obligatoire
Tests Required: test_lifecycle_order_invariant
Proof Expected: Python test (transitions)
Runtime Status: RUNTIME_CODE
Claim-Scope Notes: FEEDBACK_CAPTURED n'est pas dans le périmètre public — décision humaine requise.
Open Questions: FEEDBACK_CAPTURED dans périmètre public ?
