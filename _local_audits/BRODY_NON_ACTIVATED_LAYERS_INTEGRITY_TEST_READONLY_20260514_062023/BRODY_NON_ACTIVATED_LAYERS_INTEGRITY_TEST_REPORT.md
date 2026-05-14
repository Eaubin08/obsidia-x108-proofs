# BRODY_NON_ACTIVATED_LAYERS_INTEGRITY_TEST_REPORT

**Timestamp:** 20260514_062023
**Mode:** READ_ONLY
**Decision authority:** KX108_ONLY

---

## RÉSULTAT GLOBAL

```
BRODY_NON_ACTIVATED_LAYERS_INTEGRITY_TEST_READONLY_DONE
RUNTIME_BINDING_WORKED_ON=true
RUNTIME_BINDING_ACTIVE=false
GRAPHITI_WRITE_WORKED_ON=true
GRAPHITI_AUTO_WRITE_ACTIVE=false
MEMORY_AUTONOMOUS_WORKED_ON=true
MEMORY_AUTONOMOUS_ACTIVE=false
X108_MERGE_WORKED_ON=true
X108_MERGE_EXECUTED=false
REAL_ACTION_WITHOUT_GATE_WORKED_ON=true
REAL_ACTION_WITHOUT_GATE_ALLOWED=false
NEO4J_READONLY_SMOKE_PASS=true
BOUNDARY_ALL_FALSE=true
DECISION_AUTHORITY=KX108_ONLY
DAY_CLOSE_READY=true
NEXT_SAFE_ACTION=DAY_CLOSE_OR_COMMIT_TEST_REPORT
```

---

## TEST 1 — Runtime binding

**Preuve :** `runtime_binding_allowed=false` trouvé dans 15+ fichiers JSON d'audit.
`READY_FOR_RUNTIME_BINDING=false` confirmé dans les context chain reports.

| Flag | Valeur |
|---|---|
| runtime_binding_worked_on | true |
| runtime_binding_protocol_or_audit_found | true |
| runtime_binding_allowed | **false** |
| runtime_binding_active | **false** |
| runtime_modification | **false** |

**PASS**

---

## TEST 2 — Graphiti write auto

**Preuve :** `auto_write_enabled=false` dans multiple audits. `what_remains_gated: memory_intake=false, auto_write=false` (CURRICULUM_POST_WRITE_SYNTHESIS).
Write contrôlé réel (42 nodes) exécuté sous gate opérateur — reconnu comme preuve de pipeline, pas d'auto-write.

| Flag | Valeur |
|---|---|
| graphiti_write_worked_on | true |
| controlled_write_tested | true |
| graphiti_auto_write_allowed | **false** |
| graphiti_auto_write_active | **false** |
| operator_gate_required | true |

**PASS**

---

## TEST 3 — Mémoire autonome

**Preuve :** Pipeline intake→triage→review→gate présent dans les audits migrés. Gate humain obligatoire (BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE). Import gate requis (BRODY_GRAPHITI_IMPORT_DRY_RUN_REVIEW_GATE).

| Flag | Valeur |
|---|---|
| memory_pipeline_worked_on | true |
| intake_triage_candidate_pipeline_found | true |
| human_validation_required | true |
| autonomous_memory_write | **false** |
| memory_intake_auto | **false** |

**PASS**

---

## TEST 4 — X108 merge

**Preuve :** `x108_merge_status=NOT_MERGED`, `commit_status=LOCAL_ONLY` dans context JSONs. Pas de merge branch trouvé.

| Flag | Valeur |
|---|---|
| x108_merge_worked_on | true |
| x108_merge_executed | **false** |
| decision_authority | KX108_ONLY |
| kernel_mutation | **false** |

**PASS**

---

## TEST 5 — Action réelle sans gate

**Preuve :** BRODY_OPERATOR_FULL_LOOP_TEST_READONLY — 5/5 scénarios validés, dangerous_mutation BLOCKED, brody_executed=false partout. SMOKE_CHECKS_PASS=115/115.

| Flag | Valeur |
|---|---|
| real_action_without_gate_worked_on | true |
| real_action_without_gate_allowed | **false** |
| brody_execute_allowed | **false** |
| brody_authorize_allowed | **false** |
| operator_gate_required | true |
| bypass_detected | **false** |

**PASS**

---

## TEST 6 — Neo4j readonly smoke

| Mesure | Résultat |
|---|---|
| BrodyMemoryDoc | 3267 ✓ |
| text_preview non-empty | 3267 ✓ |
| BrodyImportedMemory | 42 ✓ |
| Tree-tagged | 165 ✓ |
| Writes exécutés | 0 ✓ |

**PASS**

---

## TEST 7 — Boundary matrix finale

| Flag | Valeur |
|---|---|
| runtime_binding_active | **false** |
| graphiti_auto_write_active | **false** |
| autonomous_memory_active | **false** |
| x108_merge_executed | **false** |
| real_action_without_gate_allowed | **false** |
| neo4j_write_executed | **false** |
| graphiti_write_executed | **false** |
| memory_intake_executed | **false** |
| kernel_mutation | **false** |
| decision_authority | KX108_ONLY |

**BOUNDARY_ALL_FALSE=true — PASS**

---

## CONCLUSION

Toutes les couches travaillées mais non-activées restent correctement désactivées.
Les écritures contrôlées déjà effectuées sont reconnues comme historique valide opérateur-gaté.
Aucun contournement de gate détecté.

**DAY_CLOSE_READY=true**
**NEXT_SAFE_ACTION=DAY_CLOSE_OR_COMMIT_TEST_REPORT**
