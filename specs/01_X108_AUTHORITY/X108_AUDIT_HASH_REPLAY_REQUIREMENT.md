# X108_AUDIT_HASH_REPLAY_REQUIREMENT

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `periphery/os3_ticket.py` (merkle_root, replay_status)
- `docs/PROOF_SCOPE.md`

Source Status: RUNTIME_CODE

Scope: Spécifier les exigences de hash et de replay pour l'audit X108.

Allowed:
- "Chaque évaluation X108 produit un ticket avec merkle_root sha256"
- "replay_status = NOT_RUN par défaut — à implémenter en Plan 3"

Forbidden:
- "Le replay est opérationnel en production" (replay_status=NOT_RUN)
- "Le ticket remplace un audit externe"

Inputs: OS3ProofTicket
Outputs: Audit log avec chaîne de hashes

Metrics:
- input_hash, output_hash, trace_hash, merkle_root (sha256)

Invariants:
- Tout ticket doit avoir merkle_root non-nul
- replay_status = futur Plan 3

X108 Boundary: KX108_ONLY
Tests Required: test_merkle_root_non_null
Proof Expected: Python test (sha256 chain)
Runtime Status: RUNTIME_CODE (ticket) + ABSENT (replay)
Claim-Scope Notes: Ne pas affirmer replay fonctionnel avant Plan 3.
Open Questions: Quand replay_status sera-t-il "REPLAYED" ?
