# P43 — Unconnected Runtime Surface Audit Report

**Date:** 2026-06-04
**Branch:** p43-unconnected-runtime-surface-audit
**Status:** P43_UNCONNECTED_RUNTIME_SURFACE_AUDIT_READY
**Decision authority:** KX108_ONLY | No ACT | Readonly

---

## Objectif

Scanner la surface runtime complète du repo (P36→P42) et produire la carte :

> TOUT CE QUI EXISTE vs TOUT CE QUI EST BRANCHÉ vs TOUT CE QUI RESTE À BRANCHER

---

## Inventaire Baseline (P37)

| Catégorie | Total |
|---|---|
| Modules Python | 117 |
| Fonctions | 535 |
| Classes | 133 |
| Routes API | 147 |
| Adapters | 10 |
| Fichiers tests | 133 |
| Fichiers docs | 26 |
| Edges (graphe) | 178 |

Source : `runtime_wiring/source_runtime/runtime_inventory_graph.py` (P37)
Capability router : `runtime_wiring/source_runtime/capability_path_router.py` (P36) — 14 capabilities déclarées

---

## Couverture Capability Router

### Modules directement référencés dans les templates de capacité

| Module (stem) | Capabilities |
|---|---|
| `brody_source_context_bridge` | MEMORY_REINTEGRATION, GRAPHITI_READONLY, OS_TRAD, PROVENANCE_TRACE, NPL, RSSI |
| `os_trad_reverse_index` | OS_TRAD_TRANSLATION, AGENT_TREE_LOOKUP, LAW_PROTOCOL_LOOKUP |
| `reverse_os_interlanguage_index` | IR_ALPHABET_MAPPING, REVERSE_OS_INTERLANGUAGE |
| `source_context_hydrator` | REVERSE_OS_INTERLANGUAGE, SOURCE_CONTEXT |
| `source_hydration_planner` | (via bridge imports) |
| `source_runtime_query` | toutes les capabilities source |

**10 modules directement connectés** (via router + static edges)
**27 modules partiellement connectés** (infra cœur utilisée par les modules connectés)
**80 modules non connectés** (voir détail ci-dessous)

---

## Familles Source — Couverture

| Famille | Entrées | Adapter | Capability | Statut |
|---|---|---|---|---|
| ATLAS | 11 263 | `atlas_to_context_packet` | ❌ Aucune | **MUST_BIND_NEXT** |
| COGNITIVE_REINTEGRATION | 2 052 | `cognitive_to_context_packet` | ✅ MEMORY_REINTEGRATION, SOURCE_CONTEXT | Connectée |
| COMPLIANCE_DATA_GOVERNANCE | 488 | `compliance_to_context_packet` | ✅ PROOF_AUDIT_CONTEXT | Connectée |
| EXTERNAL_SIGNALS | 82 | `external_signals_to_context_packet` | ❌ Aucune | **MUST_BIND_NEXT** |
| NARRATIVE_PROVENANCE_LAYER | 103 | `npl_to_context_packet` | ✅ NPL_NARRATIVE_PROVENANCE, PROVENANCE_TRACE | Connectée |
| OS_TRAD_REVERSE_OS | 555 | `os_trad_reverse_to_context_packet` | ✅ OS_TRAD_TRANSLATION, AGENT_TREE | Connectée |
| RSSI_RGPD | 976 | `rssi_rgpd_to_context_packet` | ✅ RSSI_SECURITY_CONTEXT, PROOF_AUDIT | Connectée |
| RSSI_SECURITY_PRESENTATION | 334 | `rssi_security_to_context_packet` | ✅ RSSI_SECURITY_CONTEXT | Connectée |

**6/8 familles connectées.** ATLAS (11k entrées, la plus grande!) et EXTERNAL_SIGNALS sont orphelines.

---

## Adapters — Couverture

| Adapter | Module | Capability | Statut |
|---|---|---|---|
| `atlas_to_context_packet` | source_adapters.py | ❌ Aucune | **MUST_BIND_NEXT** |
| `cognitive_to_context_packet` | source_adapters.py | ✅ | Connecté |
| `compliance_to_context_packet` | source_adapters.py | ✅ | Connecté |
| `external_signals_to_context_packet` | source_adapters.py | ❌ Aucune | **MUST_BIND_NEXT** |
| `npl_to_context_packet` | source_adapters.py | ✅ | Connecté |
| `os_trad_reverse_to_context_packet` | source_adapters.py | ✅ | Connecté |
| `reverse_os_interlanguage_to_context_packet` | source_adapters.py | ✅ | Connecté |
| `route_entry_to_context_packet` | registry_to_adapter_dry_run.py | ❌ Interne uniquement | À revoir |
| `rssi_rgpd_to_context_packet` | source_adapters.py | ✅ | Connecté |
| `rssi_security_to_context_packet` | source_adapters.py | ✅ | Connecté |

