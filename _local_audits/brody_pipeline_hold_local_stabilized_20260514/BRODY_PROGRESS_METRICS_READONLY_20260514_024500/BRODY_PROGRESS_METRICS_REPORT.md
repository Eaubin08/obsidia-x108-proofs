# BRODY PROGRESS METRICS — READONLY REPORT
## Mission: BRODY_PROGRESS_METRICS_READONLY
## Timestamp: 20260514_024500
## Status: COMPLETE | READONLY | ALL_VERDICTS_PASS

---

## Résumé final

```
BRODY_PROGRESS_METRICS_READONLY_DONE
LOW_MATERIAL_RESOLVED               = true
TREE_TAGGING_T01_T12_CONFIRMED      = true
T13_T34_PENDING_ADDITIONAL_SIGNAL   = true
MEMORY_PIPELINE_STABLE              = true
EXTERNAL_FETCH_GET_ONLY_VALIDATED   = true
OPERATOR_LOOP_VALIDATED             = true
BOUNDARY_ALL_FALSE                  = true
CURRICULUM_READINESS_CREATED        = true
FRANCAIS_READY                      = PARTIAL_READY
LOGIQUE_READY                       = PARTIAL_READY
MATHS_SIMPLES_READY                 = PARTIAL_READY
SCIENCE_READY                       = PARTIAL_READY
PHYSIQUE_READY                      = PENDING_ADDITIONAL_SIGNAL
MONDE_LARGE_READY                   = PENDING_ADDITIONAL_SIGNAL
NEW_WRITE_EXECUTED                  = false
NEO4J_WRITE_EXECUTED                = false
GRAPHITI_WRITE_EXECUTED             = false
MEMORY_INTAKE                       = false
RUNTIME_BINDING_ALLOWED             = false
X108_MERGE                          = false
DECISION_AUTHORITY                  = KX108_ONLY
GROUP_A_STAGED_PRESERVED            = true
STAGED_FILES_STILL                  = 136
```

---

## A — Corpus / Mémoire

| Métrique | Valeur |
|---|---|
| BrodyMemoryDoc total | 3267 |
| BrodyImportedMemory total | 42 |
| Nodes avec text_preview | 3267 / 3267 |
| LOW_MATERIAL résolu | true |
| body_non_empty_rate | 100% |
| Batch import intact | BRODY_REAL_IMPORT_20260514_003636 ✓ |

---

## B — Tagging / Arbres

| Métrique | Valeur |
|---|---|
| Arbres total | 34 |
| Arbres taggés précis | 12 (T01-T12) |
| Arbres pending signal | 13 (T13-T19, T23, T25-T29) |
| Arbres bloqués | 9 (T20-T22, T24, T30-T34) |
| Familles total | 8 |
| Familles actives | 3 (I, II, III) |
| Nodes taggés | 48 |
| Tags ajoutés | 96 |
| Coverage corpus tagué | 1.75% (48/2739) |

### Distribution familles

| Famille | Arbres | Docs |
|---|---|---|
| I_FONDAMENTAUX | T01-T05 | 20 |
| II_COGNITIFS | T06-T10 | 20 |
| III_CONNAISSANCE | T11-T12 | 8 |
| IV-VII | T13-T29 | 0 (PENDING) |
| VIII_OBSIDIA_AGI | T30-T34 | 0 (BLOCKED) |

---

## C — Mémoire candidate

| Métrique | Valeur |
|---|---|
| Décisions consommées | 51 |
| Candidats mémoire | 42 |
| En attente review | 4 |
| Rejetés | 4 |
| Reflex boundary review | 1 |
| Batch Graphiti importé | 42 |
| user_memory_schema_active | false |
| auto_write_enabled | false |

---

## D — External fetch / scraping

| Métrique | Valeur |
|---|---|
| GET-only validé | true |
| Allowlist active | true (example.com) |
| POST bloqué | true |
| Crawler bloqué | true |
| Secret pattern bloqué | true |
| Localhost bloqué | true |
| Tests négatifs bloqués | 7/7 |
| Receipt créé | true |
| sha256 stable | fb91d75a6bb4... |

---

## E — Boucle opérateur

| Métrique | Valeur |
|---|---|
| Scénarios testés | 5 |
| Scénarios passés | 5/5 |
| Mutation dangereuse bloquée | true |
| Reflex alerts | kernel_mutation, commit_push, x108_merge |
| Receipt validation | PASS |
| Operator gate requis | true |
| Brody never executed | 5/5 |
| Boundaries intact | 5/5 |

---

## F — Refus / Boundary

| Boundary | Valeur |
|---|---|
| brody_execute_allowed | false |
| brody_authorize_allowed | false |
| x108_merge | false |
| runtime_binding_allowed | false |
| memory_decision | false |
| decision_authority | KX108_ONLY |
| correct_refusal_rate | 5/5 |
| boundary_all_false | true |
| neo4j_write (toutes missions) | false |
| graphiti_write (toutes missions) | false |
| memory_intake (toutes missions) | false |

---

## G — Curriculum Readiness

| Curriculum | Statut | Familles requises | Tags disponibles | Tags manquants | Risque |
|---|---|---|---|---|---|
| FRANCAIS | PARTIAL_READY | I, III | T01-T05, T11-T12 | — | LOW |
| LOGIQUE | PARTIAL_READY | II | T06-T10 | — | LOW |
| MATHS_SIMPLES | PARTIAL_READY | II | T06-T10 | — | LOW |
| SCIENCE | PARTIAL_READY | III, IV | T11-T12 | T13-T17 | MEDIUM |
| PHYSIQUE | PENDING | IV, V | — | T13-T19 | HIGH |
| MONDE_LARGE | PENDING | VI, VII | — | T23-T29 | HIGH |

**Clé** : PARTIAL_READY = familles de base disponibles, couverture incomplète. PENDING = 0 docs taggés dans les familles requises.

---

## Prochain déblocage

Le seul blocage est **T13-T34 = 0 docs avec `_Tnn__` dans le titre**.

→ **BRODY_CURRICULUM_TREE_BRIDGE_READONLY** : chercher signal alternatif (text_preview, path, tags existants, noms complets des arbres).

Si trouvé → nouveau DRY_RUN → gate → écriture contrôlée T13-T29.

---

## Navigation

```
← BRODY_CANONICAL_TAGGING_POST_WRITE_AUDIT_READONLY_20260514_023500
→ BRODY_CURRICULUM_TREE_BRIDGE_READONLY
```
