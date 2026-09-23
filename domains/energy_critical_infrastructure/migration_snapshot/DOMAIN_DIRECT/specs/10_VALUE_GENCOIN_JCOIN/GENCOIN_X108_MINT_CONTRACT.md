# GENCOIN_X108_MINT_CONTRACT
Status: SOURCE_ORGANIZED
Authority: KX108_ONLY
Source Paths:
- periphery/gencoin.py\n- periphery/os3_ticket.py
Source Status: SOURCE_ORGANIZED
Scope: Contrat Gencoin-X108 pour mint.
Allowed:
- mint_allowed = True seulement si x108_gate=ALLOW ET ticket valide
Forbidden:
- Mint local = mint blockchain\n- Mint sans X108 ALLOW
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