**7/10 adapters référencés dans les capabilities.**

---

## Routes API — Couverture

| Statut | Routes | % |
|---|---|---|
| Connectées au capability router | 3 | 2% |
| Non connectées | 144 | 98% |

### Routes connectées

| Route | Fonction |
|---|---|
| `GET /api/runtime-wiring/preview` | `runtime_wiring_preview` |
| `GET /api/runtime-wiring/source-runtime/status` | `source_runtime_status` |
| `POST /api/runtime-wiring/source-runtime/preview` | `source_runtime_preview` |

### Groupes de routes non connectées (144)

| Groupe | Nb routes | Priorité connexion |
|---|---|---|
| `/api/brody/chat` | 1 | **MUST_BIND_NEXT** (entry point primaire) |
| `/api/runtime-wiring/os-trad/*` | 3 | **MUST_BIND_NEXT** (IR/OS-Trad routes) |
| `/api/x108/*` | 14 | SHOULD_BIND |
| `/api/os3/*` | 7 | SHOULD_BIND |
| `/api/memory/*` | 6 | SHOULD_BIND |
| `/api/periphery/governance/*` | 10 | UNKNOWN_REQUIRES_REVIEW |
| `/api/periphery/pipeline/*` | 12 | UNKNOWN_REQUIRES_REVIEW |
| `/api/periphery/gencoin/*` | 6 | UNKNOWN_REQUIRES_REVIEW |
| `/api/periphery/interface/*` | 7 | UNKNOWN_REQUIRES_REVIEW |
| `/api/blockchain/*` | 9 | KEEP_READONLY |
| `/api/sigma/*` | 6 | KEEP_READONLY |
| `/api/graphiti/*` | 2 | SHOULD_BIND |
| `/api/worldcalls/*` | 2 | KEEP_READONLY |
| Autres | ~60 | UNKNOWN_REQUIRES_REVIEW |

---

## Modules — Classification

### A. MUST_BIND_NEXT (7 items)

1. `source_family:ATLAS` — 11 263 entrées, adapter `atlas_to_context_packet` existe, aucune capability
2. `source_family:EXTERNAL_SIGNALS` — 82 entrées (TimeVerse temporal), adapter existe, aucune capability
3. `adapter:atlas_to_context_packet` — orphelin, aucune capability ne l'appelle
4. `adapter:external_signals_to_context_packet` — orphelin
5. `route:/api/brody/chat` — entry point primaire Brody non surfacé dans les templates
6. `module:graphiti_v20_readonly_client.py` — capability GRAPHITI_READONLY_CONTEXT déclarée, module non branché
7. `route:/api/runtime-wiring/os-trad/api/*` — 3 routes opérationnelles non dans les templates

### B. SHOULD_BIND (10 items)

1. `module:brody_v1_4_12a_final_answer_adapter.py` — chemin final_answer non câblé au router
2. `module:brody_semantic_query_router.py` — routeur sémantique existant, non connecté
3. `module:brody_memory_response_chain_adapter.py` — chaîne mémoire-réponse non connectée
4. `module:brody_full_runtime_orchestrator.py` — orchestration complète non dans router
5. `route:/api/x108/*` — 14 routes X108 actives, aucun template capability
6. `route:/api/os3/*` — 7 routes OS3, aucun template capability
7. `route:/api/memory/*` — 6 routes mémoire, aucun template capability
8. `module:brody_real_response_pipeline.py` — pipeline réponse réelle non câblé
9. `capability:ATLAS` — à déclarer (11k entrées en attente)
10. `capability:EXTERNAL_SIGNALS` — à déclarer (signaux temporels TimeVerse)

### C. KEEP_READONLY (11 items)

- `runtime_wiring/engine_bridge/readonly_engine_bridge.py`
- `runtime_wiring/engine_bridge/api_adapter_preview.py`
- `runtime_wiring/engine_bridge/bridge_types.py`
- `apps/obsidia_api/brody_safe_snapshot.py`
- `apps/obsidia_api/brody_freeze_metrics_snapshot.py`
- `apps/obsidia_api/bus/sigma_bridge.py`
- `apps/obsidia_api/bus/signal_model.py`
- `apps/obsidia_api/bus/signal_packager.py`
- `apps/obsidia_api/bus/state_aggregator.py`
- `apps/obsidia_api/brody_readonly_intent_guard.py`
- `apps/obsidia_api/brody_rights_authority_matrix.py`

