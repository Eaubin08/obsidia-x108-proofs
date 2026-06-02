# BANK_TRADING_ECOM_INTENT_ONLY_SPEC
Status: DOC_ONLY
Authority: KX108_ONLY
Source Paths:
- docs/architecture/BANK_TRADING_GPS_CALIBRATION_WORLDS_V0.md
Source Status: DOC_ONLY
Scope: Bank/Trading/Ecom = intent only avant X108.
Allowed:
- Bank actions = intent_packet → X108 evaluation\n- DRY_RUN uniquement en Plan 2
Forbidden:
- Bank actions sans X108\n- Trading = production en Plan 2
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
