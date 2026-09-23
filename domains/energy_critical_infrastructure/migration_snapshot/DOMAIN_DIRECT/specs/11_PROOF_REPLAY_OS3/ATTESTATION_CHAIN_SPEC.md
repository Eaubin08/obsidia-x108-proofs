# ATTESTATION_CHAIN_SPEC
Status: SOURCE_ORGANIZED
Authority: KX108_ONLY
Source Paths:
- periphery/os3_ticket.py\n- periphery/blockchain/signature_boundary.py
Source Status: SOURCE_ORGANIZED
Scope: Chaîne d'attestation Obsidia.
Allowed:
- Attestation = OS3ProofTicket + merkle_root\n- Signature boundary pour blockchain (local)
Forbidden:
- Attestation = signature blockchain prod\n- Attestation = NFT
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
