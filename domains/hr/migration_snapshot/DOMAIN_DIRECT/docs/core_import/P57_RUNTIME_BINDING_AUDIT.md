# P57 — RUNTIME BINDING AUDIT

**Date :** 2026-06-06
**Branche :** p57-core-machinery-runtime-binding-audit

## Légende de classification
- `ACTIVE_RUNTIME` — route active, peut émettre ou recevoir des données réelles
- `READONLY_RUNTIME` — route lecture seule, pas d'écriture ni d'émission
- `DRY_RUN_ONLY` — route en mode dry-run, simulation uniquement
- `AUDIT_ONLY` — outil d'audit, pas de runtime

## Routes apps/obsidia_api/routes/

| Route | Lignes | Binding | Sigma | runtime_wiring | periphery | Flags effectifs |
|---|---|---|---|---|---|---|
| `audit` | 54 | `READONLY_RUNTIME` | — | — | — | none |
| `blockchain` | 669 | `DRY_RUN_ONLY` | ✓ | — | ✓ | none |
| `brody` | 739 | `DRY_RUN_ONLY` | — | ✓ | — | none |
| `brody_monitoring` | 405 | `READONLY_RUNTIME` | ✓ | — | ✓ | none |
| `bus` | 51 | `ACTIVE_RUNTIME` | — | — | — | none |
| `context` | 30 | `ACTIVE_RUNTIME` | — | — | — | none |
| `gencoin` | 53 | `READONLY_RUNTIME` | — | — | — | none |
| `graphiti` | 279 | `READONLY_RUNTIME` | — | — | — | none |
| `memory` | 135 | `DRY_RUN_ONLY` | — | — | — | none |
| `os3` | 59 | `READONLY_RUNTIME` | — | — | — | none |
| `os_map` | 726 | `DRY_RUN_ONLY` | — | ✓ | — | none |
| `os_trad_ir_reverse` | 397 | `READONLY_RUNTIME` | — | — | ✓ | none |
| `periphery_ops` | 1637 | `DRY_RUN_ONLY` | ✓ | — | ✓ | none |
| `runtime_freeze` | 305 | `READONLY_RUNTIME` | — | — | — | none |
| `runtime_wiring_preview` | 111 | `DRY_RUN_ONLY` | — | ✓ | — | none |
| `sigma_monitoring` | 122 | `READONLY_RUNTIME` | ✓ | — | — | none |
| `source_runtime_status` | 170 | `READONLY_RUNTIME` | — | ✓ | — | none |
| `status` | 63 | `READONLY_RUNTIME` | — | — | — | none |
| `translation` | 38 | `ACTIVE_RUNTIME` | — | — | — | none |
| `worldcalls` | 94 | `DRY_RUN_ONLY` | — | — | — | none |
| `x108` | 464 | `ACTIVE_RUNTIME` | — | — | ✓ | none |

## Résumé routes

| Type | Nombre |
|---|---|
| `ACTIVE_RUNTIME` | 4 |
| `DRY_RUN_ONLY` | 7 |
| `READONLY_RUNTIME` | 10 |

## Note sur les flags d'écriture dans les routes

Toutes les occurrences de `memory_write: False`, `graphiti_write: False`, `real_action: False` dans les routes sont des **champs de statut dans les réponses JSON** — pas des opérations d'écriture réelles.

Seule exception : `x108.py::x108_memory_candidates_append` — écrit dans le ledger mémoire local (JSONL).
Classification : `ACTIVE_RUNTIME` intentionnel — contrôlé par X108 governance.

## runtime_wiring/ bindings

