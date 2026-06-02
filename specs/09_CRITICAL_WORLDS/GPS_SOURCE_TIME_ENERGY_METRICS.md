# GPS_SOURCE_TIME_ENERGY_METRICS
Status: RUNTIME_CODE
Authority: KX108_ONLY
Source Paths:
- periphery/adapters/gps_adapter.py
Source Status: RUNTIME_CODE
Scope: Métriques GPS: source, temps, énergie.
Allowed:
- trajectory_drift_score, source_conflict_score, time_skew_score, brownout_score in [0,1]
Forbidden:
- Ces scores = certitude
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
