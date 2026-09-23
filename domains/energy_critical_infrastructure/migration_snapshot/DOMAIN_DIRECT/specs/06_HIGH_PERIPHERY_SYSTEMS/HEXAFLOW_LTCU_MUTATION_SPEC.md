# HEXAFLOW_LTCU_MUTATION_SPEC

Status: RUNTIME_CODE
Authority: KX108_ONLY

Source Paths:
- periphery/hexaflux/ltcu_plus.py\n- periphery/hexaflux/transition_mapper.py

Source Status: RUNTIME_CODE

Scope: HexaFlux / LTCU+ — drift contextuel.

Allowed:
- LTCUPlusSignal: advisory_only=True, authorizes=False\n- Drift contextuel longue durée

Forbidden:
- LTCU autorise actions\n- HexaFlux décide

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
