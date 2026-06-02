# GPS_THREAT_MODEL_SPEC
Status: DOC_ONLY
Authority: KX108_ONLY
Source Paths:
- docs/periphery/GPS_ADAPTER_MAPPING_V0.md\n- docs/architecture/BANK_TRADING_GPS_CALIBRATION_WORLDS_V0.md
Source Status: DOC_ONLY
Scope: Threat model GPS.
Allowed:
- Spoofing GPS = détecté via source_conflict_score\n- Brownout = détecté via brownout_score
Forbidden:
- GPS = immunisé contre toute attaque (DRY_RUN)
Inputs: Domain sources
Outputs: Spec contractuelle
Metrics: N/A
Invariants: KX108_ONLY pour toute décision
X108 Boundary: KX108_ONLY
Tests Required: À définir en Plan 3
Proof Expected: Python test
Runtime Status: DOC_ONLY
Claim-Scope Notes: Voir 00_SCOPE_DISCIPLINE/
Open Questions: À préciser en Plan 3
