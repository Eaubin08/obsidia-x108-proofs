# P63 — Global Fusion Reality Audit

**Status :** P63_GLOBAL_FUSION_REALITY_AUDIT_READY
**Mode :** AUDIT_ONLY — aucun fichier importé, aucune modification
**Branche :** p62-manual-review-deferred
**Commit :** 15fdb726053a5f9401e6c7a321f689e5b5f6b3d6
**Date :** 2026-06-07

---

## 1. Verdict court

### Ce qui est déjà là (et complet)

- **Sigma** est entièrement opérationnel — 58 fichiers Python, 5 domaines (bank, ecom, trading, gps_defense_aviation, meta), P56B/P56E patchés. **Aucun import core ne l'améliorerait**.
- **Runtime wiring** est en place — 49 fichiers, dry-run router, action gateway BLOCK>HOLD>ALLOW_CONTEXT_ONLY, readonly bridge, activation matrix.
- **Routes API** sont toutes présentes — 21 routes (readonly, dry-run, contrôlées). Aucune route core n'est manquante.
- **GPS/Défense/Aviation** est le domaine le plus avancé — 6 agents implémentés, 6 exemples, 3 tests intégration, 2 connectors terrain (`aviation_robo.py`, `gps_adapter.py`), pipeline sigma connecté.
- **Graphiti/Memory** sont isolés et controlés — `graphiti_write=False`, `memory_write=False`, `neo4j_write=False` systématiques, vérifiés par tests.

### Ce qui est partiel

- **Bus adapters** : 2/4 adaptés P61 (DRY_RUN_ONLY) — `__init__.py` et `registry.py` bloqués (registry nécessite `os_trad/adapter.py` manquant).
- **Agents prompts** : présents comme MDs dans `agents/prompts/` — le runtime Python est sigma (pas les agents/ core).
- **Wording canon** : globalement mesuré — quelques termes forts dans `GLOSSAIRE.md` et `KERNEL_OVERVIEW.md` non critiques.

### Ce qui manque vraiment

- `engine/os0/determinism.py`, `engine/os1/parse_input.py`, `engine/os3/svg.py` — 3 candidats SAFE_READONLY (P62) non encore adaptés.
- `engine/core_full/modules/os_trad/adapter.py` — débloque le bus `registry.py` P61.
- `agents/sigma_dashboard.py`, `agents/utils/indicators.py` — pas de doublon dans sigma, candidats import.

### Ce qui est dangereux à fusionner brut

- `engine/obsidia_runtime/engine_final.py` et `engine_runtime.py` — **runtime live actif**, activeraient ACT sans adapter.
- `engine/obsidia_kernel/kernel.py` — **kernel mutations non bornées** sans DRY_RUN_ONLY.
- `engine/api_server/worm_uploader.py` — **write WORM actif**, DO_NOT_IMPORT définitif.
- Tout import des 5 fichiers sigma P56B protégés depuis core — **régression garantie** (perte GpsDefenseAviationState, veto boundary).

---

## 2. Matrice globale

| Surface | Déjà en place | Partiel | Absent réel | Risque | Prochain palier |
|---|---:|---:|---:|---|---|
| agents | 17 fichiers (sigma/) | 2 | 2 core | LOW | P65 |
| engine/runtime | 49+21 fichiers | 2 bus | 7 core bloqués | HIGH (core), NONE (existant) | P67 |
| sigma | 58 fichiers | 0 | 0 | HIGH si écrasé | P66 |
| routes API | 21 routes | 0 | 0 | MEDIUM (brody POST) | P68 |
| wording canon | ~95% corrigé | quelques termes | 3 remplacements | LOW | P70 |
| support présentation | 25+ docs | mixte tech/narratif | 0 | LOW | P71 |
| GPS defense aviation | 6 agents + 6 ex + 3 tests | 3 adapters OS | 4 | LOW | P69 |
| graphiti/brody/memory | isolés, write=False | — | — | NONE | surveillance |

---

## 3. Agents

### Déjà dans sigma/proof

| Fichier proof | Équivalent core | Statut |
|---|---|---|
| `sigma/domains/bank_agents.py` | `agents/domains/bank_agents.py` | **PROOF IN PLACE** |
| `sigma/domains/ecom_agents.py` | `agents/domains/ecom_agents.py` | **PROOF IN PLACE** |
| `sigma/domains/gps_defense_aviation_agents.py` | absent core | **PROOF UNIQUEMENT** |
| `sigma/domains/meta_agents.py` | `agents/domains/meta_agents.py` | **PROOF IN PLACE** |
| `sigma/domains/trading_agents.py` | `agents/domains/trading_agents.py` | **PROOF IN PLACE** |
| `sigma/registry.py` | `agents/registry.py` | **PROOF IN PLACE** |
| `sigma/run_pipeline.py` | `agents/run_pipeline.py` | **PROOF IN PLACE (P56B)** |
| `sigma/obsidia_sigma_v130.py` | `agents/obsidia_sigma_v130.py` | **PROOF IN PLACE** |
| `sigma/sigma_monitor.py` | `agents/sigma_monitor.py` | **PROOF IN PLACE** |

