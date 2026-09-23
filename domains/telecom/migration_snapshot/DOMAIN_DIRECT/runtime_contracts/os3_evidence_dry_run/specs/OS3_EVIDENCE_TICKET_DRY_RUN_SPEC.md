# OS3_EVIDENCE_TICKET_DRY_RUN_SPEC
# runtime_contracts/os3_evidence_dry_run/specs/
# Plan 3 P5 — Spec documentaire uniquement — NO PROOF / NO HASH / NO SEAL / NO EXECUTION
# Date: 2026-06-02
# Status: OS3_EVIDENCE_SPEC_ONLY / DRY_RUN_DOCUMENTATION_ONLY

---

## 1. Purpose

Ce document spécifie la structure documentaire du futur OS3 Evidence Ticket Dry-Run.

L'OS3EvidenceTicket est l'artefact qui s'attache à chaque DecisionTicket pour en garantir
la traçabilité, la rejouabilité, l'immuabilité et l'auditabilité.

En P5, ce document décrit uniquement la **forme théorique** de cet artefact.
Aucun hash réel n'est calculé. Aucun seal n'est apposé. Aucun Merkle tree n'est construit.
Aucune preuve formelle n'est produite.

---

## 2. Status

```
Status:                         OS3_EVIDENCE_SPEC_ONLY
Hash computation:               NO — PLACEHOLDER_ONLY
Seal generation:                NO — PLACEHOLDER_ONLY
Merkle tree:                    NO — PLACEHOLDER_ONLY
Replay execution:               NO — NOT_AVAILABLE_IN_P5
Proof generation:               NO — FUTURE_FORMAL_TARGET
Test execution:                 NO
Python files:                   NO
Runtime execution:              NO
Packages:                       NO
World action:                   NO
DecisionTicket réel:            NO
Commit:                         NO
Push:                           NO
```

---

## 3. Scope

L'OS3EvidenceTicket dry-run couvre les sources d'evidence suivantes :

| Source | Statut P5 | Evidence type |
|--------|----------|---------------|
| External Signals temporal receipt (packet 52) | SPEC_IMPORTED (F04) | HASH_CHAIN (théorique) |
| X108 Gateway DecisionTicket (théorique) | THEORETICAL_ONLY | DECISION_TRACE |
| Anti-bypass check results (P4) | SPEC_ONLY | BYPASS_AUDIT_TRACE |
| RSSI security posture (future F03) | COPIED_READONLY | RSSI_EVIDENCE_FUTURE |
| RGPD readiness (future F03+F10) | COPIED_READONLY | RGPD_EVIDENCE_FUTURE |
| Graphiti/Brody readonly context (future) | SPEC_ONLY | CONTEXT_TRACE_FUTURE |
| NPL provenance (specs/12/) | SPEC_IMPORTED | PROVENANCE_TRACE |
| P107/P161 advisory metrics (future Lean) | PYTHON_SPEC | FORMAL_TARGET_FUTURE |
| F78B source-pack audit | AUDIT_READY | SOURCE_PACK_GATE_TRACE |
| F78C XLSX reconciliation | AUDIT_READY | BACKLOG_GATE_TRACE |

---

## 4. Non-executable status

P5 crée uniquement :
- Fichiers `.md` documentaires
- Zéro fichier `.py`
- Zéro hash calculé
- Zéro seal apposé
- Zéro Merkle tree construit
- Zéro preuve formelle générée
- Zéro replay exécuté

Les futurs artefacts réels seront créés uniquement après :
1. Plan 3 P4 Anti-bypass spec validé ✅ (fait)
2. F03/F06/F07 imports selon pack concerné
3. Plan 3 P5 OS3 Evidence Spec validé (ce run)
4. Gate humaine sur la spec P5
5. Lean proofs formels pour les invariants P13/P17

---

## 5. Evidence model

```
OS3EvidenceTicket = artefact READONLY qui ATTESTE sans décider

Propriétés fondamentales :
  can_decide = false
  can_emit_act = false
  can_produce_allow_hold_block = false
  is_decision_substitute = false
  is_proof_in_p5 = false  (DOCUMENTARY_ONLY)
  is_verification_status_verified_in_p5 = false

Usage légitime :
  s'attache à un DecisionTicket théorique
  transport des métadonnées d'audit
  référence le receipt temporel (packet 52)
  documente les vérifications futures

Usage interdit :
  remplacer X108
  produire ALLOW/HOLD/BLOCK
  prouver sans vérification
  certifier RGPD/ISO/RSSI
  affirmer hash/seal/merkle réels en P5
```

---

## 6. Evidence sources

### Source 1 — External Signals temporal receipt (packet 52)

