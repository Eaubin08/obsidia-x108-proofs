# P44 — Critical Capability Binding Report

**Date:** 2026-06-04
**Branch:** p43-unconnected-runtime-surface-audit
**Status:** P44_CRITICAL_CAPABILITY_BINDING_READY
**Basé sur:** P43 — Unconnected Runtime Surface Audit

---

## Objectif

Brancher les 5 gaps MUST_BIND_NEXT identifiés en P43 dans le capability router P36/P37,
sans ouvrir l'action réelle, sans muter le kernel.

---

## Les 5 Gaps P43 et leur résolution

### Gap 1 — ATLAS (11 263 entrées)

**Avant P44:** `atlas_to_context_packet` existait dans `source_adapters.py`, la famille ATLAS
contenait 11 263 entrées, mais aucune capability ne pointait vers eux.

**Après P44:** Capability `ATLAS_CONTEXT_LOOKUP` déclarée.
- Intent keywords : `atlas`, `cartographie`, `corpus map`, `component map`, `atlas obsidia`
- Adapter : `atlas_to_context_packet`
- Source family : `ATLAS`
- Route template : `/api/runtime-wiring/source-runtime/preview`
- Preuve : query "atlas component map" → `ATLAS_CONTEXT_LOOKUP` sélectionné ✓

### Gap 2 — EXTERNAL_SIGNALS / TimeVerse (82 entrées)

**Avant P44:** `external_signals_to_context_packet` orphelin, famille `EXTERNAL_SIGNALS` non routée.

**Après P44:** Capability `EXTERNAL_SIGNALS_CONTEXT` déclarée.
- Intent keywords : `timeverse`, `external signals`, `signal temporel`, `c459`
- Adapter : `external_signals_to_context_packet`
- Source family : `EXTERNAL_SIGNALS`
- Preuve : query "timeverse temporal signal" → `EXTERNAL_SIGNALS_CONTEXT` ✓

### Gap 3 — `/api/brody/chat` (entrypoint primaire)

**Avant P44:** La route principale Brody `/api/brody/chat` n'apparaissait dans aucun template capability.
Le routeur ignorait le chemin d'entrée primaire.

**Après P44:** Capability `BRODY_CHAT_ENTRYPOINT` déclarée.
- Intent keywords : `brody chat`, `true voice`, `final answer`, `brody réponse`
- Route : `/api/brody/chat`
- Modules : `brody_source_context_bridge`, `brody_real_response_pipeline`
- Preuve : query "brody chat true voice" → `BRODY_CHAT_ENTRYPOINT`, `/api/brody/chat` ✓

### Gap 4 — `graphiti_v20_readonly_client` (module orphelin)

**Avant P44:** La capability `GRAPHITI_READONLY_CONTEXT` existait mais ne référençait pas
`graphiti_v20_readonly_client`. Le client graphiti était invisible au router.

**Après P44:**
- `graphiti_v20_readonly_client` ajouté à `candidate_modules` dans la taxonomie
- `graphiti_v20_readonly_client` ajouté aux `modules` du template de chemin
- Nouvel intent `GRAPHITI_READONLY` avec keywords spécifiques (`graphiti readonly`, `graphiti v20`, `graphiti client`)
- Score GRAPHITI_READONLY_CONTEXT boosted 0.73 → 0.76 (dépasse MEMORY_REINTEGRATION_CONTEXT)
- Preuve : query "graphiti v20 readonly client" → `GRAPHITI_READONLY_CONTEXT` + `graphiti_v20_readonly_client` ✓

### Gap 5 — `/api/runtime-wiring/os-trad/*` (3 routes)

**Avant P44:** Trois routes IR/OS-Trad opérationnelles (`os-trad/translate`, `ir/candidate`, `os-reverse/project`)
n'étaient dans aucun template capability.

**Après P44:** Capability `OS_TRAD_ROUTE_CONTEXT` déclarée.
- Intent keywords : `os-trad route`, `ir candidate`, `translate endpoint`, `os reverse project`
- Routes : 3 routes `/api/runtime-wiring/os-trad/api/*`
- Adapters : `os_trad_reverse_to_context_packet`, `reverse_os_interlanguage_to_context_packet`
- Preuve : query "os-trad route translate endpoint" → `OS_TRAD_ROUTE_CONTEXT` ✓

---

## Coverage avant/après P44

| Métrique | Avant P44 (P43) | Après P44 | Delta |
|---|---|---|---|
| Capabilities déclarées | 15 | 20 | +5 |
| Templates router | 14 | 18 | +4 |
| Familles source connectées | 6/8 | **8/8** | +2 ✓ |
| Adapters connectés | 7/10 | 9/10 | +2 |
| Routes dans templates | 1 | 4 | +3 |
| graphiti_v20_readonly_client branché | Non | **Oui** | ✓ |

**Toutes les 8 familles source sont désormais connectées au capability router.**

---

## Fichiers modifiés

