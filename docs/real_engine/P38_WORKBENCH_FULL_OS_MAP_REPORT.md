# P38 — Workbench Full OS Map — Rapport

**Date :** 2026-06-04  
**Branche :** p10-real-engine-controlled-bridge  
**Palier :** P38  
**Statut :** P38_WORKBENCH_FULL_OS_MAP_READY  

---

## Résumé

P38 branche le Workbench Obsidia sur la carte moteur complète construite par P36/P37.  
Un nouvel onglet **OS MAP** (sidebar) permet de soumettre une query et d'obtenir en retour :  
- les intents détectés et les capabilities requises (P36)  
- le chemin runtime sélectionné (modules, adapters, routes, families, subfamilies, evidence packs)  
- les fonctions, classes, tests et docs reliés par l'inventaire (P37)  
- le plan d'hydratation (max 8 fichiers, zéro exécutable)  
- la décision X108 et les invariants boundary (readonly, no ACT, KX108_ONLY)  

**Invariants permanents :** `runtime_allowed_now = False`, `emits_act = False`, `decision_authority = KX108_ONLY`, `readonly = True`.  

---

## Fichiers créés / modifiés

| Fichier | Rôle | Statut |
|---|---|---|
| `apps/obsidia_api/routes/os_map.py` | 2 endpoints : GET /status + POST /query (OS Map complet) | CRÉÉ |
| `apps/obsidia_api/main.py` | Enregistrement de os_map_router | MODIFIÉ |
| `apps/obsidia-workbench/src/views/OSMapView.tsx` | Vue workbench Full OS Map (React/TS) | CRÉÉ |
| `apps/obsidia-workbench/src/components/LeftSidebar.tsx` | Ajout `'os-map'` dans ViewId + sidebar | MODIFIÉ |
| `apps/obsidia-workbench/src/App.tsx` | Import + rendering de `<OSMapView />` | MODIFIÉ |
| `tests/test_os_map_workbench_p38.py` | 12 tests unitaires (statiques) | CRÉÉ |
| `tests/api/test_os_map_api_p38.py` | 8 tests API | CRÉÉ |

---

## Endpoints OS Map (P38)

### GET `/api/runtime-wiring/os-map/status`

Retourne les statistiques de l'inventaire et les capabilities disponibles.

```json
{
  "os_map_status": "READY",
  "capability_count": 16,
  "capability_ids": [...],
  "inventory_status": "READY",
  "inventory_module_count": 116,
  "inventory_function_count": 529,
  "inventory_route_count": 145,
  "inventory_adapter_count": 10,
  "inventory_test_count": 130,
  "inventory_doc_count": 19,
  "readonly": true,
  "emits_act": false,
  "decision_authority": "KX108_ONLY"
}
```

### POST `/api/runtime-wiring/os-map/query`

Retourne la carte moteur complète pour une query.

**Requête :**
```json
{ "query": "IR alphabet reverse OS interlanguage canon", "max_paths": 5 }
```

**Réponse (exemple IR) :**
```json
{
  "os_map_status": "OS_MAP_READY",
  "detected_intents": ["IR_ALPHABET", "REVERSE_OS_INTERLANGUAGE"],
  "required_capabilities": ["IR_ALPHABET_MAPPING", "REVERSE_OS_INTERLANGUAGE"],
  "selected_runtime_path": {
    "capability_chain": ["IR_ALPHABET_MAPPING"],
    "modules": ["reverse_os_interlanguage_index", "source_runtime_query"],
    "adapters": ["reverse_os_interlanguage_to_context_packet"],
    "source_subfamilies": ["REVERSE_OS_INTERLANGUAGE_CANON_V1"],
    "evidence_packs": ["REVERSE_OS_INTERLANGUAGE_CANON_V1"],
    "x108_decision": "ALLOW_CONTEXT_ONLY"
  },
  "selected_functions": ["classify_entry_layer", "build_reverse_os_interlanguage_index", ...],
  "selected_tests": ["tests/test_capability_path_router_p36.py", ...],
  "coverage_status": "FULLY_COVERED",
  "inventory_linked": true,
  "x108_decision": "ALLOW_CONTEXT_ONLY",
  "readonly": true,
  "emits_act": false,
  "decision_authority": "KX108_ONLY"
}
```

**Requête d'action bloquée :**
```json
{ "query": "envoie un mail à l'équipe" }
```
```json
{
  "os_map_status": "ACTION_BLOCKED",
  "action_blocked": true,
  "x108_decision": "BLOCK_OR_HOLD_CONTEXT_ONLY",
  "selected_runtime_path": {
    "capability_chain": ["ACTION_REQUEST_BLOCKED"]
  }
}
```

---

## Workbench OS Map — Sections affichées

| Section | Contenu affiché |
|---|---|
| **Query Panel** | Input + bouton "Show OS Map" + exemples cliquables |
| **ACTION_BLOCKED banner** | Bannière rouge si requête d'action détectée |
| **P36 — Intent & Capability Router** | `detected_intents` + `required_capabilities` en chips colorées |
| **Selected Runtime Path** | Card P36 : capability_chain, modules, adapters, subfamilies, evidence_packs, score, reason, x108_decision |
| **P37 — Runtime Inventory** | `selected_functions`, `selected_classes`, `selected_routes_inventory`, `selected_tests`, `selected_docs`, `coverage_status` |
| **Hydration Plan** | `planned_files_count`, `max_files`, `estimated_bytes`, `source_file_refs` |
| **X108 Boundary** | `x108_decision`, `decision_authority`, `runtime_allowed_now`, `emits_act`, `readonly`, safety flags |
| **OS Map status** | Badge vert/rouge `os_map_status` |

---

## Invariants affichés dans la vue

```
No ACT · No write · No runtime_allowed_now · No Graphiti write · KX108_ONLY
```

Affiché dans une barre jaune permanente en haut de la vue.

---

## Résultats de validation

| Étape | Résultat |
|---|---|
| `python -m compileall` os_map.py + main.py | OK |
| `pytest tests/test_os_map_workbench_p38.py` | 12/12 PASS |
| `pytest tests/api/test_os_map_api_p38.py` | 8/8 PASS |
| `pytest tests/test_capability_path_router_p36.py` + P36 API | 23/23 PASS |
| `pytest tests/test_runtime_inventory_graph_p37.py` + P37 API | 24/24 PASS |
| `pytest tests/` (suite complète) | **3667/3667 PASS** |
| `check_forbidden_content.py` | FORBIDDEN_CONTENT_PASS |
| `generate_recursive_manifest.py` | 7728 fichiers — hash OK |
| `verify_recursive_manifest.py` | MANIFEST_VERIFIED — 7728 fichiers match |

---

## Limites restantes

- La vue TSX n'est pas testée dans un navigateur réel (pas de build step dans les tests) — seule la structure statique est vérifiée.
- Les exemples de requêtes cliquables dans la vue préremplissent l'input mais ne soumettent pas automatiquement (UX volontaire).
- Affichage des `ranked_runtime_paths` (chemins alternatifs) : simplifié — seul le `selected_path` est affiché en détail.

---

**Verdict final : P38_WORKBENCH_FULL_OS_MAP_READY**
