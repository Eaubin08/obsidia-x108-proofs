# REPLAY_HASH_SEAL_MERKLE_PLACEHOLDER_MODEL
# runtime_contracts/os3_evidence_dry_run/specs/
# Plan 3 P5 — Modèle placeholder documentaire — NO HASH / NO SEAL / NO MERKLE / NO REPLAY
# Date: 2026-06-02
# Status: OS3_EVIDENCE_SPEC_ONLY

---

## Règle absolue P5

```
JAMAIS en P5 :
  hash_status = VERIFIED
  seal_status = SEALED
  merkle_status = VERIFIED
  replay_status = COMPLETED
  verification_status = VERIFIED

TOUJOURS en P5 :
  Tous les statuts = PLACEHOLDER_ONLY | NOT_AVAILABLE_IN_P5 | DOCUMENTARY_ONLY
  Aucun calcul réel. Aucune exécution réelle.
```

---

## 1. replay_ref / replay_status

### Statuts autorisés

| Valeur | Description | Utilisable en P5 |
|--------|-------------|-----------------|
| NOT_AVAILABLE_IN_P5 | Replay non exécuté — P5 documentaire | ✅ OUI |
| FUTURE_DRY_RUN_TARGET | Cible future pour dry-run replay | ✅ OUI |
| FUTURE_EXECUTABLE_TARGET | Cible future pour test exécutable | ✅ OUI |
| VERIFIED_LATER | Sera vérifié après implémentation réelle | ✅ OUI |
| COMPLETED | Replay exécuté et vérifié | ❌ NON en P5 |
| PASS | Replay a passé | ❌ NON en P5 |
| FAIL | Replay a échoué | ❌ NON en P5 |

### Modèle documentaire

```yaml
replay_placeholder:
  replay_ref: "REPLAY-<uuid>-PLACEHOLDER"
  replay_status: "NOT_AVAILABLE_IN_P5"
  replay_claim: false
  replay_computation: false
  replay_execution: false
  invariant_target: "D1_DETERMINISM — même input → même output"
  future_gate: "post-P5 + Lean D1 proof + kernel replay module"

  # Ce que le replay vérifiera dans le futur :
  future_checks:
    - "IntentEnvelope input identique → DecisionTicket output identique"
    - "Aucun ACT déclenché lors du replay"
    - "OS3EvidenceTicket produit identique (immutabilité)"
    - "P17_AuditGrowth : audit trail ne diminue pas"
```

---

## 2. hash_ref / hash_status

### Statuts autorisés

| Valeur | Description | Utilisable en P5 |
|--------|-------------|-----------------|
| PLACEHOLDER_ONLY | Hash documentaire non calculé | ✅ OUI |
| NOT_COMPUTED_IN_P5 | Non calculé en P5 | ✅ OUI |
| FUTURE_HASH_TARGET | Cible future | ✅ OUI |
| VERIFIED_LATER | Sera calculé et vérifié | ✅ OUI |
| sha256_VERIFIED | Hash calculé et vérifié | ❌ NON en P5 |
| COMPUTED | Hash calculé | ❌ NON en P5 |

### Modèle documentaire

```yaml
hash_placeholder:
  hash_ref: "sha256(PLACEHOLDER_receipt_id + PLACEHOLDER_intent_hash + PLACEHOLDER_tick)"
  hash_status: "PLACEHOLDER_ONLY"
  hash_value: null   # jamais de valeur réelle en P5
  hash_claim: false
  hash_computation: false

  # Formule future (documentaire) :
  future_formula: |
    sha256(
      receipt_id + 
      action_intent_hash + 
      tick_window + 
      kx108_decision_trace
    )
  
  invariant_target: "merkleRoot_change_if_leaf_change"
  future_gate: "post-P5 + OS3 kernel hash module + Lean proof P13"
```

---

## 3. seal_ref / seal_status

### Statuts autorisés

| Valeur | Description | Utilisable en P5 |
|--------|-------------|-----------------|
| PLACEHOLDER_ONLY | Seal documentaire non apposé | ✅ OUI |
| NOT_SEALED_IN_P5 | Non scellé en P5 | ✅ OUI |
| FUTURE_SEAL_TARGET | Cible future | ✅ OUI |
| VERIFIED_LATER | Sera scellé plus tard | ✅ OUI |
| SEALED | Seal réel apposé | ❌ NON en P5 |
| RFC3161_SEALED | Timestampé RFC3161 | ❌ NON en P5 |

### Modèle documentaire

```yaml
seal_placeholder:
  seal_ref: "SEAL-<uuid>-PLACEHOLDER"
  seal_status: "PLACEHOLDER_ONLY"
  seal_timestamp: null   # pas de timestamp RFC3161 réel en P5
  seal_claim: false
  seal_execution: false

  # Processus futur (documentaire) :
  future_process: |
    1. Hash calculé sur OS3EvidenceTicket
    2. RFC3161 timestamp service appelé
    3. Seal token retourné et stocké
    4. P13_Immutability invariant vérifié

  invariant_target: "P13_Immutability"
  future_gate: "post-P5 + RFC3161 integration + Lean proof P13"
```

