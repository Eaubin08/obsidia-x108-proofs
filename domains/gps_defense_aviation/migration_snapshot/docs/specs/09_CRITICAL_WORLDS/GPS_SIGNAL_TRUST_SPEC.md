# GPS_SIGNAL_TRUST_SPEC
Status: RUNTIME_CODE
Authority: KX108_ONLY
Source Paths:
- periphery/adapters/gps_adapter.py\n- sigma/domains/gps_defense_aviation_agents.py
Source Status: RUNTIME_CODE
Scope: Confiance du signal GPS.
Allowed:
- attestation_ready, rollback_possible dans GPS state\n- signal_noise_ratio, satellites_count pour scoring
Forbidden:
- GPS trust = certitude absolue
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