```yaml
evidence_from_temporal_receipt:
  packet_source: 52_temporal_receipt.packet.yaml
  fields_used:
    - receipt_id        → evidence_id base
    - action_intent_hash → hash_ref (PLACEHOLDER in P5)
    - tick_window       → temporal_context
    - anti_replay_status → replay_check_result
    - replay_pointer    → replay_ref (FUTURE)
    - kx108_decision    → linked_decision_ticket_ref (post-X108 only)
  evidence_type: HASH_CHAIN
  verification_in_p5: NOT_VERIFIED — DOCUMENTARY_ONLY
  boundary: EXTERNAL_SIGNALS_SIGNAL_ONLY
```

### Source 2 — X108 Gateway theoretical DecisionTicket

```yaml
evidence_from_decision_ticket:
  source: X108 Gateway (seul producteur)
  fields_used:
    - ticket_id         → linked_decision_ticket
    - decision          → decision_trace (ALLOW/HOLD/BLOCK — X108 seul)
    - reason_codes      → evidence_context
    - x108_gate_status  → gate_trace
    - tau_status        → temporal_tau_trace
  evidence_type: DECISION_TRACE
  link_direction: OS3Evidence → attaches_to → DecisionTicket
  claim_scope: THEORETICAL_ONLY in P5
```

### Source 3 — Anti-bypass checks (P4 spec)

```yaml
evidence_from_anti_bypass:
  source: runtime_contracts/anti_bypass_tests_spec/
  fields_used:
    - TB-01 to TB-60 scenario results → bypass_check_refs
    - failure_modes detected          → bypass_failure_trace
  evidence_type: BYPASS_AUDIT_TRACE
  claim_scope: SPEC_ONLY in P4 / FUTURE_EXECUTABLE
  boundary: NO_ACT_FROM_PERIPHERY + X108_GATEWAY_REQUIRED
```

### Source 4 — F78B/F78C gate traces (future)

```yaml
evidence_from_source_pack_gates:
  source_f78b: _source_discovery/F78B_SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_132021/
  source_f78c: _source_discovery/F78C_XLSX_IMPLEMENTATION_PLAN_RECONCILIATION_20260602_133600/
  evidence_type: SOURCE_PACK_GATE_TRACE
  claim_scope: AUDIT_READY — import gate evidence only
  note: F78B/F78C sont des audits, pas des preuves d'import
```

---

## 7. Required contracts

| Contrat | Rôle dans OS3 dry-run |
|---------|----------------------|
| OS3EvidenceTicket.contract.md | Structure principale |
| DecisionTicket.contract.md | Ticket auquel OS3 s'attache |
| IntentEnvelope.contract.md | Intent source de la décision |
| ContextPacket.contract.md | Contexte auquel OS3 peut référer |
| PeripheralSignalPacket.contract.md | Signaux inclus dans trace |
| BoundaryContract.contract.md | Droits du module OS3 |
| RuntimeAdmissionContract.contract.md | Admission avant DRY_RUN |

---

## 8. Required schemas

| Schema | Usage OS3 |
|--------|-----------|
| os3_evidence_ticket.schema.json | Validation structurelle |
| decision_ticket.schema.json | Forme du ticket lié |
| intent_envelope.schema.json | IntentEnvelope associé |
| context_packet.schema.json | ContextPackets référencés |
| peripheral_signal_packet.schema.json | Signaux référencés |

---

## 9. Required boundaries

| Boundary | Rôle |
|----------|------|
| X108_GATEWAY_REQUIRED | OS3Evidence s'attache uniquement après décision X108 |
| NO_ACT_FROM_PERIPHERY | OS3Evidence ne déclenche aucun ACT |
| FAIL_CLOSED_PRIORITY | Evidence manquante → fail_closed |
| READONLY_CONTEXT_ONLY | OS3Evidence ne modifie pas Graphiti/Brody |
| EXTERNAL_SIGNALS_SIGNAL_ONLY | temporal receipt = preuve temporelle advisory |
| RSSI_EVIDENCE_ONLY | RSSI future = evidence uniquement |
| RGPD_COMPLIANCE_SCOPE_GUARD | RGPD future = scope guard uniquement |

---

## 10. OS3EvidenceTicket dry-run shape

