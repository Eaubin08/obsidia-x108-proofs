# MERKLE_REPLAY_CHAIN_SPEC
Status: RUNTIME_CODE
Authority: KX108_ONLY
Source Paths:
- periphery/os3_ticket.py (merkle_root)
Source Status: RUNTIME_CODE
Scope: Chaîne Merkle pour replay.
Allowed:
- merkle_root = sha256([input_hash, output_hash, trace_hash])\n- Couverture: input+output+trace
Forbidden:
- Merkle tree complet (1 niveau actuellement)\n- Merkle = certification blockchain
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
