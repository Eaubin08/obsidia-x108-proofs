# WRITABLE_MEMORY_ACTIVATION_CHECKLIST
**Timestamp :** 20260514_003129  
**Mode :** CANDIDATE ONLY — NOT ACTIVE  
**Autorité :** KX108_ONLY

> Ce document définit les conditions requises pour l'activation future du write path mémoire.  
> Aucune action de cette checklist n'est autorisée dans la session actuelle.

---

## État actuel

| Champ | Valeur |
|---|---|
| writable_memory_active | **false** |
| protocol_state | **PROTOCOL_CANDIDATE_ONLY** |
| gates_passing | **0 / 6** |
| operator_approval | **false** |
| real_import_ready | **false** |

---

## A. Conditions minimales avant écriture réelle

- [ ] `operator_approval_required` — Opérateur signe le template d'approbation
- [ ] `writable_memory_protocol_validated` — Ce protocole validé par KX108
- [ ] `graphiti_import_plan_reviewed` — Les 42 candidats revus ligne par ligne par l'opérateur
- [ ] `import_scope_locked` — Batch figé à 42 candidats, aucune extension sans nouvel accord
- [ ] `rollback_plan_required` — Plan de rollback documenté avec batch_id + snapshot Neo4j
- [ ] `post_import_audit_required` — Chemin d'audit post-import défini et validé
- [ ] `x108_boundary_check_required` — KX108 confirme: no kernel_mutation, no x108_merge, no runtime_binding
- [ ] `memory_write_batch_id_required` — Batch ID unique assigné avant tout write
- [ ] `all_42_candidates_reviewed` — Tous les 42 candidats GRAPHITI_001→042 revus
- [ ] `review_excluded_4_remain_excluded_or_uplifted` — 4 TRANSITION candidats restent exclus ou upliftés explicitement
- [ ] `kx108_sole_decision_authority_confirmed` — DECISION_AUTHORITY=KX108_ONLY confirmé en écriture

---

## B. Gates obligatoires (6/6 requises — actuellement 0/6 PASS)

| Gate | gate_id | Statut actuel | Condition de passage |
|---|---|---|---|
| HUMAN_OPERATOR_GATE | GATE_001 | **BLOCKED** | Opérateur signe l'approval template avec `approved=true` et signature valide |
| KX108_BOUNDARY_GATE | GATE_002 | **BLOCKED** | KX108 confirme: no kernel_mutation, no x108_merge, no runtime_binding. DECISION_AUTHORITY=KX108_ONLY confirmé |
| GRAPHITI_IMPORT_SCOPE_GATE | GATE_003 | **BLOCKED** | Scope figé à 42 candidats. Aucune expansion sans nouveau accord opérateur. 4 REVIEW exclus ou upliftés |
| NEO4J_WRITE_SCOPE_GATE | GATE_004 | **BLOCKED** | Neo4j write limité à l'import d'épisodes Graphiti uniquement. Aucune mutation BrodyMemoryDoc directe |
| ROLLBACK_GATE | GATE_005 | **BLOCKED** | batch_id assigné + snapshot Neo4j pré-import référencé + procédure rollback testée en dry-run |
| POST_IMPORT_AUDIT_GATE | GATE_006 | **BLOCKED** | Répertoire d'audit défini + vérification node count + spot-check contenu + BOUNDARY_FALSE re-confirmé |

---

## C. Actions interdites maintenant (10/10 bloquées)

| Action | Bloquée | Raison |
|---|---|---|
| `graphiti_import_executed` | **true** | 0/6 gates pass. Import interdit. |
| `neo4j_write_executed` | **true** | NOT_AUTHORIZED_BY_DESIGN permanent |
| `memory_intake_enabled` | **true** | Protocol pas activé |
| `runtime_binding_enabled` | **true** | KX108_BOUNDARY_GATE BLOCKED |
| `x108_merge` | **true** | KX108_BOUNDARY_GATE BLOCKED |
| `crawler_enabled` | **true** | FROZEN_NOT_ENABLED permanent |
| `post_enabled` | **true** | GET-only validé. POST bloqué. |
| `automatic_import_without_operator` | **true** | HUMAN_OPERATOR_GATE obligatoire |
| `amend_existing_commit` | **true** | Group A staging préservé |
| `git_add_outside_approved_group` | **true** | Authorization opérateur requise |

---

## D. Conditions d'activation future possible

Toutes les conditions suivantes doivent être vraies simultanément :

- [ ] L'opérateur signe le template d'approbation (`approved=true`)
- [ ] Le nombre de candidats d'import est figé (`import_batch_count_fixed=true`)
- [ ] Les 42 candidats ont été revus (`all_42_candidates_reviewed=true`)
- [ ] Les 4 candidats REVIEW restent exclus ou sont explicitement upliftés (`TRANSITION → CRISTAL`)
- [ ] Le protocole writable est validé (`writable_protocol_validated=true`)
- [ ] Un plan de rollback est présent (`rollback_plan_present=true`)
- [ ] Un chemin d'audit est défini (`audit_path_present=true`)
- [ ] KX108 reste seule autorité décisionnelle (`kx108_remains_sole_decision_authority=true`)

---

## E. Template d'approbation opérateur

Fichier : `WRITABLE_MEMORY_OPERATOR_APPROVAL_TEMPLATE.json`

```json
{
  "operator_name": null,          ← À remplir
  "approved": false,              ← Passer à true
  "approved_batch_id": null,      ← Assigner un ID unique
  "approved_candidate_count": 42,
  "excluded_review_count": 4,
  "approval_scope": "SINGLE_BATCH_ONLY",
  "graphiti_write_allowed": false,
  "neo4j_write_allowed": false,
  "memory_intake_allowed": false,
  "signature_required": true,
  "signature_value": null,        ← À remplir
  "approval_timestamp": null      ← À remplir
}
```

> Remplir ce template ne suffit pas à activer le write mode.  
> Les 6 gates doivent passer indépendamment du template.

---

**ÉTAT : CANDIDATE ONLY — ACTIVATION NON AUTORISÉE DANS CETTE SESSION**
