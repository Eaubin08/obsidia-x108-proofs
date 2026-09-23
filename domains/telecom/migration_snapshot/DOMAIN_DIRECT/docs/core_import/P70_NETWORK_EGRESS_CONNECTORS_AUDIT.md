# P70 — Network Egress & Connectors Audit

**Audit ID :** P70  
**Statut :** `P70_NETWORK_EGRESS_CONNECTORS_AUDIT_READY`  
**Mode :** `AUDIT_ONLY` — aucun patch, aucune correction, aucun appel réseau  
**Branche :** `p70-network-egress-connectors-audit`  
**Date :** 2026-06-07

---

## 1. Verdict court

### Fichiers scannés

| Surface | Fichiers |
|---|---:|
| `apps/obsidia_api` | 181 |
| `apps/obsidia_api/routes` | 44 |
| `runtime_wiring` | 111 |
| `sigma` | 136 |
| `periphery` | 3278 |
| `connectors` | 10 |
| `scripts` | 258 |
| `tools` | 33 |
| `proofs` | 188 |
| `tests` | 1030 |
| `audit` | 27 |
| `docs` | 883 |
| `_source_packs` | 51 |
| `_tmp_core_import` | 368 |
| `_freezes` | 2986 |
| `.local_audits` | 46 |
| **TOTAL** | **9 630** |

### Network matrix — 17 entrées classifiées

| Catégorie | Nb | Verdict |
|---|---:|---|
| `NETWORK_EGRESS_NONE` | 5 | SAFE — aucune sortie réseau |
| `NETWORK_EGRESS_GRAPHITI_REVIEW` | 3 | REVIEW — write flags à vérifier |
| `NETWORK_EGRESS_CONNECTOR_ACTIVE_REVIEW` | 2 | HIGH — while True + irreversible, manque dry_run |
| `NETWORK_EGRESS_LOCALHOST_REVIEW` | 2 | LOW — scripts/tools, non runtime |
| `NETWORK_EGRESS_TEST_ONLY` | 2 | SAFE — smoke/archives |
| `NETWORK_EGRESS_TRADING_REVIEW` | 1 | HIGH — ccxt.binance() externe + while True |
| `NETWORK_EGRESS_NEO4J_REVIEW` | 1 | MEDIUM — P66 patché, fail-closed |
| `NETWORK_EGRESS_BLOCKED` | 1 | MEDIUM — proof only, inexécutable |

### Connector matrix — 6 connecteurs classifiés

| Catégorie | Nb | Verdict |
|---|---:|---|
| `CONNECTOR_ACTIVE_REVIEW` | 2 | HIGH — aviation + bank, manquent dry_run + KX108 |
| `CONNECTOR_DO_NOT_RUN` | 1 | HIGH — trading_live + ccxt externe |
| `CONNECTOR_DRY_RUN_SAFE` | 1 | LOW — graphiti_v20 readonly |
| `CONNECTOR_REQUIRES_AUTH_BOUNDARY` | 1 | MEDIUM — neo4j P66 patché |
| `CONNECTOR_LOCALHOST_REVIEW` | 1 | LOW — sigma tool one-shot |

### Zones safe confirmées

- `sigma/connectors.py` — descriptive-only, route constants relatives, aucun appel réseau
- `sigma/graphiti_readonly_bridge.py` — pure in-process, `graphiti_probe_mode=IN_PROCESS_ONLY`
- `apps/obsidia_api/routes/worldcalls.py` — lecture locale `audit/world_action_bus.jsonl` uniquement
- `apps/obsidia_api/brody_memory_response_chain_adapter.py` — vérifie env vars, aucune connexion réelle
- `runtime_wiring/source_runtime/world_action_bus_dry_run_activation.py` — local jsonl, gelé P56E
- `.local_audits/` smoke scripts — archives, non runtime
- `periphery/brody_memory_readonly/` smoke scripts — validation locale uniquement

### Zones à adresser (P71)

- `connectors/aviation_robo.py` — ADD_DRY_RUN_FLAG_AND_KX108_BOUNDARY
- `connectors/bank_normal_flow.py` — ADD_DRY_RUN_FLAG_AND_KX108_BOUNDARY
- `connectors/trading_live.py` — CONNECTOR_DO_NOT_RUN sans gate explicite

### Zones guarded (OK état courant)

- `graphiti_v20_readonly_client.py` — GET readonly, fallback stub, write flags False
- `neo4j_brody_guide_bridge_readonly_v1.py` — P66 patché, NEO4J_PASSWORD fail-closed, double guard

---

## 2. Modèle réseau/egress

