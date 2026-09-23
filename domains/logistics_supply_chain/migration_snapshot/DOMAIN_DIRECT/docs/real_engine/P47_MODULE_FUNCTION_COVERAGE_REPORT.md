# P47 — Module & Function Coverage Report

**Date:** 2026-06-04  
**Phase:** P47  
**Branch:** p43-unconnected-runtime-surface-audit  
**Builds on:** P45 (routes 100%), P46 (vues Workbench 100%)

---

## Verdict

**P47_MODULE_FUNCTION_COVERAGE_100_READY**

- Modules totaux scannés : **121**  
- Modules classifiés : **121**  
- Modules non classifiés : **0**  
- Couverture modules : **100%**

- Fonctions totales scannées : **548**  
- Fonctions classifiées : **548**  
- Fonctions non classifiées : **0**  
- Couverture fonctions : **100%**

---

## Classification Modules

| Catégorie | Modules | Fonctions |
|---|---|---|
| CONNECTED_CAPABILITY | 7 | 40 |
| CONNECTED_ROUTE_HANDLER | 12 | 113 |
| CONNECTED_ADAPTER | 33 | 175 |
| CONNECTED_RUNTIME | 9 | 42 |
| CONNECTED_STATUS_ONLY | 10 | 59 |
| CONNECTED_WORKBENCH_SUPPORT | 2 | 6 |
| BLOCKED_ACTION_RUNTIME | 7 | 23 |
| INTERNAL_HELPER | 39 | 87 |
| ARCHIVE_ONLY | 2 | 3 |
| DO_NOT_BIND_EXPLICIT | 0 | 0 |
| CONNECTED_TEST_ONLY | 0 | 0 |
| UNCLASSIFIED | **0** | **0** |
| **TOTAL** | **121** | **548** |

---

## Modules clés par catégorie

### CONNECTED_CAPABILITY (7 modules)
- `runtime_wiring/source_runtime/capability_path_router.py` — P36 router
- `runtime_wiring/source_runtime/capability_taxonomy.py` — taxonomie capabilities
- `runtime_wiring/source_runtime/capability_inventory_linker.py` — P44 linker
- `runtime_wiring/source_runtime/runtime_inventory_graph.py` — P37 graph
- `runtime_wiring/source_runtime/runtime_inventory_builder.py` — P37 builder
- `runtime_wiring/source_runtime/route_capability_map.py` — P45 route map
- `runtime_wiring/source_runtime/route_coverage_classifier.py` — P45 classifier

### CONNECTED_ROUTE_HANDLER (12 modules)
- `apps/obsidia_api/routes/os_map.py` — P38/P45/P46/P47 OS Map
- `apps/obsidia_api/routes/brody.py` — chat Brody
- `apps/obsidia_api/routes/audit.py` — audit events
- `apps/obsidia_api/routes/memory.py` — memory candidates
- `apps/obsidia_api/routes/context.py` — context packets
- `apps/obsidia_api/routes/translation.py` — OS Trad
- `apps/obsidia_api/routes/os_trad_ir_reverse.py` — IR/Reverse
- `apps/obsidia_api/routes/runtime_wiring_preview.py` — preview
- `apps/obsidia_api/routes/periphery_ops.py` — periphery
- `apps/obsidia_api/routes/bus.py` — bus
- `apps/obsidia_api/routes/graphiti.py` — graphiti readonly
- `apps/obsidia_api/main.py` — FastAPI app

### CONNECTED_ADAPTER (33 modules)
- `runtime_wiring/source_runtime/brody_source_context_bridge.py`
- `runtime_wiring/source_runtime/source_context_hydrator.py`
- `runtime_wiring/source_runtime/source_hydration_planner.py`
- `runtime_wiring/source_runtime/source_family_selector.py`
- `runtime_wiring/source_runtime/source_pack_resolver.py`
- `runtime_wiring/source_runtime/source_runtime_cache.py`
- `runtime_wiring/source_runtime/readonly_content_loader.py`
- `apps/obsidia_api/graphiti_v20_readonly_client.py`
- Tous les `brody_*_adapter.py`, `brody_*_bridge.py`
- `runtime_wiring/source_registry/registry_loader.py`
- `runtime_wiring/engine_bridge/readonly_engine_bridge.py`
- etc.

### CONNECTED_RUNTIME (9 modules)
- `runtime_wiring/dry_run_packet_router.py`
- `runtime_wiring/source_runtime/source_runtime_query.py`
- `runtime_wiring/source_runtime/os_trad_reverse_index.py`
- `runtime_wiring/source_runtime/reverse_os_interlanguage_index.py`
- `apps/obsidia_api/audit_middleware.py`
- `apps/obsidia_api/brody_full_runtime_orchestrator.py`
- `apps/obsidia_api/brody_full_runtime_reconnect.py`
- `apps/obsidia_api/brody_real_response_pipeline.py`
- + 1 autre

### CONNECTED_WORKBENCH_SUPPORT (2 modules — P46)
- `runtime_wiring/source_runtime/workbench_view_capability_map.py`
- `runtime_wiring/source_runtime/workbench_view_coverage_classifier.py`

