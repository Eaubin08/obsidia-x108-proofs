# Periphery Stabilization Rules — P72

**Statut :** P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT_READY  
**Date :** 2026-06-07

Ce document définit les règles de stabilisation pour chaque domaine périphérique. La périphérie est non-décisionnelle. Ces règles garantissent qu'elle reste dans cet état lors des extensions futures.

---

## Principe fondateur

La périphérie (mémoire, graphiti, agents, bus, connecteurs, sources, routes) n'a **aucune autorité décisionnelle**. Toute décision ACT/HOLD/BLOCK finale passe par Guard X-108 (`decideX108`). Cette garantie est portée par l'invariant `KX108_ONLY_DECISION_AUTHORITY` et renforcée par `NO_PERIPHERY_DECISION_AUTHORITY`.

---

## MEMORY_SRL — Session Registry Layer

**Statut actuel :** COMPLIANT  
**Audit palier :** P66  
**Invariants protégés :** NO_MEMORY_WRITE_WITHOUT_GATE, NO_PERIPHERY_DECISION_AUTHORITY

**Règles :**
- SRL = lecture seule par défaut. `memory_write_enabled=False`.
- Tout accès SRL est advisory — ne peut pas déclencher d'action.
- Aucun adapter SRL ne peut déclarer `emits_act=True`.

**Action si violée :** IMMEDIATE_HOLD — `memory_write_enabled` doit rester False jusqu'à gate KX108 explicite.

---

## GRAPHITI — Client readonly

**Statut actuel :** COMPLIANT  
**Audit palier :** P70  
**Invariants protégés :** NO_GRAPHITI_WRITE, NO_PERIPHERY_DECISION_AUTHORITY

**Règles :**
- `graphiti_v20_readonly_client.py` — GET uniquement, `write=False`, `graphiti_write_enabled=False`.
- Fallback stub en l'absence de serveur graphiti.
- Aucun write graphiti sans gate KX108 explicite et audit palier dédié.

**Action si violée :** IMMEDIATE_HOLD — tout write graphiti non-gaté = mutation d'état non-décisionnel.

---

## AGENTS — Composants agents

**Statut actuel :** COMPLIANT  
**Audit palier :** P71  
**Invariants protégés :** NO_PERIPHERY_DECISION_AUTHORITY, KX108_ONLY_DECISION_AUTHORITY

**Règles :**
- Agents = `advisory_only=True`, `emits_act=False`.
- Aucun agent ne peut prendre de décision finale sans passer par Guard.
- `_tmp_core_import/OBSIDIA_CORE_ONLY_FULL_MACHINERY` = DO_NOT_RUNTIME_LOAD. Import staging uniquement.

**Action si violée :** CLASSIFIER_HOLD — tout agent avec `emits_act=True` requiert audit palier dédié.

---

## BUS — Obsidia Bus Adapter

**Statut actuel :** COMPLIANT  
**Audit palier :** P61  
**Invariants protégés :** BUS_PROPOSE_ONLY, NO_PERIPHERY_DECISION_AUTHORITY

**Règles :**
- Bus = PROPOSE_ONLY. Aucun `emit_act`.
- Bus adapters classifiés `ADAPTER_DRY_RUN_SAFE` (P71).
- Tout bus adapter doit déclarer `dry_run_only=True`.

**Action si violée :** IMMEDIATE_HOLD — bus adapter avec `emit_act=True` = court-circuit Guard.

---

## CONNECTORS — Connecteurs actifs

**Statut actuel :** REVIEW_REQUIRED  
**Audit palier :** P70  
**Invariants protégés :** NETWORK_EGRESS_REVIEW_REQUIRED, DRY_RUN_ONLY_ADAPTERS

**Connecteurs concernés :**
- `connectors/aviation_robo.py` — `while True` + `requests.post()` + `irreversible=True` → CONNECTOR_ACTIVE_REVIEW (HIGH)
- `connectors/bank_normal_flow.py` — idem → CONNECTOR_ACTIVE_REVIEW (HIGH)
- `connectors/trading_live.py` — + `ccxt.binance()` externe → CONNECTOR_DO_NOT_RUN
- `connectors/graphiti_v20_readonly_client.py` — GET readonly → CONNECTOR_DRY_RUN_SAFE

**Règles :**
- `dry_run_declared=True` obligatoire avant activation.
- `kx108_authority_declared=False` pour tout connecteur non-Guard.
- `while True` + `requests.post()` + `irreversible=True` = DO_NOT_RUN sans audit gate.

**Action si violée :** DO_NOT_RUN — connecteur actif sans dry_run gate = action irréversible non-contrôlée.

---

## SOURCE_PACKS — Packs source et adapters

**Statut actuel :** COMPLIANT  
**Audit palier :** P71  
**Invariants protégés :** DRY_RUN_ONLY_ADAPTERS, SOURCE_PACK_NOT_CANON_BY_EXISTENCE

**État (P71) :**
- 14 source packs classifiés (8 SOURCE_FULL_LOCAL, 3 ARCHIVE_ONLY, 1 METADATA_ONLY, 1 UNCANONIZED, 1 DO_NOT_RUNTIME_LOAD)
- `runtime_allowed_now=0`, `emits_act=0`, `py_files_all_do_not_import=True`
- `source_file_registry.json` — safety invariants confirmés

**Règles :**
- `DRY_RUN_ONLY: bool = True` dans chaque adapter.
- `advisory_only=True` post-hydration (source_context_hydrator.py).
- `.py` interdit dans `readonly_content_loader.py` (`ForbiddenFileError`).
- Tout nouveau pack = MANIFEST_SHA256.json + source_file_registry avant runtime load.

**Action si violée :** AUDIT_REQUIRED — `runtime_allowed_now` doit rester 0.

---

## UI_ROUTES — Frontière d'authentification API

**Statut actuel :** PARTIAL_REVIEW (findings ouverts)  
**Audit palier :** P69  
**Invariants protégés :** ROUTE_AUTH_BOUNDARY

**Findings ouverts (P69/P71) :**
- `POST /api/runtime-wiring/source-runtime/preview` — sans `Depends(require_api_key)` → `SOURCE_EXCERPT_AUTH_REQUIRED`
- `POST /api/runtime-wiring/os-map/query` — sans auth → `SOURCE_EXCERPT_AUTH_REQUIRED`
- `source_pack_resolver.py` — chemin absolu `C:/Users/User/Downloads` → `SOURCE_PATH_EXPOSURE_REVIEW`

**Règles :**
- Toute nouvelle route exposant des données = `Depends(require_api_key)` obligatoire.
- 503 fail-fermé si `OBSIDIA_API_KEY` absent.
- Chemins absolus système → remplacer par env var ou relative path.

**Action si violée :** APPLY_AUTH — ADD_REQUIRE_API_KEY sur les endpoints concernés (P73+).