---

## 4. merkle_ref / merkle_status

### Statuts autorisés

| Valeur | Description | Utilisable en P5 |
|--------|-------------|-----------------|
| PLACEHOLDER_ONLY | Merkle documentaire non construit | ✅ OUI |
| NOT_BUILT_IN_P5 | Non construit en P5 | ✅ OUI |
| FUTURE_MERKLE_TARGET | Cible future | ✅ OUI |
| VERIFIED_LATER | Sera construit et vérifié | ✅ OUI |
| VERIFIED | Merkle vérifié | ❌ NON en P5 |
| ROOT_COMPUTED | Root calculé | ❌ NON en P5 |

### Modèle documentaire

```yaml
merkle_placeholder:
  merkle_ref: "MERKLE-<uuid>-PLACEHOLDER"
  merkle_root: null   # jamais de valeur réelle en P5
  merkle_status: "PLACEHOLDER_ONLY"
  merkle_leaf_ref: "<hash_ref>-PLACEHOLDER"
  merkle_claim: false
  merkle_computation: false

  # Structure future (documentaire) :
  future_structure: |
    MerkleTree {
      leaves: [sha256(evidence_1), sha256(evidence_2), ...]
      root: sha256(sha256(leaf_1) + sha256(leaf_2) + ...)
    }
    
  invariant_target: "merkleRoot_change_if_leaf_change — invariant kernel"
  future_gate: "post-P5 + Merkle kernel module + Lean P13 proof"
```

---

## 5. verification_status / custody_status

### verification_status — statuts autorisés

| Valeur | Description | Utilisable en P5 |
|--------|-------------|-----------------|
| NOT_VERIFIED_IN_P5 | Non vérifié — P5 documentaire | ✅ OUI |
| DOCUMENTARY_ONLY | Documentaire uniquement | ✅ OUI |
| FUTURE_VERIFICATION_TARGET | Cible future | ✅ OUI |
| VERIFIED_LATER | Sera vérifié | ✅ OUI |
| UNVERIFIED | Non vérifié (documentaire honnête) | ✅ OUI |
| VERIFIED | Vérifié | ❌ NON en P5 |
| PASS | Vérification passée | ❌ NON en P5 |

### custody_status — statuts autorisés

| Valeur | Description | Utilisable en P5 |
|--------|-------------|-----------------|
| DOCUMENTARY_ONLY | Documentation uniquement | ✅ OUI |
| CHAIN_NOT_BUILT_IN_P5 | Chaîne de custody non construite | ✅ OUI |
| FUTURE_CUSTODY_TARGET | Cible future | ✅ OUI |
| VERIFIED_CHAIN | Chaîne vérifiée | ❌ NON en P5 |

---

## 6. Synthèse — valeurs autorisées P5

```yaml
# OS3EvidenceTicket placeholder complet — P5 maximal
os3_evidence_placeholder_p5:
  evidence_id: "EV-<uuid>-PLACEHOLDER"
  linked_decision_ticket: "<ticket_id>-THEORETICAL"
  evidence_type: "HASH_CHAIN | REPLAY_LOG | BYPASS_AUDIT_TRACE | DECISION_TRACE"
  source: "<source_identifier>"
  source_status: "SPEC_ONLY | SPEC_IMPORTED | AUDIT_READY"
  
  hash: "sha256(PLACEHOLDER...)"
  hash_status: "PLACEHOLDER_ONLY"
  
  replay_ref: null
  replay_status: "NOT_AVAILABLE_IN_P5"
  
  seal_ref: null
  seal_status: "PLACEHOLDER_ONLY"
  
  merkle_ref: null
  merkle_status: "PLACEHOLDER_ONLY"
  
  verification_status: "NOT_VERIFIED_IN_P5"
  custody_status: "DOCUMENTARY_ONLY"
  
  claim_scope: "THEORETICAL_ONLY"
  dry_run: true
  can_decide: false
  can_emit_act: false
  advisory_only: true
  world_action: false
  
  # Assertions interdites en P5
  hash_is_real: false
  seal_is_real: false
  merkle_is_real: false
  replay_executed: false
  proof_generated: false
  rssi_certified: false
  rgpd_compliant: false
```

---

## 7. Mapping invariants → placeholders futurs

| Invariant | Placeholder P5 | Future gate |
|-----------|---------------|-------------|
| P13_Immutability | seal_status=PLACEHOLDER_ONLY | RFC3161 + Lean P13 |
| merkleRoot_change_if_leaf_change | merkle_status=PLACEHOLDER_ONLY | Merkle kernel + Lean |
| P17_AuditGrowth | replay_status=NOT_AVAILABLE | Replay module + Lean P17 |
| D1_DETERMINISM | verification_status=NOT_VERIFIED | Replay + Lean D1 |
| aggregate4_fail_closed | custody_status=DOCUMENTARY | Kernel OS3 |