```yaml
# Forme théorique — documentaire uniquement en P5
os3_evidence_ticket_dry_run:
  evidence_id: "EV-<uuid>-THEORETICAL"
  linked_decision_ticket: "<ticket_id>-THEORETICAL"
  evidence_type: "HASH_CHAIN | REPLAY_LOG | SEAL | DECISION_TRACE | BYPASS_AUDIT_TRACE"

  # Sources d'évidence (théoriques en P5)
  source: "temporal_receipt_C466 | os3_kernel | anti_bypass_spec_p4"
  source_status: "SPEC_ONLY | SPEC_IMPORTED | AUDIT_READY"

  # Hash — PLACEHOLDER en P5
  hash: "sha256(PLACEHOLDER_intent_id + PLACEHOLDER_tick + PLACEHOLDER_nonce)"
  hash_status: "PLACEHOLDER_ONLY"
  hash_claim: false   # jamais affirmer hash réel en P5

  # Replay — indisponible en P5
  replay_ref: null
  replay_status: "NOT_AVAILABLE_IN_P5"
  replay_claim: false

  # Seal — PLACEHOLDER en P5
  seal_ref: null
  seal_status: "PLACEHOLDER_ONLY"
  seal_claim: false

  # Merkle — PLACEHOLDER en P5
  merkle_ref: null
  merkle_status: "PLACEHOLDER_ONLY"
  merkle_claim: false

  # Vérification — documentaire en P5
  verification_status: "NOT_VERIFIED_IN_P5"
  verification_claim: false

  # Custody
  custody_status: "DOCUMENTARY_ONLY"

  # Métadonnées
  claim_scope: "THEORETICAL_ONLY"
  dry_run: true
  can_decide: false
  can_emit_act: false
  can_emit_verdict: false
  advisory_only: true
  world_action: false
```

---

## 11. Link to DecisionTicket

```
OS3EvidenceTicket → s'attache à → DecisionTicket
OS3EvidenceTicket ↛ produit → DecisionTicket
OS3EvidenceTicket ↛ remplace → DecisionTicket

Lien dans les contrats :
  DecisionTicket.evidence_ticket_refs[] → ["EV-<uuid>"]
  OS3EvidenceTicket.linked_decision_ticket → "<ticket_id>"

Direction : OS3Evidence est subordonné au DecisionTicket.
Le DecisionTicket existe d'abord (X108 produit) — OS3Evidence l'annote ensuite.

En P5 : les deux sont THEORETICAL_ONLY — aucun n'est produit réellement.
```

---

## 12. Replay metadata model

```yaml
replay_metadata_dry_run:
  replay_id: "REPLAY-<uuid>-THEORETICAL"
  original_intent_id: "<intent_envelope_id>-THEORETICAL"
  original_decision_ticket_id: "<ticket_id>-THEORETICAL"
  replay_tick: "<original_tick>"
  replay_status: NOT_AVAILABLE_IN_P5

  # En P5 : aucun replay n'est exécuté
  replay_execution: false
  replay_verification: false
  replay_claim: false

  # Futur (post-P5) :
  future_replay_target: true
  replay_invariant: "D1_DETERMINISM — même input → même output"

  # Ce que le replay devra vérifier dans le futur :
  future_checks:
    - "même IntentEnvelope → même DecisionTicket shape"
    - "invariants D1 respectés"
    - "aucun ACT déclenché lors du replay"
    - "OS3EvidenceTicket produit identique ou croissant (P17_AuditGrowth)"
```

---

## 13. Hash / seal / merkle placeholder model

Voir `specs/REPLAY_HASH_SEAL_MERKLE_PLACEHOLDER_MODEL.md` pour le modèle complet.

Règle P5 :

```
JAMAIS affirmer :
  hash = <valeur réelle>
  seal = SEALED
  merkle = VERIFIED
  verification_status = VERIFIED

TOUJOURS dire :
  hash_status = PLACEHOLDER_ONLY
  seal_status = PLACEHOLDER_ONLY
  merkle_status = PLACEHOLDER_ONLY
  verification_status = NOT_VERIFIED_IN_P5
```

---

## 14. Temporal receipt binding

```yaml
temporal_receipt_binding:
  source_packet: 52_temporal_receipt.packet.yaml
  packet_fields_mapped:
    receipt_id → evidence_id_base
    action_intent_hash → hash_ref (PLACEHOLDER)
    tick_window → temporal_context_evidence
    anti_replay_status → replay_integrity_check
    replay_pointer → replay_ref (FUTURE)
    kx108_decision → decision_trace_ref (post-X108 only)
    policy_version → policy_evidence_ref

  binding_condition: "only_after_X108_decides"
  effect_receipt_rule: "effect_receipt_only_after_ACT — C482"

  claim_in_p5: THEORETICAL_ONLY
  not_in_p5: "kx108_decision field (not yet produced)"
```

---

## 15. Anti-bypass evidence binding