### Seulement core (candidats import P65)

| Fichier core | Raison | Décision |
|---|---|---|
| `agents/sigma_dashboard.py` | Pas d'équivalent sigma | IMPORT_TEST P65 |
| `agents/utils/indicators.py` | Utilitaire readonly | IMPORT_TEST P65 |

### Doublons — proof supérieur (ne pas importer)

| Core | Proof | Raison |
|---|---|---|
| `agents/aggregation.py` | `sigma/aggregation.py` | Proof P56B gamma |
| `agents/contracts.py` | `sigma/contracts.py` | Proof P56B + GpsDefenseAviationState |
| `agents/guard.py` | `sigma/guard.py` | Proof P56D veto boundary |
| `agents/protocols.py` | `sigma/protocols.py` | Proof P56B canonical decision |
| `agents/run_pipeline.py` | `sigma/run_pipeline.py` | Proof P56B + GPS domain |
| `python_agents/*` (10 fichiers) | `sigma/*` | Tous doublons agents/ |

### Bloqués définitivement

- `agents/sigma_config.json` — conflit sigma/ config (DO_NOT_IMPORT P62)
- `agents/base.py`, `agents/registry.py`, `python_agents/__init__.py`, `python_agents/demo_run.py` — bloqués P62

---

## 4. Runtime / Engine

### Readonly existant

| Fichier | Rôle | Statut |
|---|---|---|
| `runtime_wiring/source_runtime/readonly_content_loader.py` | Chargement readonly | PRESENT |
| `runtime_wiring/source_runtime/graphiti_memory_readonly_activation.py` | Graphiti readonly | PRESENT |
| `runtime_wiring/source_runtime/brody_readonly_activation.py` | Brody readonly | PRESENT |
| `runtime_wiring/engine_bridge/readonly_engine_bridge.py` | Bridge engine readonly | PRESENT |

### Dry-run existant

| Fichier | Rôle | Statut |
|---|---|---|
| `runtime_wiring/dry_run_packet_router.py` | Router dry-run principal | PRESENT |
| `runtime_wiring/source_runtime/action_gateway_hold_block_sandbox.py` | BLOCK>HOLD>ALLOW | PRESENT |
| `apps/obsidia_api/bus/message.py` | DRY_RUN_ONLY=True (P61) | PRESENT |
| `apps/obsidia_api/bus/router.py` | DRY_RUN_ONLY=True (P61) | PRESENT |

### Runtime actif absent (ne pas importer brut)

| Fichier core | Risque | Décision |
|---|---|---|
| `engine/obsidia_runtime/engine_final.py` | HIGH — runtime live | BLOCKED |
| `engine/obsidia_runtime/engine_runtime.py` | HIGH — runtime live | BLOCKED |
| `engine/obsidia_kernel/kernel.py` | HIGH — kernel mutations | BLOCKED |
| `engine/unified/orchestrator.py` | MEDIUM — orchestration | BLOCKED |
| `engine/unified/pipeline.py` | MEDIUM — pipeline | BLOCKED |
| `engine/api_server/worm_uploader.py` | HIGH — write WORM | DO_NOT_IMPORT |

### Candidats adapter (P67)

| Fichier core | Surface P62 | Adapter cible |
|---|---|---|
| `engine/os0/determinism.py` | SAFE_READONLY_ADAPTER_CANDIDATE | readonly wrapper |
| `engine/os1/parse_input.py` | SAFE_READONLY_ADAPTER_CANDIDATE | readonly wrapper |
| `engine/os3/svg.py` | SAFE_READONLY_ADAPTER_CANDIDATE | readonly wrapper |
| `engine/core_full/modules/os_trad/adapter.py` | IMPORT_AFTER_ADAPTER | débloque P61 registry.py |

---

## 5. Sigma

### Fichiers protégés (ne jamais écraser)

| Fichier | Raison |
|---|---|
| `sigma/aggregation.py` | P56B gamma — score calibré |
| `sigma/contracts.py` | P56B + GpsDefenseAviationState + CanonicalDecisionEnvelope |
| `sigma/guard.py` | P56D — veto post-guard boundary |
| `sigma/protocols.py` | P56B — aggregate_gps_defense_aviation |
| `sigma/run_pipeline.py` | P56B — OS4 CLI bridge complet |
| `sigma/contracts.broken-ragnarok.py` | Scellé ragnarok |

### Déjà patchés P56

