# P36 — Global Capability Path Router — Rapport

**Date :** 2026-06-04  
**Branche :** p10-real-engine-controlled-bridge  
**Palier :** P36  
**Statut :** P36_GLOBAL_CAPABILITY_PATH_ROUTER_READY  

---

## Résumé

P36 construit le routeur global de capacités du moteur Obsidia X-108.  
Chaque requête utilisateur est classée en intents → capabilities → chemins runtime candidats.  
Le meilleur chemin est sélectionné, un plan d'hydratation est construit, et le tout est injecté dans le payload Brody via le bridge.  

**Invariants permanents :**  
- `runtime_allowed_now = False` dans tous les chemins  
- `emits_act = False` dans tous les chemins  
- `decision_authority = KX108_ONLY` dans tous les chemins  
- `readonly = True` / `no_act = True` dans toutes les réponses  

---

## Fichiers créés / modifiés

| Fichier | Rôle | Statut |
|---|---|---|
| `runtime_wiring/source_runtime/capability_taxonomy.py` | 16 capability classes avec métadonnées complètes | CRÉÉ |
| `runtime_wiring/source_runtime/capability_path_router.py` | Routeur : query → intents → capabilities → chemins ranked | CRÉÉ |
| `runtime_wiring/source_runtime/source_hydration_planner.py` | Planner : selected_path → plan d'hydratation (max 8 fichiers) | CRÉÉ |
| `runtime_wiring/source_runtime/brody_source_context_bridge.py` | Bridge étendu avec router + planner branchés | MODIFIÉ |
| `apps/obsidia_api/routes/source_runtime_status.py` | Route preview étendue avec tous les champs P36 | MODIFIÉ |
| `tests/test_capability_path_router_p36.py` | 15 tests unitaires | CRÉÉ |
| `tests/api/test_capability_path_preview_p36.py` | 8 tests API | CRÉÉ |

---

## Taxonomie des capabilities (16 classes)

| capability_id | Description courte |
|---|---|
| `ANSWER_ONLY` | Réponse interne Brody sans source pack |
| `SOURCE_CONTEXT` | Contexte source générique |
| `PROVENANCE_TRACE` | Trace de provenance narrative |
| `OS_TRAD_TRANSLATION` | Traduction OS Trad structurée |
| `REVERSE_OS_INTERLANGUAGE` | Canon interlanguage Reverse OS (P34/P35) |
| `IR_ALPHABET_MAPPING` | Mapping IR Alphabet L2 — 12 tokens |
| `AGENT_TREE_LOOKUP` | 34 arbres / 52 agents |
| `LAW_PROTOCOL_LOOKUP` | Lois et protocoles Obsidiens |
| `RSSI_SECURITY_CONTEXT` | Contexte sécurité RSSI |
| `NPL_NARRATIVE_PROVENANCE` | Narrative Provenance Layer |
| `MEMORY_REINTEGRATION_CONTEXT` | Réintégration mémoire Brody |
| `GRAPHITI_READONLY_CONTEXT` | Graphiti en lecture seule |
| `OS4_ENGINE_STATUS` | Statut moteur OS4 |
| `PROOF_AUDIT_CONTEXT` | Audit conformité / compliance |
| `WORKBENCH_PREVIEW` | Preview workbench sans exécution |
| `ACTION_REQUEST_BLOCKED` | Requête d'action bloquée — READONLY |

---

## Exemples de chemins sélectionnés

### 1. Query : "IR alphabet reverse OS"

```
detected_intents:    [IR_ALPHABET, REVERSE_OS_INTERLANGUAGE]
required_capabilities: [IR_ALPHABET_MAPPING, REVERSE_OS_INTERLANGUAGE]
selected_path:
  capability_chain:  [IR_ALPHABET_MAPPING]
  modules:           [reverse_os_interlanguage_index, source_runtime_query]
  adapters:          [reverse_os_interlanguage_to_context_packet]
  routes:            [/api/runtime-wiring/source-runtime/preview]
  source_families:   [OS_TRAD_REVERSE_OS]
  source_subfamilies: [REVERSE_OS_INTERLANGUAGE_CANON_V1]
  evidence_packs:    [REVERSE_OS_INTERLANGUAGE_CANON_V1]
  x108_decision:     ALLOW_CONTEXT_ONLY
  runtime_allowed_now: False
  emits_act:         False
```

### 2. Query : "34 arbres agents"

```
detected_intents:    [AGENT_TREE]
required_capabilities: [AGENT_TREE_LOOKUP, OS_TRAD_TRANSLATION]
selected_path:
  capability_chain:  [AGENT_TREE_LOOKUP]
  modules:           [os_trad_reverse_index, source_runtime_query]
  adapters:          [os_trad_reverse_to_context_packet]
  source_families:   [OS_TRAD_REVERSE_OS]
  x108_decision:     ALLOW_CONTEXT_ONLY
```

### 3. Query : "lois protocoles non décision"

```
detected_intents:    [LAW_PROTOCOL]
required_capabilities: [LAW_PROTOCOL_LOOKUP]
selected_path:
  capability_chain:  [LAW_PROTOCOL_LOOKUP]
  modules:           [os_trad_reverse_index, source_runtime_query]
  adapters:          [os_trad_reverse_to_context_packet]
  source_families:   [OS_TRAD_REVERSE_OS]
  reason:            Boundary advisory uniquement
```