```yaml
anti_bypass_evidence_binding:
  source: runtime_contracts/anti_bypass_tests_spec/
  test_matrix_ref: ANTI_BYPASS_TEST_MATRIX.md (60 tests)
  failure_modes_ref: ANTI_BYPASS_FAILURE_MODES.md (25 modes)

  evidence_from_p4:
    bypass_checks_spec: TB-01 to TB-60 (SPEC_ONLY in P4)
    bypass_failure_detected: → evidence_type=BYPASS_AUDIT_TRACE
    boundary_violations: → evidence_type=BOUNDARY_VIOLATION_TRACE

  link_to_os3:
    - OS3EvidenceTicket.evidence_type = BYPASS_AUDIT_TRACE
    - OS3EvidenceTicket.source = "anti_bypass_spec_p4"
    - OS3EvidenceTicket.claim_scope = SPEC_ONLY_P4

  claim_in_p5: SPEC_ONLY — anti-bypass tests not yet executable
  future: anti-bypass execution results → OS3Evidence après gate humaine
```

---

## 16. Allowed operations (P5)

```
✅ Créer des fichiers .md documentaires dans os3_evidence_dry_run/
✅ Décrire la forme théorique d'un OS3EvidenceTicket
✅ Documenter le binding avec DecisionTicket théorique
✅ Décrire les placeholders hash/seal/merkle
✅ Documenter les sources d'evidence et leurs statuts
✅ Créer des exemples JSON documentaires en Markdown
✅ Créer des rapports de traçabilité
✅ Lier aux contrats et boundaries existants
```

---

## 17. Forbidden operations (P5)

```
❌ Calculer un hash réel
❌ Apposer un seal réel
❌ Construire un Merkle tree réel
❌ Exécuter un replay réel
❌ Générer une preuve formelle Lean
❌ Créer un fichier .py
❌ Créer un test exécutable
❌ Modifier le runtime existant
❌ Importer un source pack
❌ Modifier specs/ ou runtime_contracts/ existants sans backup guard
❌ Prétendre que RSSI/RGPD sont certifiés
❌ Prétendre que hash = valeur réelle
❌ Prétendre que OS3Evidence = décision
❌ Prétendre que OS3Evidence remplace X108
❌ Committer ou pousser
```

---

## 18. Failure handling

```
∀ failure mode f : f → fail_closed
∀ failure mode f : f → no_act
∀ failure mode f : f → requires_x108_review
∀ failure mode f : f ↛ allow_by_default
Priorité : BLOCK > HOLD > ALLOW
```

---

## 19. Claim-scope

| Composant | Claim autorisé en P5 |
|-----------|---------------------|
| OS3EvidenceTicket | THEORETICAL_ONLY — documentaire |
| Hash | PLACEHOLDER_ONLY — non calculé |
| Seal | PLACEHOLDER_ONLY — non apposé |
| Merkle | PLACEHOLDER_ONLY — non construit |
| Replay | NOT_AVAILABLE_IN_P5 |
| Vérification | NOT_VERIFIED_IN_P5 |
| DecisionTicket | THEORETICAL_ONLY — X108 seul producteur réel |
| RSSI/RGPD evidence | FUTURE — F03+F78B required |

---

## 20. Future implementation gates

| Gate | Prérequis | Description |
|------|-----------|-------------|
| Hash réel | P5 Spec ✅ + kernel OS3 implémenté | sha256 calculé sur receipt_id + intent_hash + tick |
| Seal réel | Hash réel ✅ + RFC3161 timestamp | Seal cryptographique |
| Merkle réel | Seal réel ✅ + P13_Immutability | Merkle root calculé |
| Replay réel | Merkle réel ✅ + D1_DETERMINISM | Replay exécutable |
| Lean proof P13 | OS3 implémenté | P13_Immutability formal |
| Lean proof P17 | OS3 implémenté | P17_AuditGrowth formal |

---

## 21. Tests required later

```
test_os3_evidence_not_decision_source
test_os3_evidence_required_for_critical
test_hash_placeholder_not_verified
test_seal_placeholder_not_sealed
test_merkle_placeholder_not_built
test_replay_not_available_in_p5
test_evidence_cannot_override_x108
test_evidence_missing_critical_hold
test_rssi_evidence_not_certification
test_rgpd_evidence_not_compliance
```

---

## 22. Proof expected later

```
Lean proofs attendus :
  P13_Immutability — hash ne change pas après seal
  P17_AuditGrowth — audit trail croissant (jamais décroissant)
  merkleRoot_change_if_leaf_change — root change si leaf change

TLA+ specs attendues :
  OS3EvidenceInvariant.tla
  AuditGrowthProperty.tla
  MerkleImmutability.tla
```
