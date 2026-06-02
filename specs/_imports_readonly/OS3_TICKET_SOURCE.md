# OS3_TICKET_SOURCE

Import Type: READONLY_SOURCE_IMPORT

Original Source Paths:
- `periphery/os3_ticket.py`

Imported Facts:
- `OS3ProofTicket` dataclass : ticket_id, action_id, domain, x108_gate, reason_code, severity, scores, unknowns, risk_flags, contradictions, evidence_refs, input_hash, output_hash, trace_hash, merkle_root, replay_status
- Hashes sha256 : input_hash = sha256(action_candidate), output_hash = sha256(envelope), trace_hash = sha256({input+output+packet}), merkle_root = sha256([ih, oh, th])
- `replay_status = "NOT_RUN"` par défaut
- `ticket_is_valid()` vérifie que les 4 hashes sont non-nuls
- `build_os3_ticket()` construit le ticket depuis action_candidate + packet + envelope

What This Source Proves:
- Existence d'un ticket de preuve runtime avec chaîne de hashes sha256
- Le ticket capture l'état X108 (x108_gate = ALLOW/HOLD/BLOCK)
- Le merkle_root couvre input + output + trace

What This Source Does NOT Prove:
- Preuve formelle Lean du ticket
- Que replay_status est jamais différent de "NOT_RUN" (mécanisme de replay non implémenté)
- Intégrité cryptographique au niveau RFC3161

Boundary:
- RUNTIME_CODE — sha256 Python — pas RFC3161 en production

Claim-Scope:
- "Obsidia génère un ticket de preuve runtime avec hashes sha256" — AUTORISÉ
- "Obsidia a un système de replay fonctionnel en production" — INTERDIT (replay_status=NOT_RUN)

Specs Depending On This Source:
- 11_PROOF_REPLAY_OS3/OS3_PROOF_RUNTIME_SPEC.md
- 11_PROOF_REPLAY_OS3/MERKLE_REPLAY_CHAIN_SPEC.md
- 01_X108_AUTHORITY/X108_AUDIT_HASH_REPLAY_REQUIREMENT.md

Runtime Status: RUNTIME_CODE

Do Not Move Original Source: true
Authority: KX108_ONLY