### 4. Query : "RSSI sécurité audit conformité"

```
detected_intents:    [RSSI_SECURITY, COMPLIANCE_AUDIT]
required_capabilities: [RSSI_SECURITY_CONTEXT, PROOF_AUDIT_CONTEXT]
selected_path:
  capability_chain:  [RSSI_SECURITY_CONTEXT]
  adapters:          [rssi_security_to_context_packet, rssi_rgpd_to_context_packet]
  source_families:   [RSSI_SECURITY_PRESENTATION, RSSI_RGPD]
```

### 5. Query : "mémoire Brody Graphiti"

```
detected_intents:    [MEMORY_GRAPHITI]
required_capabilities: [MEMORY_REINTEGRATION_CONTEXT, GRAPHITI_READONLY_CONTEXT]
selected_path:
  capability_chain:  [MEMORY_REINTEGRATION_CONTEXT]
  adapters:          [cognitive_to_context_packet, npl_to_context_packet]
  source_families:   [COGNITIVE_REINTEGRATION, NARRATIVE_PROVENANCE_LAYER]
```

### 6. Query : "envoie un mail / lance action / modifie fichier"

```
detected_intents:    [ACTION_REQUEST]
required_capabilities: [ACTION_REQUEST_BLOCKED]
selected_path:
  capability_chain:  [ACTION_REQUEST_BLOCKED]
  modules:           []
  adapters:          []
  x108_decision:     BLOCK_OR_HOLD_CONTEXT_ONLY
  reason:            Action requested but runtime is READONLY
  runtime_allowed_now: False
  emits_act:         False
```

---

## Plan d'hydratation

Le `source_hydration_planner.py` reçoit le `selected_path` et construit un plan :

- Maximum **8 fichiers** sélectionnés
- Budget maximum **50 000 bytes**
- Extensions autorisées : `.md`, `.yaml`, `.yml`, `.json`, `.txt`, `.csv`
- Extensions interdites (jamais sélectionnées) : `.py`, `.pyc`, `.ps1`, `.bat`, `.sh`, `.exe`, `.dll`, `.so`, `.bin`, `.cmd`
- Priorité par type : manifest > index > registry > canon > spec > schema > evidence > proof

---

## Payload Brody Bridge (nouveaux champs P36)

```python
{
    "capability_path_router_available": True,
    "detected_intents": [...],
    "required_capabilities": [...],
    "ranked_runtime_paths": [...],
    "selected_runtime_path": {...},
    "selected_modules": [...],
    "selected_adapters": [...],
    "selected_routes": [...],
    "selected_source_families": [...],
    "selected_source_subfamilies": [...],
    "selected_evidence_packs": [...],
    "hydration_plan": {...},
    "source_file_refs": [...],
    "x108_decision_path": "ALLOW_CONTEXT_ONLY",
    "runtime_allowed_now": False,
    "emits_act": False,
    "decision_authority": "KX108_ONLY",
    "no_act": True,
}
```

---

## Résultats de validation

| Étape | Résultat |
|---|---|
| `python -m compileall` nouveaux fichiers | OK — aucune erreur syntaxe |
| `pytest tests/test_capability_path_router_p36.py` | 15/15 PASS |
| `pytest tests/api/test_capability_path_preview_p36.py` | 8/8 PASS |
| `pytest tests/test_reverse_os_interlanguage_runtime_extension_p35.py` | 14/14 PASS |
| `pytest tests/api/test_reverse_os_interlanguage_preview_p35.py` | 19/19 PASS |
| `pytest tests/` (suite complète) | **3623/3623 PASS** |
| `check_forbidden_content.py` | FORBIDDEN_CONTENT_PASS |
| `generate_recursive_manifest.py` | 7719 fichiers — hash OK |
| `verify_recursive_manifest.py` | MANIFEST_VERIFIED — 7719 fichiers match |

---

## Limites restantes

- Le routeur classe par mots-clés — pas de LLM embedding ou de scoring sémantique avancé.
- Les `selected_files` dans les chemins sont symboliques (famille/subfamily) — l'hydratation réelle de fichiers depuis les ZIP reste dans `source_runtime_query.py` (P26+).
- Les familles non disponibles localement sont pénalisées en score mais pas bloquées — le planner reste conservateur.
- Workbench display P36 (affichage des chemins dans le frontend) : **WORKBENCH_CAPABILITY_PATH_DISPLAY_DEFERRED_TO_P37**.

---

## Prochain palier P37

P37 devra brancher l'affichage workbench des capability paths sélectionnés :

- Afficher `selected_runtime_path` / `modules` / `adapters` / `routes` / `evidence_packs`
- Afficher le label `no ACT / readonly` dans l'UI
- Permettre la navigation entre `ranked_runtime_paths` dans le workbench
- Éventuellement : scoring sémantique par embedding pour affiner les intents

---

**Verdict final : P36_GLOBAL_CAPABILITY_PATH_ROUTER_READY**
