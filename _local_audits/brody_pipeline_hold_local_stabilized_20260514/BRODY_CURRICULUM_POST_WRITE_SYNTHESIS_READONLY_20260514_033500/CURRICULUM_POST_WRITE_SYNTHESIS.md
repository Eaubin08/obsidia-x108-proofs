# CURRICULUM POST-WRITE SYNTHESIS
## BRODY_CURRICULUM_POST_WRITE_SYNTHESIS_READONLY
## Timestamp: 20260514_033500 | Status: COMPLETE_READONLY

---

## Vue d'ensemble

Cette synthèse couvre l'ensemble du pipeline Brody depuis l'état initial (LOW_MATERIAL, zéro tagging, boucle non testée) jusqu'à l'état final après BRODY_PATH_B_END_TO_END_CONTROLLED_WRITE_AND_EVAL.

**Résultat global : tous les objectifs initiaux sont atteints ou partiellement atteints par design.**

---

## Ce qui est réellement écrit dans Neo4j

### Écriture 1 — PATH_A (BRODY_CANONICAL_TAGGING_CONTROLLED_WRITE_V1, 20260514_022400)

| Paramètre | Valeur |
|-----------|--------|
| Nodes modifiés | 48 |
| Tags ajoutés | 96 |
| Arbres couverts | T01–T12 (12 arbres) |
| Familles | I_FONDAMENTAUX (20), II_COGNITIFS (20), III_CONNAISSANCE (8 pour T11/T12) |
| Signal | TITLE_REGEX `_Tnn__` — confidence 0.99 |
| Post-write audit | 10/10 PASS |
| Rollback | PATH_A_ROLLBACK_PLAN.cypher (48 statements) — non exécuté |

### Écriture 2 — PATH_B (BRODY_PATH_B_END_TO_END_CONTROLLED_WRITE_AND_EVAL, 20260514_032500)

| Paramètre | Valeur |
|-----------|--------|
| Nodes modifiés | 117 |
| Tags ajoutés | 234 |
| Arbres couverts | T13–T19, T23, T25–T29 (13 arbres, safe trees uniquement) |
| Familles | III_CONNAISSANCE (+27), IV_RELATIONNELS_SOCIAUX (36), VI_TEMPORELS_MEMORIELS (18), VII_META_STRUCTURELS (36) |
| Signal | PATH_SLUG `n.path CONTAINS folder_slug` — confidence 0.98 |
| Post-write audit | 12/12 PASS |
| Rollback | PATH_B_ROLLBACK_PLAN.cypher (117 statements) — non exécuté |

### Écriture 3 — BrodyImportedMemory (BRODY_GRAPHITI_REAL_IMPORT_CONTROLLED_WRITE_TEST_V1, 20260514_003636)

| Paramètre | Valeur |
|-----------|--------|
| Nodes écrits | 42 |
| Label | BrodyImportedMemory |
| Batch ID | BRODY_REAL_IMPORT_20260514_003636 |
| Post-write audit | 7/7 PASS |
| Rollback | DETACH DELETE sur batch_id — disponible |

### Total écrit

| Métrique | Valeur |
|----------|--------|
| BrodyMemoryDoc nodes tagués | 165 (48 + 117) |
| Tags ajoutés | 330 (96 + 234) |
| Arbres couverts | 21/34 (25 safe, 9 blocked, 9 blocked/MONDE_LARGE) |
| BrodyImportedMemory | 42 |
| BrodyMemoryDoc total | 3267 (inchangé) |

---

## Ce qui reste readonly / non écrit

