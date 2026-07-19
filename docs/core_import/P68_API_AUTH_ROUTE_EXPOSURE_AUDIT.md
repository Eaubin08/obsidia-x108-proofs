# P68 — API Auth & Route Exposure Audit

**Audit ID :** P68  
**Statut :** `P68_API_AUTH_ROUTE_EXPOSURE_AUDIT_READY`  
**Mode :** `AUDIT_ONLY` — aucun patch, aucune modification de routes, aucun import  
**Branche :** `p68-api-auth-route-exposure-audit`  
**Date :** 2026-06-07

---

## 1. Verdict court

### Finding principal : quasi-absence d'auth

Sur **80 routes détectées** dans `apps/obsidia_api/routes/` (+ 3 connecteurs), **une seule route** possède une authentification réelle :

| Route | Auth | Verdict |
|---|---|---|
| `POST /api/brody/chat` | `require_api_key` (OBSIDIA_API_KEY) | AUTH_REQUIRED_DRY_RUN — OK |
| Toutes les autres (79) | AUCUNE | REVIEW REQUIS |

L'implémentation auth (`apps/obsidia_api/auth.py`) est correcte en elle-même :
- Lit `OBSIDIA_API_KEY` depuis l'env — fail-fermé (503 si vide, pas de bypass silencieux)
- Pattern `Depends(require_api_key)` FastAPI standard

Le problème : ce guard n'est appliqué qu'à une seule route.

### Répartition des catégories

| Catégorie | Nb routes | Risque |
|---|---:|---|
| `ACTION_RISK_REVIEW` | 23 | HIGH / MEDIUM |
| `MEMORY_GRAPHITI_REVIEW` | 14 | MEDIUM |
| `AUTH_REQUIRED_READONLY` | 9 | LOW (GET status) |
| `CONNECTOR_EGRESS_REVIEW` | 9 | MEDIUM |
| `STATUS_ONLY` | 7 | LOW |
| `UNKNOWN_REQUIRES_REVIEW` | 6 | MEDIUM |
| `SOURCE_EXPOSURE_REVIEW` | 4 | MEDIUM |
| `PUBLIC_MINIMAL_SAFE` | 3 | NONE |
| `WORKBENCH_ONLY` | 3 | LOW |
| `INTERNAL_ONLY` | 2 | MEDIUM |

### Règle cible (non appliquée ici — P68 AUDIT_ONLY)

```
PUBLIC_MINIMAL_SAFE : /, /api/health, /api/readiness, /api/status uniquement
Tout le reste        : auth_required=True OU internal_only=True OU debug_only=True
```

---

## 2. Modèle de catégories d'exposition

| Catégorie | Définition | Action future |
|---|---|---|
| `PUBLIC_MINIMAL_SAFE` | Routes statut publiques minimales. Aucun payload sensible. | OK |
| `AUTH_REQUIRED_DRY_RUN` | Nécessite auth — résultat DRY_RUN_ONLY. Actuellement: brody/chat. | OK |
| `AUTH_REQUIRED_READONLY` | Nécessite auth — lecture seule. | Ajouter auth — P69+ |
| `STATUS_ONLY` | Rapports Sigma / X108 status. GET uniquement, minimal. | Ajouter auth — P69+ |
| `INTERNAL_ONLY` | Réservé opérateur interne. Ex: freeze-dashboard (git introspection). | Ne pas exposer public |
| `WORKBENCH_ONLY` | DRY_RUN_ONLY déclaré. Ex: worldcalls. | Auth recommandée |
| `SOURCE_EXPOSURE_REVIEW` | Expose état runtime source (`runtime_allowed_now` présent). | Review P69 |
| `ACTION_RISK_REVIEW` | POST sans auth pouvant déclencher des actions. | AUTH OBLIGATOIRE — P69+ |
| `MEMORY_GRAPHITI_REVIEW` | Opérations mémoire / Graphiti. Certaines POST sans auth. | AUTH OBLIGATOIRE — P69+ |
| `CONNECTOR_EGRESS_REVIEW` | Connecteurs réseau actifs (requests.post). Env-driven. | Valider endpoint config |
| `UNKNOWN_REQUIRES_REVIEW` | POST sans auth inclassifiés. | Analyser + auth — P69+ |

---

## 3. Matrice route par route (sélection critique)

### Routes PUBLIC_MINIMAL_SAFE — OK

| Route | Méthode | Source |
|---|---|---|
| `/api/health` | GET | `status.py` |
| `/api/readiness` | GET | `status.py` |
| `/api/status` | GET | `status.py` |

