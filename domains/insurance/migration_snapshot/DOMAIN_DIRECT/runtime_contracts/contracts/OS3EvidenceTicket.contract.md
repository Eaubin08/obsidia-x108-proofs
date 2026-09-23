# OS3EvidenceTicket
# runtime_contracts/contracts/OS3EvidenceTicket.contract.md
# Status: CONTRACT_SKELETON_ONLY / NO_RUNTIME_EXECUTION

---

## 1. Purpose

L'OS3EvidenceTicket attache à tout DecisionTicket la preuve, la trace, le
replay, le hash, le seal, et les métadonnées d'audit nécessaires à la
vérifiabilité de la décision X-108.

Il s'appuie directement sur la structure existante `OS3ProofTicket` de
`periphery/os3_ticket.py` (sha256 chain : input_hash, output_hash, trace_hash,
merkle_root) et l'enrichit avec les informations de seal, replay, et audit.

Un OS3EvidenceTicket ne peut jamais décider. Il est purement probatoire.

---

## 2. Contract Status

```
Status:          CONTRACT_SKELETON_ONLY
Runtime:         NO_RUNTIME_EXECUTION
Authority:       KX108_ONLY (lié au DecisionTicket)
Emits ACT:       false
Emits decision:  false
Probatory only:  true
```

---

## 3. Required Fields

| Field | Type | Required | Description | Boundary |
|-------|------|----------|-------------|---------|
| `evidence_id` | string (UUID) | OUI | Identifiant unique | Immutable |
| `linked_decision_ticket` | string (UUID) | OUI | Référence au DecisionTicket | Doit exister |
| `evidence_type` | enum | OUI | `HASH_CHAIN`, `REPLAY_TRACE`, `SEAL_MERKLE`, `AUDIT_LOG`, `RFC3161_ANCHOR` | |
| `source` | string | OUI | Module ou couche source de la preuve | |
| `hash` | string | OUI | sha256 de l'artefact | `P13_Immutability` |
| `replay_status` | enum | OUI | `NOT_RUN`, `PASS`, `FAIL`, `PENDING` | Default `NOT_RUN` |
| `seal_status` | enum | OUI | `SEALED`, `UNSEALED`, `INVALID` | |
| `merkle_status` | enum | OUI | `VALID`, `INVALID`, `NOT_COMPUTED` | `merkleRoot_change_if_leaf_change` |
| `timestamp_or_tick` | string | OUI | Contexte temporel | Anti-replay C463 |
| `verification_status` | enum | OUI | `VERIFIED`, `UNVERIFIED`, `FAILED`, `PENDING` | |
| `claim_scope` | enum | OUI | `CLAIMABLE_FORMAL`, `CLAIMABLE_ADVISORY`, `CLAIMABLE_SPEC_ONLY` | |

---

## 4. Forbidden Fields

| Field | Reason |
|-------|--------|
| `decision` | Ne décide pas |
| `act_trigger` | Ne déclenche pas ACT |
| `allow_flag` / `hold_flag` / `block_flag` | Ne produit pas de verdict |
| Claim `verification_status = VERIFIED` si non vérifié | Fausse preuve — CRITICAL |

---

## 5. Failure Mode

| Situation | Comportement |
|-----------|-------------|
| `verification_status ≠ VERIFIED` | Ne pas clamer preuve vérifiée |
| `hash` invalide | `merkle_status = INVALID` → DecisionTicket pénalisé |
| `replay_status = FAIL` | Signal vers DecisionTicket → potentiel BLOCK |
| Schema invalide | Reject → DecisionTicket sans preuve = HOLD candidat |

---

## 6. JSON Example

```json
{
  "evidence_id": "os3-2026-06-02-001",
  "linked_decision_ticket": "dt-2026-06-02-001",
  "evidence_type": "HASH_CHAIN",
  "source": "periphery/os3_ticket.py",
  "hash": "sha256:abc123def456...",
  "replay_status": "NOT_RUN",
  "seal_status": "SEALED",
  "merkle_status": "VALID",
  "timestamp_or_tick": "2026-06-02T09:10:40Z",
  "verification_status": "VERIFIED",
  "claim_scope": "CLAIMABLE_ADVISORY",
  "input_hash": "sha256:aaa...",
  "output_hash": "sha256:bbb...",
  "trace_hash": "sha256:ccc...",
  "merkle_root": "sha256:ddd...",
  "rfc3161_anchor_ref": null
}
```

---

## 7. Boundary / Authority / Claim-Scope

```
OS3EvidenceTicket ↛ décision
OS3EvidenceTicket → preuves attachées à DecisionTicket
Invariants: P13_Immutability, merkleRoot_change_if_leaf_change, P17_AuditGrowth
Claim autorisé: "OS3EvidenceTicket prouve la traçabilité de la décision X-108"
Claim interdit: "OS3EvidenceTicket remplace une preuve Lean formelle"
```

---

## 8. Tests Required Later

- `test_os3_evidence_hash_chain_valid`
- `test_os3_evidence_no_decision`
- `test_os3_evidence_verification_status_honest`

---

## 9. Future Implementation Notes

**FUTURE_IMPLEMENTATION_NOTE — P5 :** RFC3161 anchor sera ajouté en production.
**FUTURE_IMPLEMENTATION_NOTE — P5 :** replay_status = PASS requis pour ALLOW CRITICAL en production.

---

## 10. Proof Expected Later

- Python test : hash chain validation (pattern existant os3_ticket.py)
- `test_merkle_root_coverage` + `test_os3_ticket_hash_chain` (existants à étendre)
