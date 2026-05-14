# BRODY PATH_B TAGGING DRY-RUN — READONLY REPORT
## Mission: BRODY_PATH_B_TAGGING_DRY_RUN_READONLY
## Timestamp: 20260514_031500
## Status: COMPLETE | READONLY | PATH_B_SIGNAL_FOUND

---

## Résumé final

```
BRODY_PATH_B_TAGGING_DRY_RUN_READONLY_DONE
PATH_B_SIGNAL_FOUND               = true
T13_T34_TREE_COUNT_WITH_SIGNAL    = 22 / 22
PATH_B_CANDIDATES_PATH_SLUG       = 117  ← PRIOR ASSUMPTION VALIDÉE
PATH_B_CANDIDATES_TP_GENUINE      = 78   ← NOUVELLE DÉCOUVERTE
PATH_B_CANDIDATES_TP_MULTI_TREE   = 2    ← REVIEW_REQUIRED
PATH_B_META_EXCLUDED              = 19   ← CONTAMINATION CROSS-TREE
PATH_B_RAW_SAFE_TOTAL             = 216  ← (117 + 78 + 2 + 19)
PATH_B_RECOMMENDED_WRITE          = 117  ← PATH_SLUG uniquement
PATH_B_BLOCKED_TREE_NODES         = 136
HEURISTIC_TAGGING                 = false
LLM_GUESSING                      = false
INVENTION                         = false
NEW_WRITE_EXECUTED                = false
NODE_COUNT_UNCHANGED              = true (3267)
GROUP_A_STAGED_PRESERVED          = true (136 files)
DECISION_AUTHORITY                = KX108_ONLY
NEXT_ACTION                       = BRODY_PATH_B_TAGGING_REVIEW_GATE_READONLY
```

---

## Résultat critique : 216 ≠ 117

L'hypothèse initiale de 117 candidats était **correcte pour le signal PATH_SLUG uniquement**.

Le scan complet (PATH + TEXT_PREVIEW) révèle 216 nodes dans les safe trees.

| Signal | Candidats | Confiance | Disposition |
|---|---|---|---|
| PATH_SLUG | **117** | 0.98 | CANDIDATE — recommandé pour write |
| TEXT_PREVIEW_SLUG (genuines) | **78** | 0.88 | CANDIDATE — requires_operator_review |
| TEXT_PREVIEW multi-tree | **2** | 0.50 | REVIEW_REQUIRED_MULTI_TREE |
| META_DOCUMENT cross-tree | **19** | 0.10 | EXCLUDED |
| **Total safe scan** | **216** | — | — |

---

## Contamination META détectée

### GRAPHITI_V2_002404 — arbres_34.canon.json
- Apparaît dans **6 trees** : T13, T14, T15, T16, T17, T18
- Cause : registre canonical qui liste tous les 34 folders
- Disposition : **EXCLUDED_META_DOCUMENT**

### GRAPHITI_V2_003250 — brody_taxonomy_mapper_34_8_readonly_v1_6_4d.py
- Apparaît dans **21 trees** : T13-T33
- Cause : script Python qui référence tous les 34 arbres
- Disposition : **EXCLUDED_META_DOCUMENT**

### GRAPHITI_V2_000694 — 48AAB2F1C286_demo_output_context_packet.json
- Apparaît dans **2 trees** : T18 + T26
- Cause : contexte demo qui référence les deux folders
- Disposition : **REVIEW_REQUIRED_MULTI_TREE** (ne peut pas être tagué T18 ET T26 sans décision opérateur)

---

## Préflight — tous passés

| Check | Résultat |
|---|---|
| baseline node count | 3267 |
| post-scan node count | 3267 (inchangé) |
| BrodyImportedMemory | 42 |
| T01-T12 tags présents | true (4 nodes × 12 arbres = 48) |
| T13-T34 currently tagged | 0 |
| write guard | PASS |
| staged files | 136 |

---

## Signal PATH_SLUG — 9 nodes par arbre (identique à la découverte initiale)

Chaque arbre T13-T34 a exactement **9 nodes** avec `n.path CONTAINS 'ARBRE_nn__CanonicalName'` :
- activation_rules.md
- definition.md
- examples_events.md
- links_to_other_trees.json
- node_registry.json
- README.md
- risks_confusions.md
- tensor_coordinates.json
- tests.md

Ces 9 docs × 13 safe trees = **117 nodes PATH_SLUG** confirmés.

---

## Signal TEXT_PREVIEW_SLUG — GRAPHITI_SERIALIZED (genuines)

6-7 nodes supplémentaires par arbre ont le folder slug dans leur `text_preview` uniquement.
Ces nodes sont des copies GRAPHITI-sérialisées des mêmes documents sources (titres hash-préfixés,  path=empty).

**Ils ne sont pas des hallucinations.** Ce sont de vraies copies de contenu T13-T34, mais leur signal source est moins direct que PATH_SLUG.

→ Requires_operator_review=true pour décision sur inclusion dans write gate.

---

## Plan proposé : 117 PATH_SLUG

```
BRODY_PATH_B_TAGGING_REVIEW_GATE_READONLY
  → Revue des 117 candidats PATH_SLUG (CANDIDATE_PATH_SLUG.jsonl)
  → Gate phrase: "J'autorise l'ecriture canonique PATH_B des 117 nodes"
  → BRODY_PATH_B_TAGGING_CONTROLLED_WRITE_V1 (117 nodes)
  → Tags: Tnn + family_id APPEND_ONLY
  → 234 tags totaux
```

**Option étendue** (si opérateur valide) :
```
  → Revue des 78 TP_GENUINE nodes (CANDIDATE_TP_GENUINE.jsonl)
  → Gate phrase étendue: "J'autorise l'ecriture PATH_B des 195 nodes (117 PATH_SLUG + 78 TP_GENUINE)"
  → 390 tags totaux (195 nodes × 2 tags)
```

---

## Curriculum impact prévisionnel (PATH_SLUG write uniquement)

| Stage | Avant | Après write | Note |
|---|---|---|---|
| FRANCAIS | EVAL_PASS 3/3 | EVAL_PASS 3/3 | Inchangé |
| LOGIQUE | PARTIAL 3/5 | PROJECTION_FULL 5/5 | T26+T27 ajoutés |
| MATHS_SIMPLES | PARTIAL 5/6 | PROJECTION_FULL 6/6 | T26 ajouté |
| SCIENCE | PARTIAL 2/5 | PROJECTION_FULL 5/5 | T14+T26+T27 ajoutés |
| PHYSIQUE | PARTIAL 2/6 | PROJECTION_FULL 6/6 | T23+T25+T26+T27 ajoutés |
| MONDE_LARGE | NO_TEST 0/13 | PROJECTION_PARTIAL 4/13 | T16-T19 ajoutés; 9 bloqués |

**Important** : "PROJECTION_FULL" = non confirmé. EVAL_PASS réel requiert write + GET-only post-write test.

---

## Navigation

```
← BRODY_CURRICULUM_GET_ONLY_EVAL_READONLY_20260514_030000
→ BRODY_PATH_B_TAGGING_REVIEW_GATE_READONLY (immédiat, READONLY)
  → Gate: "J'autorise l'ecriture canonique PATH_B des 117 nodes"
  → BRODY_PATH_B_TAGGING_CONTROLLED_WRITE_V1
  → BRODY_CURRICULUM_GET_ONLY_EVAL_READONLY (all stages)
```