| Fichier | Binding | Lignes |
|---|---|---|
| `runtime_wiring\contracts_loader.py` | `DRY_RUN_ONLY` | 87 |
| `runtime_wiring\dry_run_packet_router.py` | `DRY_RUN_ONLY` | 99 |
| `runtime_wiring\engine_bridge\api_adapter_preview.py` | `DRY_RUN_ONLY` | 134 |
| `runtime_wiring\engine_bridge\bridge_types.py` | `READONLY_RUNTIME` | 215 |
| `runtime_wiring\engine_bridge\readonly_engine_bridge.py` | `DRY_RUN_ONLY` | 284 |
| `runtime_wiring\os3_evidence_stub.py` | `DRY_RUN_ONLY` | 55 |
| `runtime_wiring\p8b_demo.py` | `DRY_RUN_ONLY` | 164 |
| `runtime_wiring\packet_types.py` | `DRY_RUN_ONLY` | 175 |
| `runtime_wiring\source_adapters.py` | `DRY_RUN_ONLY` | 381 |
| `runtime_wiring\source_registry\adapter_target_map.py` | `READONLY_RUNTIME` | 160 |
| `runtime_wiring\source_registry\build_source_file_registry.py` | `AUDIT_ONLY` | 321 |
| `runtime_wiring\source_registry\p9c_integration_demo.py` | `DRY_RUN_ONLY` | 260 |
| `runtime_wiring\source_registry\registry_loader.py` | `AUDIT_ONLY` | 145 |
| `runtime_wiring\source_registry\registry_to_adapter_dry_run.py` | `DRY_RUN_ONLY` | 256 |
| `runtime_wiring\source_registry\registry_types.py` | `AUDIT_ONLY` | 144 |
| `runtime_wiring\source_runtime\action_gateway_hold_block_sandbox.py` | `DRY_RUN_ONLY` | 211 |
| `runtime_wiring\source_runtime\adapter_capability_map.py` | `DRY_RUN_ONLY` | 203 |
| `runtime_wiring\source_runtime\adapter_coverage_classifier.py` | `READONLY_RUNTIME` | 120 |
| `runtime_wiring\source_runtime\brody_readonly_activation.py` | `READONLY_RUNTIME` | 145 |
| `runtime_wiring\source_runtime\brody_source_context_bridge.py` | `DRY_RUN_ONLY` | 243 |
| `runtime_wiring\source_runtime\capability_inventory_linker.py` | `AUDIT_ONLY` | 436 |
| `runtime_wiring\source_runtime\capability_path_router.py` | `READONLY_RUNTIME` | 505 |
| `runtime_wiring\source_runtime\capability_taxonomy.py` | `READONLY_RUNTIME` | 467 |
| `runtime_wiring\source_runtime\controlled_activation_matrix.py` | `DRY_RUN_ONLY` | 471 |
| `runtime_wiring\source_runtime\global_runtime_surface_gate.py` | `READONLY_RUNTIME` | 251 |
| `runtime_wiring\source_runtime\graphiti_memory_readonly_activation.py` | `READONLY_RUNTIME` | 205 |
| `runtime_wiring\source_runtime\module_function_capability_map.py` | `DRY_RUN_ONLY` | 264 |
| `runtime_wiring\source_runtime\module_function_coverage_classifier.py` | `DRY_RUN_ONLY` | 194 |
| `runtime_wiring\source_runtime\os_trad_reverse_index.py` | `READONLY_RUNTIME` | 368 |
| `runtime_wiring\source_runtime\readonly_content_loader.py` | `READONLY_RUNTIME` | 157 |
| `runtime_wiring\source_runtime\reverse_os_interlanguage_index.py` | `READONLY_RUNTIME` | 316 |
| `runtime_wiring\source_runtime\route_capability_map.py` | `READONLY_RUNTIME` | 123 |
| `runtime_wiring\source_runtime\route_coverage_classifier.py` | `READONLY_RUNTIME` | 351 |
| `runtime_wiring\source_runtime\runtime_inventory_builder.py` | `AUDIT_ONLY` | 417 |
| `runtime_wiring\source_runtime\runtime_inventory_graph.py` | `AUDIT_ONLY` | 183 |
| `runtime_wiring\source_runtime\source_context_hydrator.py` | `DRY_RUN_ONLY` | 96 |
| `runtime_wiring\source_runtime\source_family_selector.py` | `READONLY_RUNTIME` | 129 |
| `runtime_wiring\source_runtime\source_hydration_planner.py` | `READONLY_RUNTIME` | 145 |
| `runtime_wiring\source_runtime\source_pack_resolver.py` | `READONLY_RUNTIME` | 150 |
| `runtime_wiring\source_runtime\source_runtime_cache.py` | `READONLY_RUNTIME` | 144 |
| `runtime_wiring\source_runtime\source_runtime_query.py` | `DRY_RUN_ONLY` | 269 |
| `runtime_wiring\source_runtime\workbench_view_capability_map.py` | `DRY_RUN_ONLY` | 186 |
| `runtime_wiring\source_runtime\workbench_view_coverage_classifier.py` | `READONLY_RUNTIME` | 140 |
| `runtime_wiring\source_runtime\world_action_bus_dry_run_activation.py` | `DRY_RUN_ONLY` | 195 |
| `runtime_wiring\x108_admission_stub.py` | `DRY_RUN_ONLY` | 114 |