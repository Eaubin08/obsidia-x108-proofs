# OS3_PROOF_RUNTIME_SPEC

Status: RUNTIME_CODE
Authority: KX108_ONLY

Source Paths:
- `periphery/os3_ticket.py`
- `docs/PROOF_SCOPE.md`

Source Status: RUNTIME_CODE + SOURCE_CANON

Scope: Spécification du système de preuve runtime OS3 (OS3ProofTicket).

Allowed:
- "OS3ProofTicket est un artefact de preuve runtime généré après X108_EVALUATED"
- "La chaîne sha256 (input→output→trace→merkle_root) garantit l'intégrité de la trace"

Forbidden:
- "OS3ProofTicket = preuve formelle Lean"
- "OS3ProofTicket = preuve RFC3161 en production"
- "Le replay est opérationnel" (replay_status=NOT_RUN)

Inputs: action_candidate + packet + envelope (output X108)

Outputs: OS3ProofTicket avec :
- ticket_id (uuid)
- action_id, domain
- x108_gate : ALLOW | HOLD | BLOCK
- reason_code, severity
- scores, unknowns, risk_flags, contradictions, evidence_refs
- input_hash, output_hash, trace_hash, merkle_root (sha256)
- replay_status : "NOT_RUN" par défaut

Metrics:
- Chaîne : sha256(input) → sha256(output) → sha256({in+out+packet}) → sha256([ih,oh,th])

Invariants:
- `ticket_is_valid()` = les 4 hashes sont non-nuls
- merkle_root couvre input + output + trace
- x108_gate est fixé par KX108

X108 Boundary: Le ticket capture la décision KX108

Tests Required:
- test_os3_ticket_hash_chain
- test_merkle_root_coverage

Proof Expected: Python test (sha256 chain integrity)

Runtime Status: RUNTIME_CODE

Claim-Scope Notes:
"OS3ProofTicket = preuve runtime Python — pas Lean proof, pas RFC3161 prod."

Open Questions: Quand replay_status sera-t-il "REPLAYED" ? (Plan 3)