| Catégorie | Description | Autorisé ? | Exemple |
|---|---|:---:|---|
| `NETWORK_EGRESS_NONE` | Aucun appel réseau actif. In-process. | ✓ SAFE | sigma/connectors.py |
| `NETWORK_EGRESS_DOC_ONLY` | URLs dans docs/strings uniquement. | ✓ SAFE | docs/*  |
| `NETWORK_EGRESS_TEST_ONLY` | Appels réseau dans tests/smoke/archive. | ✓ SAFE | .local_audits/ |
| `NETWORK_EGRESS_LOCALHOST_REVIEW` | POST/GET localhost, scripts/tools. | ✓ (TOOL) | run_bank_enterprise_pack.py |
| `NETWORK_EGRESS_CONNECTOR_DRY_RUN` | Connecteur localhost avec dry_run déclaré. | ✓ GUARDED | graphiti_v20_readonly_client.py |
| `NETWORK_EGRESS_CONNECTOR_ACTIVE_REVIEW` | POST localhost + while True + irreversible. | ⚠️ REVIEW | aviation_robo, bank_normal_flow |
| `NETWORK_EGRESS_GRAPHITI_REVIEW` | Graphiti localhost. OK si write flags False. | ⚠️ REVIEW | graphiti_v20_readonly_client |
| `NETWORK_EGRESS_NEO4J_REVIEW` | bolt://localhost Neo4j. P66 guarded. | ⚠️ MEDIUM | neo4j_brody_guide_bridge |
| `NETWORK_EGRESS_MARKET_DATA_REVIEW` | ccxt market data externe. | ⚠️ REVIEW | trading_live (ccxt.binance) |
| `NETWORK_EGRESS_TRADING_REVIEW` | Trading live + ccxt + while True. | ✗ DO_NOT_RUN | trading_live |
| `NETWORK_EGRESS_WEBHOOK_REVIEW` | POST vers URL externe webhook. | ✗ NON DÉTECTÉ | — |
| `NETWORK_EGRESS_BLOCKED` | Infra inexistante / proof only. | — BLOCKED | proofs/distributed/aggregator.py |

---

## 3. Focus findings

### 1. connectors/aviation_robo.py — CONNECTOR_ACTIVE_REVIEW ⚠️

`run_flight_flow()` : `while True` + `requests.post(127.0.0.1:8000/gps, timeout=10)` + `time.sleep(4)`.  
Payload contient `irreversible=True`. **Aucun `dry_run_flag`**. **Aucune déclaration `KX108_ONLY`**.  
Non patché en P70. Action P71 : `ADD_DRY_RUN_FLAG_AND_KX108_BOUNDARY`.

### 2. connectors/bank_normal_flow.py — CONNECTOR_ACTIVE_REVIEW ⚠️

`run_normal_bank()` : `while True` + `requests.post(127.0.0.1:8000/bank, timeout=10)` + `time.sleep(10)`.  
Payload contient `irreversible=True`. **Aucun `dry_run_flag`**. **Aucune déclaration `KX108_ONLY`**.  
Non patché en P70. Action P71 : `ADD_DRY_RUN_FLAG_AND_KX108_BOUNDARY`.

### 3. connectors/trading_live.py — CONNECTOR_DO_NOT_RUN ⚠️⚠️

`stream_to_kernel()` : `while True` + `ccxt.binance()` (EXTERNE) + `exchange.fetch_ticker("BTC/USDT")` + `requests.post(127.0.0.1:8000/trading, timeout=10)` + `time.sleep(2)`.  
Payload `irreversible=True`. **Aucun `dry_run_flag`**. **Aucune déclaration `KX108_ONLY`**.  
Boucle la plus rapide (2s). Seul connecteur avec sortie réseau **externe** (Binance).  
**CONNECTOR_DO_NOT_RUN** sans gate explicite. Action P71 : `CONNECTOR_DO_NOT_RUN_UNGUARDED_REQUIRES_DRY_RUN_AND_KX108`.

### 4. apps/obsidia_api/graphiti_v20_readonly_client.py — GRAPHITI_REVIEW — LOW ✓

`urllib.request.urlopen` GET vers `127.0.0.1:8011`. timeout=2.5s. Fallback `BACKEND_STUB` si indisponible.  
Tous write flags False : `graphiti_write=False`, `neo4j_write=False`.  
`KX108_ONLY=True`. **SAFE** — `CONNECTOR_DRY_RUN_SAFE`.

### 5. neo4j_brody_guide_bridge_readonly_v1.py — NEO4J_REVIEW — MEDIUM ✓ (P66)

`bolt://localhost:7688`. `NEO4J_PASSWORD` obligatoire, fail-closed (P66 patché).  
Double guard : `OBSIDIA_ALLOW_MANUAL_NEO4J_WRITE` + `KX108_MANUAL_REVIEW_GRAPH_WRITE_OK`.  
Neo4j write possible **uniquement** si les deux confirmations présentes. **OK état courant.**

### 6. periphery/ graphiti_import_apply_guarded_manual_only/ (x2) — GRAPHITI_REVIEW — MEDIUM

`graphiti_write=True` possible si gate levé. `QUARANTINE_FOR_SRL_PATH` depuis P66.  
Hors chemin SRL readonly. **OK état courant.**

### 7. sigma/connectors.py — NONE ✓

Descriptive-only. Constantes de routes relatives. Aucun `requests` import. Aucun appel réseau réel.  
`_CONNECTOR_BOUNDARY` avec all write flags False. **SAFE.**

### 8. sigma/graphiti_readonly_bridge.py — NONE ✓

Pure in-process. `graphiti_probe_mode=IN_PROCESS_ONLY`. Aucun `urllib`/`requests`.  
Génère candidate query uniquement. **SAFE.**

### 9. sigma/tools/run_bank_enterprise_pack.py — LOCALHOST_REVIEW — LOW ✓

`requests.get(127.0.0.1:8000/sigma/bank, timeout=30)`. Script tool one-shot.  
Non invoqué depuis l'API en runtime. Analyse sigma isolée. **OK TOOL_ONLY.**

### 10. proofs/distributed/aggregator.py — BLOCKED ✓

`urllib.request.urlopen` POST vers `node1:8000` … `node4:8000` (symbolic hostnames).  
Consensus distribué — proof uniquement. Jamais exécutable sans infrastructure spécifique.  
**BLOCKED — PROOF_ONLY.**

### 11. apps/obsidia_api/routes/worldcalls.py — NONE ✓

`Path.read_text()` sur `audit/world_action_bus.jsonl` local. `_BOUNDARY` avec `real_egress=False`, `dry_run_only=True`. **SAFE.**

### 12. Dettes préexistantes (inchangées)

| Fichier | Statut |
|---|---|
| `audit/world_action_bus.jsonl` | HASH_MISMATCH_PREEXISTING_P65 |
| `proofs/PROOFKIT_REPORT.json` | HASH_MISMATCH_PREEXISTING_P65 |
| `tests/test_invariants_against_engine.py` | ModuleNotFoundError: obsidia_os2 |
| `tests/sigma_stress_test.py` | ModuleNotFoundError: agents.obsidia_sigma_v130 |
| `tests/test_agents_functional.py` | ImportError: TradingState |
| `tests/test_consensus_inprocess.py` | ModuleNotFoundError: agents.run_pipeline |
| `tests/test_sigma_v18_9.py` | ModuleNotFoundError: agents.obsidia_sigma_v130 |

---

## 4. Matrice par surface

| Surface | Entrées réseau | Catégorie dominante | Risque |
|---|---:|---|---|
| `connectors` | 3 | CONNECTOR_ACTIVE_REVIEW / TRADING_REVIEW | HIGH |
| `apps/obsidia_api` | 2 | GRAPHITI_REVIEW / NONE | LOW–MEDIUM |
| `periphery` | 3 | GRAPHITI_REVIEW / NEO4J_REVIEW / TEST_ONLY | LOW–MEDIUM |
| `sigma` | 3 | NONE / LOCALHOST_REVIEW | NONE–LOW |
| `proofs` | 1 | BLOCKED | MEDIUM (proof only) |
| `runtime_wiring` | 1 | NONE | NONE — FROZEN_P56E |
| `.local_audits` | 1 | TEST_ONLY | NONE |
| `scripts` | 1 | LOCALHOST_REVIEW | LOW |

---

## 5. Décision

P70 ne corrige pas. P70 classe.

**Connecteurs actifs non guarded (action P71 obligatoire) :**
1. `connectors/aviation_robo.py` → `ADD_DRY_RUN_FLAG_AND_KX108_BOUNDARY_P71`
2. `connectors/bank_normal_flow.py` → `ADD_DRY_RUN_FLAG_AND_KX108_BOUNDARY_P71`
3. `connectors/trading_live.py` → `CONNECTOR_DO_NOT_RUN_UNGUARDED_REQUIRES_DRY_RUN_AND_KX108_P71`

**Connecteurs guarded (OK état courant) :**
- `graphiti_v20_readonly_client.py` — readonly, write flags False, fallback stub
- `neo4j_brody_guide_bridge_readonly_v1.py` — P66 fail-closed, double guard

**Aucune sortie réseau externe active détectée en runtime API** (hors trading_live non lancé).

**Prochain geste : P71 — Source Runtime & Source Packs Deep Audit.**

---

**Verdict :** `P70_NETWORK_EGRESS_CONNECTORS_AUDIT_READY`
