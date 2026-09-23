# P37 — Runtime Function Inventory Graph — Rapport

**Date :** 2026-06-04  
**Branche :** p10-real-engine-controlled-bridge  
**Palier :** P37  
**Statut :** P37_RUNTIME_FUNCTION_INVENTORY_GRAPH_READY  

---

## Résumé

P37 construit un inventaire machine-readable de la machination réelle du repo Obsidia X-108, puis le connecte au routeur de capacités P36.  

**Découverte statique AST** — aucune exécution, aucun import dynamique.  
**Cache module-level** — construit une fois, réutilisé à chaud.  
**Invariants permanents** : `runtime_allowed_now = False`, `emits_act = False`, `decision_authority = KX108_ONLY`, `readonly = True`.

---

## Fichiers créés / modifiés

| Fichier | Rôle | Statut |
|---|---|---|
| `runtime_wiring/source_runtime/runtime_inventory_builder.py` | Scan AST statique → modules/fonctions/classes/routes/adapters/tests/docs | CRÉÉ |
| `runtime_wiring/source_runtime/runtime_inventory_graph.py` | Graphe d'inventaire : noeuds + 175 arêtes (34 statiques + 141 dynamiques) | CRÉÉ |
| `runtime_wiring/source_runtime/capability_inventory_linker.py` | Linker P36→P37 : capability → fonctions/routes/tests/docs réels | CRÉÉ |
| `runtime_wiring/source_runtime/capability_path_router.py` | Ajout champs P37 avec défauts dans chaque path | MODIFIÉ |
| `runtime_wiring/source_runtime/brody_source_context_bridge.py` | Inventaire + linker branchés dans le bridge | MODIFIÉ |
| `apps/obsidia_api/routes/source_runtime_status.py` | Preview expose tous les champs P37 | MODIFIÉ |
| `tests/test_runtime_inventory_graph_p37.py` | 15 tests unitaires | CRÉÉ |
| `tests/api/test_runtime_inventory_preview_p37.py` | 9 tests API | CRÉÉ |

---

## Statistiques de l'inventaire (2026-06-04)

| Catégorie | Nombre |
|---|---|
| Modules Python scannés | **116** |
| Fonctions | **529** |
| Classes | **132** |
| Routes API | **145** |
| Adapters (*_to_context_packet) | **10** |
| Fichiers test | **130** |
| Fichiers docs | **19** |
| Arêtes total (graph) | **175** |
| — Arêtes statiques (architecturales) | 34 |
| — Arêtes dynamiques (découvertes AST) | 141 |

---

## Architecture du graphe

### Types de noeuds
- `module` — fichier `.py`
- `function` — fonction définie dans un module
- `class` — classe définie dans un module
- `route` — endpoint FastAPI (`GET`/`POST`/etc.)
- `adapter` — fonction `*_to_context_packet` (heuristique nom)
- `test` — fichier `test_*.py`
- `doc` — fichier `.md` dans `docs/`

### Types d'arêtes
| Type | Signification |
|---|---|
| `USES` | capability utilise un module/fonction |
| `READS` | adapter lit un source pack |
| `EXPOSES` | route expose une fonction |
| `CALLS` | route appelle une fonction |
| `IMPORTS` | module importe un autre module |
| `TESTS` | fichier test couvre un module |
| `DOCUMENTS` | fichier doc documente un module |
| `GUARDS` | capability bloque une autre |
| `DEFINED_IN` | adapter défini dans un module |

---

## Exemples de chemins complets (capability → inventaire)

### Query : "IR alphabet reverse OS interlanguage"

```
Capability chain:   [IR_ALPHABET_MAPPING, REVERSE_OS_INTERLANGUAGE]
selected_functions: [classify_entry_layer, build_reverse_os_interlanguage_index,
                     route_capability_path, build_brody_context_from_source_packs, ...]
selected_adapters:  [reverse_os_interlanguage_to_context_packet]
selected_routes:    [/api/runtime-wiring/source-runtime/preview]
selected_tests:     [tests/test_capability_path_router_p36.py,
                     tests/api/test_capability_path_preview_p36.py,
                     tests/test_reverse_os_interlanguage_runtime_extension_p35.py, ...]
selected_docs:      [docs/real_engine/P35_REVERSE_OS_INTERLANGUAGE_RUNTIME_EXTENSION_REPORT.md,
                     docs/real_engine/P36_GLOBAL_CAPABILITY_PATH_ROUTER_REPORT.md]
coverage_status:    FULLY_COVERED
inventory_linked:   True
```

### Query : "34 arbres agents"

```
Capability chain:   [AGENT_TREE_LOOKUP]
selected_functions: [build_os_trad_deep_concept_index, classify_entry_layer, ...]
selected_adapters:  [os_trad_reverse_to_context_packet]
selected_routes:    [/api/runtime-wiring/source-runtime/preview]
selected_tests:     [tests/test_capability_path_router_p36.py]
coverage_status:    FULLY_COVERED
```

### Query : "envoie un mail"

```
Capability chain:   [ACTION_REQUEST_BLOCKED]
selected_functions: []   (aucune exécution possible)
selected_routes:    []
x108_decision:      BLOCK_OR_HOLD_CONTEXT_ONLY
inventory_linked:   True
coverage_status:    NO_IMPLEMENTATION_FOUND
```

---

## Preuve No ACT

- `runtime_allowed_now = False` dans tous les graphes et arêtes
- `emits_act = False` dans le graphe et tous les chemins
- `readonly = True` dans le graphe
- `decision_authority = KX108_ONLY` dans le graphe et la réponse API
- Scanner AST : `ast.parse()` uniquement — zéro exécution, zéro import dynamique
- Pas de `subprocess`, pas de `eval`, pas d'`__import__`

---

## Résultats de validation

| Étape | Résultat |
|---|---|
| `python -m compileall` nouveaux fichiers | OK — aucune erreur syntaxe |
| `pytest tests/test_runtime_inventory_graph_p37.py` | 15/15 PASS |
| `pytest tests/api/test_runtime_inventory_preview_p37.py` | 9/9 PASS |
| `pytest tests/test_capability_path_router_p36.py` + api P36 | 23/23 PASS |
| `pytest tests/` (suite complète) | **3647/3647 PASS** |
| `check_forbidden_content.py` | FORBIDDEN_CONTENT_PASS |
| `generate_recursive_manifest.py` | 7725 fichiers — hash OK |
| `verify_recursive_manifest.py` | MANIFEST_VERIFIED — 7725 fichiers match |

---

## Limites restantes

- Le scanner AST ne résout pas les imports indirects (alias, re-exports) — il découvre uniquement les définitions directes.
- Les routes avec préfixe dynamique (variable) ne sont pas résolues — les préfixes connus sont hardcodés dans `_KNOWN_PREFIXES`.
- La résolution des tests → modules est heuristique (nom de fichier) — pas de parsing AST des imports de test.
- Workbench display (affichage des fonctions/routes/tests dans le frontend) : **WORKBENCH_RUNTIME_INVENTORY_DISPLAY_DEFERRED_TO_P38**.

---

## Prochain palier P38

P38 devra brancher l'affichage workbench de l'inventaire runtime :

- Afficher `selected_functions` / `selected_routes` / `selected_tests` dans l'UI
- Permettre la navigation par module dans le workbench
- Éventuellement : graphe interactif des arêtes capability→module→route→test
- Résolution des imports indirects (optionnel)

---

**Verdict final : P37_RUNTIME_FUNCTION_INVENTORY_GRAPH_READY**
