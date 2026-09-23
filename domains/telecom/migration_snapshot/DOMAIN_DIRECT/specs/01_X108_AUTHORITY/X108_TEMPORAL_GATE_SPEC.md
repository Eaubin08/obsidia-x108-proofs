# X108_TEMPORAL_GATE_SPEC

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `periphery/action_lifecycle.py` (X108_EVALUATED step + transitions)

Source Status: RUNTIME_CODE

Scope: Spécifier la position temporelle de X108 dans le cycle d'action.

Allowed:
- "X108 est évalué après SIGMA_ROUTED et avant OS3_TICKETED"
- "Le cycle d'action comporte 10 états — X108_EVALUATED est le 5e"

Forbidden:
- "X108 peut être évalué avant que Sigma n'ait routé"
- "X108 peut être contourné dans le cycle"

Inputs: ActionPhase.SIGMA_ROUTED (sortie Sigma)
Outputs: ActionPhase.X108_EVALUATED → transition vers OS3_TICKETED
Metrics: N/A

Invariants:
- SIGMA_ROUTED → X108_EVALUATED → OS3_TICKETED (ordre strict)
- Aucune transition ne saute X108_EVALUATED

X108 Boundary: X108_EVALUATED EST la boundary
Tests Required: test_action_lifecycle_x108_position
Proof Expected: Python test (transitions)
Runtime Status: RUNTIME_CODE
Claim-Scope Notes: La position temporelle de X108 est contractuelle — ne pas modifier l'ordre des états.
Open Questions: FEEDBACK_CAPTURED (état 9) est-il dans le périmètre public ?