### BLOCKED_ACTION_RUNTIME (7 modules)
- `apps/obsidia_api/routes/blockchain.py` — blockchain BLOCKED
- `apps/obsidia_api/routes/gencoin.py` — gencoin LEDGER_ONLY
- `apps/obsidia_api/routes/worldcalls.py` — worldcall DRY_RUN_ONLY
- `apps/obsidia_api/brody_gencoin_cognitive_ledger.py`
- `apps/obsidia_api/brody_gencoin_shadow_value.py`
- `apps/obsidia_api/brody_gencoin_transverse_interface.py`
- `apps/obsidia_api/brody_memory_promotion_guard.py`

### ARCHIVE_ONLY (2 modules)
- `runtime_wiring/p8b_demo.py`
- `runtime_wiring/source_registry/p9c_integration_demo.py`

### INTERNAL_HELPER (39 modules)
- Tous les `__init__.py` (6)
- `apps/obsidia_api/contracts.py` (26 classes Pydantic)
- `apps/obsidia_api/safe_response.py`
- `apps/obsidia_api/output_envelope.py`
- Modules brody signaux / diagnostics internes
- `runtime_wiring/packet_types.py`, `x108_admission_stub.py`, etc.

---

## Fonctions clés classifiées

| Fonction | Catégorie |
|---|---|
| `capability_path_router.py::route_capability_path` | CONNECTED_CAPABILITY |
| `capability_taxonomy.py::list_capability_ids` | CONNECTED_CAPABILITY |
| `runtime_inventory_graph.py::build_runtime_inventory_graph` | CONNECTED_CAPABILITY |
| `capability_inventory_linker.py::link_capabilities_to_inventory` | CONNECTED_CAPABILITY |
| `route_capability_map.py::build_route_capability_map` | CONNECTED_CAPABILITY |
| `os_map.py::os_map_query` | CONNECTED_ROUTE_HANDLER |
| `os_map.py::os_map_status` | CONNECTED_ROUTE_HANDLER |
| `brody.py::brody_chat` | CONNECTED_ROUTE_HANDLER |
| `workbench_view_capability_map.py::build_workbench_coverage_summary` | CONNECTED_WORKBENCH_SUPPORT |
| `workbench_view_coverage_classifier.py::classify_workbench_view` | CONNECTED_WORKBENCH_SUPPORT |
| `source_hydration_planner.py::build_hydration_plan_from_path` | CONNECTED_ADAPTER |
| `dry_run_packet_router.py` (toutes fonctions) | CONNECTED_RUNTIME |

---

## Preuves NO ACT

| Invariant | Valeur |
|---|---|
| runtime_allowed_now | false (tous modules/fonctions) |
| emits_act | false (tous modules/fonctions) |
| decision_authority | KX108_ONLY |
| memory_write | false |
| graph_write | false |
| kernel_mutation | false |
| zip_extraction | false |
| world_action | false |

---

## Note sur les risk_flags

Certains modules ont des `risk_flags` détectés par l'analyse statique :
- `runtime_inventory_builder.py`: SUBPROCESS_RISK, EVAL_RISK, DYNAMIC_IMPORT_RISK, SHELL_RISK — ces flags correspondent à du code qui **analyse** d'autres fichiers, pas à des actions réelles. Classification : CONNECTED_CAPABILITY.
- `build_source_file_registry.py`: RUNTIME_ALLOWED_NOW_TRUE, EMITS_ACT_TRUE — faux positifs (le fichier contient ces chaînes dans des noms de variables/checks, pas comme actions réelles). Classification : CONNECTED_ADAPTER.
- Ces modules restent classifiés (non UNCLASSIFIED) et couverts à 100%.

---

## Fichiers produits

| Fichier | Rôle |
|---|---|
| `_runtime_wiring_preflight/P47_MODULE_FUNCTION_INVENTORY_RAW.json` | Inventaire brut 121 modules |
| `_runtime_wiring_preflight/P47_MODULE_FUNCTION_COVERAGE_MAP.json` | Carte couverture 100% |
| `runtime_wiring/source_runtime/module_function_coverage_classifier.py` | Classifieur P47 |
| `runtime_wiring/source_runtime/module_function_capability_map.py` | Map fonction → capability |
| `apps/obsidia_api/routes/os_map.py` | Enrichi avec champs P47 |
| `tests/test_module_function_coverage_p47.py` | Tests unitaires P47 |
| `tests/api/test_module_function_coverage_os_map_p47.py` | Tests API P47 |
| `docs/real_engine/P47_MODULE_FUNCTION_COVERAGE_REPORT.md` | Ce rapport |

---

## Limites restantes pour P48

- `CONNECTED_TEST_ONLY` = 0 : les 140 fichiers de test ne sont pas dans le graphe d'inventaire runtime (ils sont dans `tests/` hors scope P37). P48 pourrait enrichir le scan.
- 39 modules INTERNAL_HELPER : certains pourraient être affinés (ex. `brody_reflex_diagnostic_packet.py` est interne mais lié à Brody).
- `DO_NOT_BIND_EXPLICIT` = 0 : aucun module n'a été explicitement exclu du routing. P48 pourrait documenter les exclusions.
- Les risk_flags (SUBPROCESS_RISK, EVAL_RISK) sont des faux positifs d'analyse statique — P48 pourrait affiner le scanner.