| Domaine | Statut | Raison |
|---------|--------|--------|
| PATH_B Tier 2 (78 nodes TP_GENUINE) | NON ÉCRIT | Gate opérateur non ouvert |
| T20/T21/T22/T24/T30-T34 | NON TAGUÉ | Bloqués par design |
| GRAPHITI_V2_000694 (multi-tree) | NON TAGUÉ | Ambiguïté T18/T26 non résolue |
| BrodyUserMemory schema | NON DÉPLOYÉ | Conception non faite |
| Graphiti V20 frozen | INCHANGÉ | Readonly |
| Runtime binding | BLOQUÉ | RUNTIME_BINDING_ALLOWED=false |
| X108 merge | BLOQUÉ | X108_MERGE=false |
| GROUP_A commit | NON COMMITÉ | Autorisation explicite requise |

---

## Pourquoi MONDE_LARGE reste EVAL_PASS_PARTIAL

MONDE_LARGE requiert 13 arbres : T16/T17/T18/T19/T20/T21/T22/T24/T30-T34.

- T16/T17/T18/T19 : **testés, PASS** (9 nodes chacun)
- T20/T21/T22 : **BLOCKED_ACTION_TRIGGER** — décision opérateur intentionnelle
- T24 : **BLOCKED_DIRECT_MEMORY_WRITE** — décision opérateur intentionnelle
- T30-T34 : **BLOCKED_AGI_LAYER** — décision opérateur intentionnelle

Ce n'est pas un problème de signal ou de données. Les 9 arbres bloqués ont leurs nodes dans Neo4j (signal PATH_SLUG présent) mais l'autorisation de les tagger est refusée par design. Le verdict EVAL_PASS_PARTIAL est correct et attendu.

**Pour débloquer MONDE_LARGE vers EVAL_PASS :** décision opérateur explicite arbre par arbre + gate KX108 pour chaque famille bloquée (PATH_C).

---

## Preuves par objectif

| Objectif | Preuve principale | Fichier source |
|----------|-------------------|----------------|
| LOW_MATERIAL corrigé | PWV_12 PASS / CHECK_07 PASS / low_material_resolved=true | PATH_B_POST_WRITE_VALIDATION.json / CANONICAL_TAGGING_POST_WRITE_AUDIT_REPORT.json |
| Mémoire stable | memory_pipeline_stable=true / 42 BrodyImportedMemory | BRODY_PROGRESS_METRICS_REPORT.json |
| External fetch validé | GET_TREE_005 PASS / 7 négatifs bloqués | BRODY_WORLD_TREE_GET_ONLY_TEST_READONLY_REPORT.json |
| Boucle opérateur | E_operator_loop.scenarios_passed=5 / SMOKE=115/115 | BRODY_PROGRESS_METRICS_REPORT.json |
| Curriculum progressif | 5/6 EVAL_PASS / 12/12 PWV PASS | PATH_B_CURRICULUM_EVAL_SUMMARY_MATRIX.json |
| Métriques créées | verdicts A-G tous PASS | BRODY_PROGRESS_METRICS_REPORT.json |

---

## Prochain palier recommandé

**Recommandation prioritaire A (sans risque, immédiat) :**

```
GROUP_A_COMMIT — 136 fichiers stagés, dry-run fait, message préparé
Trigger : "Commit GROUP_A"
```

**Recommandation B (parallel-available, readonly) :**

```
BRODY_RUNTIME_BINDING_RISK_REVIEW_READONLY
BRODY_CANONICAL_TAGGING_TIER2_DRY_RUN_READONLY
```

**Recommandation C (long terme, gate KX108) :**

```
PATH_C — déblocage MONDE_LARGE arbre par arbre (T20-T34)
```

---

## Invariants vérifiés

- NODE_COUNT_UNCHANGED = true (3267)
- NO_NEO4J_WRITE_IN_SYNTHESIS = true
- NO_GRAPHITI_WRITE = true
- NO_MEMORY_INTAKE = true
- NO_RUNTIME_BINDING = true
- NO_X108_MERGE = true
- NO_GIT_ADD = true
- BLOCKED_TREES_TAGGED = false
- ROLLBACK_READY = true (PATH_A + PATH_B)
- DECISION_AUTHORITY = KX108_ONLY
