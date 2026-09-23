# VALUE_EMISSION_MODEL
Status: SOURCE_ORGANIZED
Authority: KX108_ONLY
Source Paths:
- docs/gencoin/GENCOIN_FORMAL_MATH_SPEC_V0_2.md\n- docs/gencoin/GENCOIN_DISTRIBUTION_LAW_V0.md\n- periphery/gencoin_distribution.py
Source Status: SOURCE_ORGANIZED
Scope: Modèle d'émission de valeur Gencoin.
Allowed:
- GC = X108_ALLOW x OS3_PROOF x ... x max(0,VALUE-DEBT)\n- Distribution law documentée
Forbidden:
- Émission de valeur sans X108 ALLOW\n- value_emission = token minting
Inputs: Domain sources
Outputs: Spec contractuelle
Metrics: N/A
Invariants: KX108_ONLY pour toute décision
X108 Boundary: KX108_ONLY
Tests Required: À définir en Plan 3
Proof Expected: Python test
Runtime Status: SOURCE_ORGANIZED
Claim-Scope Notes: Voir 00_SCOPE_DISCIPLINE/
Open Questions: À préciser en Plan 3