Tous les fichiers sigma/ sont au niveau P56B minimum. La suite P56A→P56E est complète. Sigma est la couche la plus aboutie du repo.

### Fichiers core régressifs (import interdit)

Les 5 fichiers core correspondant aux fichiers protégés manquent :
- Les patches P56B gamma (scores calibrés, severities révisées)
- GpsDefenseAviationState (absent dans core agents/)
- aggregate_gps_defense_aviation (absent dans core agents/)
- Le veto post-guard P56D

### Modifications possibles (P66)

Extension non-destructive uniquement via `sigma/connectors.py` (F64, descriptive map) et `sigma/packets.py` (F62, readonly normalizer). Toute modification des fichiers protégés nécessite un diff minimal reviewé.

---

## 6. Routes API

### Routes déjà présentes — classées

| Route | Type | Risque |
|---|---|---|
| `audit.py` | readonly | NONE |
| `worldcalls.py` | readonly, dry_run_only=True | NONE |
| `runtime_freeze.py` | readonly dashboard | NONE |
| `sigma_monitoring.py` | readonly GET (F63) | NONE |
| `os_map.py` | readonly | NONE |
| `source_runtime_status.py` | readonly | NONE |
| `status.py` | readonly | NONE |
| `graphiti.py` | readonly proxy (fallback BACKEND_STUB) | NONE |
| `runtime_wiring_preview.py` | readonly preview | NONE |
| `blockchain.py` | dry-run simulation | LOW |
| `bus.py` | dry-run bus signals | LOW |
| `os3.py` | dry-run OS3 | LOW |
| `os_trad_ir_reverse.py` | reverse IR dry-run | LOW |
| `brody.py` | POST contrôlé, API key | MEDIUM |
| `memory.py` | candidates, auto_promotion=False | LOW |
| `context.py` | context injection POST | LOW |

### Routes core à ne pas brancher

- `engine/api_server/main.py` — couvert par apps/obsidia_api (DO_NOT_IMPORT)
- `engine/api_server/worm_uploader.py` — write WORM (DO_NOT_IMPORT)
- `engine/api_server/security.py`, `signing.py` — architectural review requis

### Route à adapter (P68)

- `engine/api_server/audit_log.py` — comparer avec `apps/obsidia_api/` avant import éventuel

---

## 7. Canon wording

### Termes acceptables (justifiés techniquement)

| Terme | Justification |
|---|---|
| `deterministic` | Prouvé — Merkle + hash chain + seal V18_3_1 |
| `canonical` | Hash-ancré — sha256 + Merkle |
| `frozen` | Merkle seal + RFC3161 |
| `KX108_ONLY` | Contrainte effective à 3 niveaux (module, route, response) |
| `by construction` | Architecture boundary, pas convention |
| `readonly` | Vérifié par tests + boundary dicts |
| `BLOCK > HOLD > ALLOW_CONTEXT_ONLY` | Priority order prouvé dans action_gateway |

### Termes trop forts (à réviser en P70)

| Fichier | Terme | Révision suggérée |
|---|---|---|
| `docs/GLOSSAIRE.md` | "moins de 5 millisecondes" | "conçu pour interception avant exécution" |
| `docs/GLOSSAIRE.md` | "garantissant la sécurité" | "visant à assurer la sécurité" |
| `docs/KERNEL_OVERVIEW.md` | "Décision ex ante garantie" | "Décision ex ante by design" |

### Fichiers à laisser

- `docs/core_import/P56-P62` — audit records, ne pas modifier
- `proofs/V18_3_1/` — sealed proof
- `docs/demo/OBSIDIA_F41_WHAT_IT_PROVES_AND_DOES_NOT_PROVE.md` — scope bornant utile

---

## 8. Support présentation

### Docs techniques (rester dans le repo)

- `docs/core_import/P56-P62` (audit chain)
- `docs/architecture/F68-F73` (décisions architecturales)
- `proofs/V18_3_1/` (preuve moteur scellée)
- `docs/freeze/` (runtime freeze evidence)
- `docs/demo/F43-F59` (runbooks opérateur)

### Docs narratifs (candidats séparation P71)

- `docs/demo/OBSIDIA_F41_PUBLIC_INVESTOR_PITCH.md`
- `docs/demo/OBSIDIA_F41_INVESTOR_JURY_FAQ.md`
- `docs/demo/OBSIDIA_F41_DEMO_SCRIPT_3_5_MIN.md`
- `docs/civilization/AGENTIC_CONSTITUTIONAL_CIVILIZATION_STACK_V1.md`
- `docs/civilization/OBSIDIA_AS_AGENTIC_GOVERNANCE_INFRASTRUCTURE_V1.md`

**Risque actuel :** les docs narratifs coexistent avec les preuves techniques dans le même repo. Ils ne polluent pas les tests. La séparation est utile mais non urgente.

---

