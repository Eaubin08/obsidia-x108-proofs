# GPS_DEFENSE_AVIATION_BOUNDARY_SPEC
Status: RUNTIME_CODE
Authority: KX108_ONLY
Source Paths:
- periphery/adapters/gps_adapter.py\n- connectors/aviation_robo.py\n- sigma/domains/gps_defense_aviation_agents.py
Source Status: RUNTIME_CODE
Scope: Boundary GPS défense aviation.
Allowed:
- GPS = strategic surface\n- Verdict = proposed_verdict uniquement
Forbidden:
- GPS = défense production\n- Aviation connector = actuateur réel
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
