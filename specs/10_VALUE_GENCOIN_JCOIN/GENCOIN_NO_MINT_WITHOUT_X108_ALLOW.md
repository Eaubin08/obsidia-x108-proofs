# GENCOIN_NO_MINT_WITHOUT_X108_ALLOW
Status: SOURCE_CANON
Authority: KX108_ONLY
Source Paths:
- periphery/blockchain/token_policy.py\n- docs/blockchain/GENCOIN_NOT_A_TOKEN_POLICY_V1.md
Source Status: SOURCE_CANON
Scope: Règle absolue: pas de mint sans X108 ALLOW.
Allowed:
- BLOCK absolu sur MINT/DEPLOY/CREATE si is_gencoin=True
Forbidden:
- Mint Gencoin sans X108\n- DEPLOY Gencoin sur blockchain
Inputs: Domain sources
Outputs: Spec contractuelle
Metrics: N/A
Invariants: KX108_ONLY pour toute décision
X108 Boundary: KX108_ONLY
Tests Required: À définir en Plan 3
Proof Expected: Python test
Runtime Status: SOURCE_CANON
Claim-Scope Notes: Voir 00_SCOPE_DISCIPLINE/
Open Questions: À préciser en Plan 3
