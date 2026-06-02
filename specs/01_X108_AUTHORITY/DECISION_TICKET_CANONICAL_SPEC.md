# DECISION_TICKET_CANONICAL_SPEC

Status: RUNTIME_CODE
Authority: KX108_ONLY

Source Paths:
- `periphery/os3_ticket.py`

Source Status: RUNTIME_CODE

Scope:
Spécifier le DecisionTicket (OS3ProofTicket) comme artefact central de la chaîne de preuve.

Allowed:
- "OS3ProofTicket est l'artefact de preuve runtime généré après chaque évaluation X108"
- "Le ticket contient une chaîne de hashes sha256 : input → output → trace → merkle_root"

Forbidden:
- "Le ticket remplace une preuve Lean formelle"
- "Le ticket = preuve cryptographique RFC3161 en production"

Inputs:
- action_candidate, packet, envelope (output X108)

Outputs:
- OS3ProofTicket avec : ticket_id, action_id, domain, x108_gate, reason_code, severity, scores, unknowns, risk_flags, contradictions, evidence_refs, input_hash, output_hash, trace_hash, merkle_root, replay_status

Metrics:
- input_hash = sha256(action_candidate)
- output_hash = sha256(envelope)
- trace_hash = sha256({input+output+packet})
- merkle_root = sha256([ih, oh, th])

Invariants:
- `ticket_is_valid()` = les 4 hashes sont non-nuls
- `replay_status = "NOT_RUN"` par défaut
- Le ticket est produit APRÈS X108_EVALUATED

X108 Boundary:
- x108_gate dans le ticket = valeur fixée par KX108

Tests Required:
- test_os3_ticket_hash_chain
- test_merkle_root_coverage

Proof Expected: Python test (sha256 chain)

Runtime Status: RUNTIME_CODE

Claim-Scope Notes:
merkle_root couvre input+output+trace — pas l'intégralité de la session.

Open Questions: Quand replay_status sera-t-il autre que "NOT_RUN" ?