### `runtime_wiring/source_runtime/capability_taxonomy.py`
- Ajout de `ATLAS_CONTEXT_LOOKUP`, `EXTERNAL_SIGNALS_CONTEXT`, `BRODY_CHAT_ENTRYPOINT`, `OS_TRAD_ROUTE_CONTEXT`
- Mise à jour de `GRAPHITI_READONLY_CONTEXT` : ajout de `graphiti_v20_readonly_client` dans `candidate_modules`

### `runtime_wiring/source_runtime/capability_path_router.py`
- Ajout des intents `ATLAS`, `EXTERNAL_SIGNALS`, `BRODY_CHAT`, `OS_TRAD_ROUTE`, `GRAPHITI_READONLY`
- Mapping `_INTENT_TO_CAPABILITIES` étendu (+5 entrées)
- Scores ajoutés : `OS_TRAD_ROUTE_CONTEXT` (0.84), `BRODY_CHAT_ENTRYPOINT` (0.78), `ATLAS_CONTEXT_LOOKUP` (0.71), `EXTERNAL_SIGNALS_CONTEXT` (0.67)
- GRAPHITI_READONLY_CONTEXT score : 0.73 → 0.76
- Templates ajoutés pour les 4 nouvelles capabilities
- GRAPHITI_READONLY_CONTEXT template : `graphiti_v20_readonly_client` ajouté aux modules

### `runtime_wiring/source_runtime/capability_inventory_linker.py`
- `_CAPABILITY_MODULE_STEMS` étendu : +4 nouvelles capabilities
- `_CAPABILITY_ROUTE_FRAGMENTS` étendu : +4 nouvelles capabilities, GRAPHITI_READONLY_CONTEXT mis à jour
- `_CAPABILITY_TEST_STEMS` étendu : référence aux tests P44
- `_CAPABILITY_DOC_STEMS` étendu : référence aux rapports P43/P44

---

## Tests P44

### `tests/test_critical_capability_binding_p44.py` (13 tests)
1. ATLAS_CONTEXT_LOOKUP dans la taxonomie
2. EXTERNAL_SIGNALS_CONTEXT dans la taxonomie
3. BRODY_CHAT_ENTRYPOINT dans la taxonomie
4. GRAPHITI_READONLY_CONTEXT lié à graphiti_v20_readonly_client
5. OS_TRAD_ROUTE_CONTEXT dans la taxonomie
6. Query atlas → ATLAS_CONTEXT_LOOKUP + atlas_to_context_packet
7. Query timeverse → EXTERNAL_SIGNALS_CONTEXT
8. Query brody → BRODY_CHAT_ENTRYPOINT + /api/brody/chat
9. Query graphiti → GRAPHITI_READONLY_CONTEXT
10. Query os-trad → OS_TRAD_ROUTE_CONTEXT
11. Aucun runtime_allowed_now=True
12. Aucun emits_act=True
13. decision_authority=KX108_ONLY partout

### `tests/api/test_critical_capability_os_map_p44.py` (7 tests)
Tests API via `/api/runtime-wiring/os-map/query`

---

## Résultats de validation

```
python -m pytest tests/test_critical_capability_binding_p44.py tests/api/test_critical_capability_os_map_p44.py -q
→ 20 passed

python -m pytest tests/test_capability_path_router_p36.py tests/api/test_capability_path_preview_p36.py
  tests/test_runtime_inventory_graph_p37.py tests/api/test_runtime_inventory_preview_p37.py
  tests/test_os_map_workbench_p38.py tests/api/test_os_map_api_p38.py
  tests/test_unconnected_runtime_surface_audit_p43.py -q
→ 74 passed

python -m pytest tests/ -q
→ 3700 passed, 4 skipped

python scripts/check_forbidden_content.py → FORBIDDEN_CONTENT_PASS
```

---

## Limites restantes

- `route_entry_to_context_packet` : adapter interne (`registry_to_adapter_dry_run.py`), non destiné aux capabilities
- 80 modules `brody_*` restent non connectés au capability router — nécessitent analyse individuelle
- 141 routes API non dans les templates (X108, OS3, memory, periphery) → palier P45
- La route `/api/brody/chat` est surfacée dans BRODY_CHAT_ENTRYPOINT mais le pipeline complet
  (brody_v1_4_12a_final_answer_adapter → source context → réponse) n'est pas encore câblé end-to-end

---

## Prochain palier P45

Suggestions prioritaires :
1. Capability `BRODY_FINAL_ANSWER` → `brody_v1_4_12a_final_answer_adapter`
2. Capability `SEMANTIC_ROUTING` → `brody_semantic_query_router`
3. Capabilities X108 (`X108_COGNITIVE`, `X108_MATH`, `X108_MEMORY`)
4. Capability `OS3_AUDIT` pour les 7 routes OS3
5. Capability `MEMORY_CANDIDATE` pour les 6 routes memory

---

*P44 — lecture seule, aucun ACT, aucune mutation kernel, aucune écriture graphiti/mémoire.*