### D. ARCHIVE_ONLY (3 items)

- `runtime_wiring/p8b_demo.py` (démo P8B, remplacé par P36+)
- `runtime_wiring/source_registry/p9c_integration_demo.py` (démo P9C)
- `runtime_wiring/source_registry/build_source_file_registry.py` (script de build)

### E. DO_NOT_BIND (2 items)

- Source packs `.py` dans le registry (DO_NOT_IMPORT_RUNTIME — interdit)
- `apps/obsidia_api/brody_existing_reverse_os_bridge.py` (remplacé par P35)

### F. UNKNOWN_REQUIRES_REVIEW (35 modules)

Principalement les 42 modules `brody_*` de `apps/obsidia_api/` non encore analysés.
Plusieurs contiennent des adapters ou des compositeurs qui pourraient être intégrés au router.
Nécessitent une inspection individuelle avant décision.

---

## Vues Workbench — Couverture

| Vue | Connectée | Notes |
|---|---|---|
| `RuntimeWiringPreviewView.tsx` | ✅ | P29+ capability preview |
| `OSMapView.tsx` | ✅ | P38 OS Map |
| `ChatView.tsx` | Partielle | `/api/brody/chat` branché, pas dans capability templates |
| `GraphitiView.tsx` | Non | Routes graphiti non dans router |
| `MemoryView.tsx` | Non | Routes memory non dans router |
| `OS3View.tsx` | Non | Routes OS3 non dans router |
| `X108View.tsx` | Non | Routes X108 non dans router |
| `AuditView.tsx` | Non | Audit routes non dans router |
| `BlockchainView.tsx` | Non | KEEP_READONLY |
| `GencoinView.tsx` | Non | UNKNOWN_REQUIRES_REVIEW |
| `TranslationView.tsx` | Partielle | os_trad routes non dans templates |
| `WorldCallView.tsx` | Non | KEEP_READONLY |
| `SettingsView.tsx` | Non | Frontend uniquement |

---

## Priorités de Connexion Suivantes

| Priorité | Item | Raison |
|---|---|---|
| 1 | Capability ATLAS | 11 263 entrées, adapter prêt, plus grand gap |
| 2 | Capability EXTERNAL_SIGNALS | Signaux TimeVerse, adapter prêt |
| 3 | `/api/brody/chat` dans capability templates | Entry point primaire non surfacé |
| 4 | `graphiti_v20_readonly_client` dans GRAPHITI capability | Module graphiti non branché |
| 5 | `/api/runtime-wiring/os-trad/*` dans templates | 3 routes IR/OS-Trad opérationnelles |
| 6 | `brody_v1_4_12a_final_answer_adapter` | Chemin final_answer critique |
| 7 | X108 route capability surface | 14 routes X108 sans couverture capability |

---

## Récapitulatif de Couverture

| Catégorie | Total | Connecté | Partiel | Non connecté | % connecté |
|---|---|---|---|---|---|
| Modules | 117 | 10 | 27 | 80 | 8.5% |
| Fonctions | 535 | 46 | ~80 | ~409 | 8.6% |
| Routes | 147 | 3 | 0 | 144 | 2.0% |
| Adapters | 10 | 7 | 0 | 3 | 70% |
| Familles source | 8 | 6 | 0 | 2 | 75% |
| Vues workbench | 13 | 2 | 2 | 9 | 15% |

**Verdict** : La machinerie centrale (source runtime, capability router, P36-P42) est bien câblée.
L'orbite Brody (42 modules), les routes X108/OS3/memory, et les familles ATLAS/EXTERNAL_SIGNALS
représentent la surface principale restant à connecter. Aucune anomalie de safety détectée.

---

## Invariants de Sécurité

- `runtime_allowed_now = False` : aucun module audité n'active ce flag
- `emits_act = False` : confirmé sur tous les modules de la chaîne capability
- `decision_authority = KX108_ONLY` : maintenu dans toute la surface connectée
- Contenu interdit : `FORBIDDEN_CONTENT_PASS` (check_forbidden_content.py)

---

*Généré par P43 — lecture seule, aucune modification au kernel, aucun ACT.*