### AUTH_REQUIRED_DRY_RUN — seule route protégée

| Route | Méthode | Auth | Source |
|---|---|---|---|
| `/api/brody/chat` | POST | `require_api_key` (OBSIDIA_API_KEY) | `brody.py` |

### ACTION_RISK_REVIEW — priorité P69

| Route | Méthode | Source | Raison |
|---|---|---|---|
| `/api/blockchain/policy/evaluate` | POST | `blockchain.py` | Évaluation politique sans auth |
| `/api/blockchain/signature/check` | POST | `blockchain.py` | Signature check sans auth |
| `/api/blockchain/wallet/gate` | POST | `blockchain.py` | Gate wallet sans auth |
| `/api/blockchain/gencoin/compute` | POST | `blockchain.py` | Gencoin compute sans auth |
| `/api/blockchain/world/gateway` | POST | `blockchain.py` | World gateway sans auth — HIGH |
| `/api/blockchain/world/bus-dispatch` | POST | `blockchain.py` | Bus dispatch sans auth — HIGH |
| `/api/blockchain/world/ticket-status` | POST | `blockchain.py` | Ticket status sans auth |
| `/api/x108/cognitive/shazam` | POST | `x108.py` | Cognitive op sans auth |
| `/api/x108/cognitive/dominant-trees` | POST | `x108.py` | Cognitive op sans auth |
| `/api/x108/math/lyapunov` | POST | `x108.py` | Math op sans auth |
| `/api/x108/math/pog` | POST | `x108.py` | Math op sans auth |
| `/api/x108/math/trust-path` | POST | `x108.py` | Trust path sans auth |
| `/api/x108/cognitive/regime-classify` | POST | `x108.py` | Régime classify sans auth |
| `/api/x108/oracle/freshness` | POST | `x108.py` | Oracle sans auth |
| `/api/x108/timeverse/sync` | POST | `x108.py` | Timeverse sync sans auth |
| `/api/periphery/pipeline/run` | POST | `periphery_ops.py` | Pipeline run sans auth |
| `/api/periphery/pipeline/data-gate` | POST | `periphery_ops.py` | Data gate sans auth |
| `/api/periphery/pipeline/provenance-gate` | POST | `periphery_ops.py` | Provenance gate sans auth |
| `/api/periphery/pipeline/eml-compression` | POST | `periphery_ops.py` | EML compression sans auth |
| `/api/periphery/pipeline/energy-thermo` | POST | `periphery_ops.py` | Energy thermo sans auth |
| `/api/periphery/pipeline/ocs-generation` | POST | `periphery_ops.py` | OCS génération sans auth |
| `/api/periphery/pipeline/operational-constance` | POST | `periphery_ops.py` | Opérationnel sans auth |
| `/api/periphery/pipeline/permission-economic` | POST | `periphery_ops.py` | Permission éco sans auth |

### MEMORY_GRAPHITI_REVIEW — priorité P69

| Route | Méthode | Source | Raison |
|---|---|---|---|
| `/api/x108/memory/candidates/append` | POST | `x108.py` | Memory append sans auth |
| `/api/x108/memory/replay/session` | POST | `x108.py` | Session replay sans auth |
| `/api/x108/memory/candidates/read` | GET | `x108.py` | Memory read sans auth |
| `/api/memory/candidate/from-message` | POST | `memory.py` | Candidat mémoire sans auth |
| `/api/memory` | GET | `memory.py` | Mémoire root sans auth |
| `/api/memory/status` | GET | `memory.py` | Mémoire status sans auth |
| `/api/memory/sources` | GET | `memory.py` | Sources mémoire sans auth |
| `/api/memory/candidates` | GET | `memory.py` | Candidats mémoire sans auth |
| `/api/graphiti/status` | GET | `graphiti.py` | Graphiti status sans auth |
| `/api/graphiti/context` | GET | `graphiti.py` | Graphiti context sans auth |
| `/api/graphiti/search` | GET | `graphiti.py` | Graphiti search sans auth |
| `/api/graphiti/metrics` | GET | `graphiti.py` | Graphiti metrics sans auth |
| `/api/graphiti/readiness` | GET | `graphiti.py` | Graphiti readiness sans auth |
| `/api/periphery/pipeline/memory-governor` | POST | `periphery_ops.py` | Memory governor sans auth |

### INTERNAL_ONLY — subprocess git