## 9. GPS / Défense / Aviation

### Déjà intégré sigma

| Composant | Statut |
|---|---|
| `sigma/domains/gps_defense_aviation_agents.py` | **6 agents implémentés** |
| `sigma/protocols.py aggregate_gps_defense_aviation` | **Pipeline connecté** |
| `sigma/registry.py build_gps_defense_aviation_agents` | **Registré** |
| `sigma/run_pipeline.py domain=gps_defense_aviation` | **CLI supporté** |
| `apps/obsidia_api/routes/sigma_monitoring.py` | **Endpoint GET /api/periphery/monitoring/sigma/gps** |

### Testé

| Test | Type |
|---|---|
| `tests/integration/test_full_stack_static_gps.py` | Intégration stack complète |
| `tests/integration/test_sigma_bridge_gps.py` | Bridge sigma GPS |
| `tests/integration/test_v3_full_pipeline_gps.py` | Pipeline V3 GPS |

### Terrain portable (connecteurs existants)

| Connecteur | Cible |
|---|---|
| `connectors/aviation_robo.py` | `localhost:8000/api/periphery/monitoring/adapters/gps` |
| `periphery/adapters/gps_adapter.py` | Adapter periphery GPS |

### Données sauvegardées (sigma/examples/)

`gps_nominal.json`, `gps_brownout.json`, `gps_no_source.json`, `gps_omega_chaos.json`, `gps_source_conflict.json`, `gps_time_skew.json`

### Manques pour P69

1. `engine/os0/determinism.py` (SAFE_READONLY_ADAPTER_CANDIDATE) — invariant déterminisme OS0
2. `engine/os1/parse_input.py` (SAFE_READONLY_ADAPTER_CANDIDATE) — parseur entrées OS1
3. `engine/os3/svg.py` (SAFE_READONLY_ADAPTER_CANDIDATE) — génération SVG OS3
4. `engine/core_full/modules/os_trad/adapter.py` (IMPORT_AFTER_ADAPTER) — débloque P61 registry.py

---

## 10. Plan de fusion total

### P64 — TARGETED_FUSION_PLAN

Transformer l'audit P63 en lots exécutables. Critères d'entrée/sortie pour P65-P72.

### P65 — AGENTS_RECONCILIATION (risque LOW)

Importer `agents/sigma_dashboard.py` et `agents/utils/indicators.py`. Ne toucher aucun doublon proof_wins. Surface AUDIT_TOOLING.

### P66 — SIGMA_SAFE_EVOLUTION (risque MEDIUM)

Modifier sigma par patches ciblés uniquement. Jamais écraser les 5 fichiers P56B protégés. Extension via `connectors.py` et `packets.py` uniquement.

### P67 — RUNTIME_READONLY_DRYRUN_ADAPTERS (risque LOW-MEDIUM)

Adapter `engine/os0/determinism.py`, `engine/os1/parse_input.py`, `engine/os3/svg.py` (SAFE_READONLY_ADAPTER_CANDIDATE). Adapter `engine/core_full/modules/os_trad/adapter.py` (débloque P61 `registry.py`). Pattern DRY_RUN_ONLY identique à P61.

### P68 — API_ROUTES_CONTROLLED_WIRING (risque MEDIUM)

Brancher `engine/api_server/audit_log.py` après comparaison. Vérifier couverture GPS endpoint terrain. Ne pas toucher worm_uploader ni engine_final.

### P69 — GPS_TERRAIN_PORTABLE_RECONCILIATION (risque LOW)

Valider `connectors/aviation_robo.py` vs sigma_monitoring GPS endpoint. Tests terrain portables. Import adapters OS après P67.

### P70 — CANON_WORDING_GLOBAL_CLEANUP (risque LOW)

Corriger 3 termes dans `GLOSSAIRE.md` et `KERNEL_OVERVIEW.md`. Garder tous termes techniques justifiés. Ajouter tests détection.

### P71 — PRESENTATION_PROOF_SEPARATION (risque LOW)

Créer `docs/public/`. Déplacer docs narratifs F41-series + civilization/. Garder docs opérateur F43-F59 en place.

### P72 — FULL_REGRESSION_FREEZE (risque NONE)

Suite complète : P56E→P72 tests + verify_all + forbidden + manifest + freeze.

---

## Périmètres non touchés par P63

| Périmètre | Modifié |
|---|---|
| sigma/ | NON |
| apps/obsidia_api/routes/ | NON |
| runtime_wiring/ | NON |
| proofs/V18_3_1/ | NON |
| ACT | NON |
| memory_write | NON |
| graphiti_write | NON |
| kernel_mutation | NON |

## Suite recommandée

**P67** (adapters OS0/OS1/OS3 + os_trad) → **P65** (agents complémentaires) → **P69** (GPS terrain) → **P70** (wording)