| Route | Méthode | Source | Raison |
|---|---|---|---|
| `/api/runtime/freeze-dashboard` | GET | `runtime_freeze.py` | subprocess.run(["git", ...]) — read-only |
| `/api/runtime/freeze-dashboard/summary` | GET | `runtime_freeze.py` | idem |

### SOURCE_EXPOSURE_REVIEW — runtime_allowed_now déclaré

| Route | Source | Raison |
|---|---|---|
| `GET /api/runtime-wiring/os-map/status` | `os_map.py` | `runtime_allowed_now` dans boundary (False) |
| `POST /api/runtime-wiring/os-map/query` | `os_map.py` | idem |
| `GET /api/runtime-wiring/source-runtime/status` | `source_runtime_status.py` | `runtime_allowed_now` dans boundary (False) |
| `POST /api/runtime-wiring/source-runtime/preview` | `source_runtime_status.py` | idem |

### CONNECTOR_EGRESS_REVIEW — réseau actif

| Fichier | Tech | Raison |
|---|---|---|
| `connectors/aviation_robo.py` | `requests.post()` | Egress vers URL configurable |
| `connectors/bank_normal_flow.py` | `requests.post()` | Egress vers URL configurable |
| `connectors/trading_live.py` | `requests.post()` + `ccxt` | Egress + exchange library |
| `POST /api/periphery/monitoring/adapters/bank` | route | Bridge vers bank connector |
| `POST /api/periphery/monitoring/adapters/gps` | route | Bridge vers aviation connector |
| `POST /api/periphery/monitoring/adapters/trading` | route | Bridge vers trading connector |

---

## 4. Findings critiques

### Auth quasi-absente

L'architecture FastAPI avec `Depends(require_api_key)` est correcte mais sous-utilisée.
Le pattern existe, il suffit de l'étendre.

**Auth correcte (P67 vérifiée) :**
- `OBSIDIA_API_KEY` env var obligatoire — 503 si vide (fail-fermé)
- Pas de bypass silencieux
- Pattern propre `Depends(require_api_key)`

**Auth absente sur 79/80 routes.**

### subprocess dans runtime_freeze.py

`subprocess.run(["git", *args])` — introspection git read-only.  
Pas dangereux en soi, mais la route ne doit pas être exposée publiquement.
Catégorie `INTERNAL_ONLY` — accès opérateur seulement.

### runtime_allowed_now dans os_map.py et source_runtime_status.py

Ces fichiers déclarent `runtime_allowed_now = False` dans leurs boundary dicts (comme variable de statut dans la réponse), pas comme flag d'activation. Cohérent avec P56E freeze. Review pour s'assurer que le client ne peut pas forcer `runtime_allowed_now=True` via payload.

### Connecteurs réseau actifs (fonctionnel, non anormal)

`connectors/` : `requests.post()` vers URLs env-driven. Fonctionnel.  
Review requis : s'assurer que `AVIATION_URL`, `BANK_URL`, `TRADING_URL` ne peuvent pas être injectées via payload de route.

### Dettes préexistantes (inchangées)

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

## 5. Ce que P68 ne fait pas

| Interdit P68 | Raison |
|---|---|
| Patcher les routes | AUDIT_ONLY |
| Ajouter `require_api_key` aux routes | Correction future P69+ |
| Modifier `apps/obsidia_api/auth.py` | AUDIT_ONLY |
| Modifier sigma/ | Protection permanente |
| Modifier runtime_wiring/ | Gel P56E |
| Modifier periphery/ SRL | Gel P66 |
| Activer ACT | Interdit |
| Activer memory_write | Interdit |
| Activer graphiti_write | Interdit |
| X108 merge | Interdit |

---

## 6. Décision

P68 ne corrige pas. P68 classe et documente.

L'audit révèle que l'**infrastructure auth existe et est correcte** (fail-fermé, pas de bypass),
mais qu'elle n'est appliquée qu'à **1 route sur 80**.

Les routes prioritaires à sécuriser dans les paliers futurs :
1. `ACTION_RISK_REVIEW` (23 routes) — POST sans auth — **priorité maximale**
2. `MEMORY_GRAPHITI_REVIEW` (14 routes) — accès mémoire/Graphiti sans auth
3. `SOURCE_EXPOSURE_REVIEW` (4 routes) — exposition état runtime
4. `INTERNAL_ONLY` (2 routes) — subprocess git — ne pas exposer public

**Prochain geste : P69 — Filesystem & Path Exposure Audit.**

---

**Verdict :** `P68_API_AUTH_ROUTE_EXPOSURE_AUDIT_READY`
