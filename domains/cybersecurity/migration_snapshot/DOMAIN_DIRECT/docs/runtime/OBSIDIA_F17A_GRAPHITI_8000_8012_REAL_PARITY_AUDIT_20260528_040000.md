# OBSIDIA F17A — GRAPHITI 8000 / 8011 / 8012 REAL PARITY AUDIT

CHECKPOINT: F17A_GRAPHITI_8000_8012_REAL_PARITY_AUDIT
MODE: READ_ONLY
Date: 2026-05-28 04:00 UTC

---

## BOUNDARY CHECK

```
KX108_ONLY=true
readonly=true
advisory_only=true
emits_act=false
emits_verdict=false
memory_write=false
graphiti_write=false
kernel_mutation=false
x108_mutation=false
execution_allowed=false
NO_BACKEND_TOUCH=true
NO_KERNEL_TOUCH=true
NO_COMMIT=true
NO_PATCH=true (audit only — F17A stops here)
```

---

## VERROU

```
HEAD commit : 2f6767e
Tag         : BRODY_F16B_REAL_LIVE_SOURCE_WIRING_20260528
Tree status : CLEAN (no uncommitted changes to audited files)
```

---

## SECTION A — ARCHITECTURE RÉELLE (CONFIRMÉE)

### Ports actifs

| Port | Service | Statut (probe socket) |
|---|---|---|
| 7688 | Neo4j Bolt | OPEN — Neo4j IS running |
| 8000 | Brody API (main runtime) | OPEN — confirmed by payload |
| 8011 | ObsidiaShell / Graphiti V20 frozen sidecar | OPEN — confirmed by probe |
| 8012 | Brody API (second instance, same stack as 8000) | OPEN — no Graphiti frozen routes |

### Rôles

- **8000** : `uvicorn apps.obsidia_api.main:app`. Brody chat (`/api/brody/chat`). Aussi proxy vers 8011 pour les routes `/api/graphiti/*`.
- **8011** : ObsidiaShell API Gateway. Graphiti V20 frozen (167 nodes, 477 rels, 20 episodes). `live_neo4j_dependency: false`. Sert `freeze_phase0_v20_20260506_140654`.
- **8012** : Deuxième instance Brody (même codebase que 8000, lancé sur port 8012). Aucune route Graphiti frozen. N'est pas le sidecar Graphiti.

---

## SECTION B — PAYLOAD 8000 BRODY CHAT (EXTRAIT CLÉ)

Fichier source : `docs/runtime/F17A_8000_BRODY_GRAPHITI_PAYLOAD.json`

```json
{
  "graphiti_status": "GRAPHITI_LIVE_BLOCKED",
  "graphiti_blocker": "NEO4J_PASSWORD not set",
  "neo4j_status": "LIVE_READONLY",
  "source": "REAL_BRODY_RUNTIME_NO_GRAPHITI",
  "memory_response_chain_snapshot": {
    "source_mode": "LOCAL_GRAPHITI_INDEX_FALLBACK",
    "neo4j_status": "NEO4J_PASSWORD_NOT_SET",
    "material_quality": "USABLE_MATERIAL"
  }
}
```

Interprétation critique :
- `neo4j_status: LIVE_READONLY` → `port_7688_open = True` (Neo4j tourne bien sur 7688)
- `graphiti_blocker: "NEO4J_PASSWORD not set"` → **seul** bloqueur
- `port_8011_open = True` — déduit du fait que le bloqueur ne mentionne pas 8011

---

## SECTION C — PROBE 8011 FROZEN ENDPOINTS (EXTRAIT CLÉ)

Fichier source : `docs/runtime/F17A_8011_GRAPHITI_V20_PROBE.json`

```json
{
  "title": "ObsidiaShell API Gateway — Graphiti Phase0 V20 memory graph access v1.1.0-graphiti-v20",
  "frozen_status": {
    "status": "FROZEN_READONLY",
    "node_count": 167,
    "relationship_count": 477,
    "episode_count": 20,
    "live_neo4j_dependency": false,
    "freeze_dir": "graphiti-lab/.graphiti_runs/freeze_phase0_v20_20260506_140654"
  },
  "frozen_context": {
    "graphiti_role": "READONLY_CONTEXT_PROVIDER",
    "live_neo4j_dependency": false
  }
}
```

8011 est pleinement fonctionnel. `live_neo4j_dependency: false` = aucun besoin de NEO4J_PASSWORD pour servir le contexte frozen.

---

## SECTION D — SOURCE CODE AUDIT

### Fichiers audités

| Fichier | Rôle clé |
|---|---|
| `apps/obsidia_api/brody_real_response_pipeline.py` | Pipeline principal du chat Brody — probe graphiti + fallbacks |
| `apps/obsidia_api/brody_full_runtime_orchestrator.py` | Orchestrateur alternatif (même logique de probe) |
| `apps/obsidia_api/brody_memory_response_chain_adapter.py` | Chaîne mémoire → LOCAL_GRAPHITI_INDEX_FALLBACK |
| `apps/obsidia_api/graphiti_v20_readonly_client.py` | Client HTTP readonly pour 8011 |
| `apps/obsidia_api/routes/graphiti.py` | Routes `/api/graphiti/*` — utilisent le client V20 |
| `apps/obsidia_api/routes/brody.py` | Route `/api/brody/chat` — orchestre toutes les couches |

---

### D1 — `_probe_graphiti()` dans `brody_real_response_pipeline.py` (lignes 32–50)

```python
def _probe_graphiti() -> dict[str, Any]:
    result = {"status": "GRAPHITI_LIVE_BLOCKED", ...}
    for port, key in [(7688, "port_7688_open"), (8011, "port_8011_open")]:
        try:
            s = socket.socket(); s.settimeout(1)
            s.connect(('127.0.0.1', port)); s.close()
            result[key] = True
        except: pass
    blockers = []
    if not os.environ.get("NEO4J_PASSWORD"): blockers.append("NEO4J_PASSWORD not set")
    if not result["port_7688_open"]: blockers.append("Neo4j port 7688 closed")
    if not result["port_8011_open"]: blockers.append("ObsidiaShell port 8011 closed")
    if not blockers:
        result["status"] = "GRAPHITI_LIVE_READONLY_PASS"
    else:
        result["blocker"] = " | ".join(blockers)
    return result
```

**Condition de PASS** : les trois conditions doivent être vraies simultanément :
1. `NEO4J_PASSWORD` env var set ← **manquant dans le processus 8000**
2. Port 7688 open ← TRUE (Neo4j tourne)
3. Port 8011 open ← TRUE (ObsidiaShell tourne)

Un seul bloqueur suffit pour obtenir `GRAPHITI_LIVE_BLOCKED`.

---

### D2 — `_neo4j_available()` dans `brody_memory_response_chain_adapter.py` (lignes 52–65)

```python
def _neo4j_available() -> tuple[bool, str]:
    password = os.environ.get("NEO4J_PASSWORD", "")
    if not password:
        return False, "NEO4J_PASSWORD_NOT_SET"
    try:
        s = socket.socket()
        s.settimeout(1.5)
        s.connect(("127.0.0.1", 7688))
        s.close()
        return True, "NEO4J_REACHABLE"
    except Exception:
        return False, "NEO4J_PORT_7688_CLOSED_OR_UNREACHABLE"
```

Même condition : si `NEO4J_PASSWORD` absent → `False` immédiat, sans même tester le port 7688.

---

### D3 — `build_memory_response_chain()` — cascade des fallbacks (lignes 403–606)

```
neo4j_ok = _neo4j_available()
│
├─ False (NEO4J_PASSWORD manquant)
│    └─ _load_local_graphiti_index()
│         └─ JSONL : _graphiti_readonly_indexes/
│              GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854/
│              graphiti_readonly_records_v2.jsonl
│         → 3267 items → _query_local_index() → scoring keyword
│         → source_mode: LOCAL_GRAPHITI_INDEX_FALLBACK
│         → material_quality: USABLE_MATERIAL (si match)
│
└─ True (NEO4J_PASSWORD set, port 7688 open)
     └─ query_mod.query_neo4j() via BrodyMemoryDoc
          ├─ results > 0 → hydrate → engine → REAL_BRODY_GRAPHITI_LIVE
          └─ results = 0 → Phase 12B fallback :
               _query_graphiti_frozen_http_ladder()
               → HTTP GET http://127.0.0.1:8011/graph/v20/frozen/context
               → source_mode: GRAPHITI_V20_FROZEN_HTTP_FALLBACK
```

**Gap critique** : Quand `NEO4J_PASSWORD` est absent, la chaîne va directement au JSONL local. Elle ne tente jamais `_query_graphiti_frozen_http_ladder()` vers 8011, même si 8011 est up et `live_neo4j_dependency: false`.

---

### D4 — Routes `/api/graphiti/*` vs chemin mémoire chat (routes/graphiti.py)

```python
# routes/graphiti.py — proxy vers 8011
from apps.obsidia_api.graphiti_v20_readonly_client import graphiti_v20_get

@router.get("/status")
async def graphiti_status():
    payload = graphiti_v20_get("/graph/v20/frozen/status")
    # → HTTP GET 127.0.0.1:8011 — aucun check NEO4J_PASSWORD
    # → retourne FROZEN_READONLY si 8011 up
```

La route `/api/graphiti/status` contourne entièrement `_neo4j_available()`. Elle interroge 8011 directement via HTTP. Résultat : **FROZEN_READONLY** même quand `NEO4J_PASSWORD` manque.

C'est le **disconnect** : status = frozen works, chat memory = blocked.

---

### D5 — `graphiti_v20_readonly_client.py` (client HTTP, lignes 40–67)

```python
def graphiti_v20_get(path: str, params=None, timeout=2.5) -> dict | None:
    base = os.getenv("GRAPHITI_V20_HTTP_BASE", "http://127.0.0.1:8011")
    # ... HTTP GET vers 8011
    # Aucun check NEO4J_PASSWORD
    # Envelope boundary: readonly=True, KX108_ONLY, graphiti_write=False
```

Ce client est **indépendant de NEO4J_PASSWORD**. Il fonctionne si 8011 répond. Déjà utilisé par `_query_graphiti_frozen_http_once()` dans le chain adapter (Phase 12B, neo4j=0 results).

---

## SECTION E — RÉPONSES AUX 8 QUESTIONS

**Q1. Pourquoi `graphiti_status = GRAPHITI_LIVE_BLOCKED` sur 8000 ?**

`_probe_graphiti()` exige trois conditions simultanées : NEO4J_PASSWORD set + port 7688 open + port 8011 open. Les deux ports sont ouverts. Seule `NEO4J_PASSWORD` est absente de l'environnement du processus Brody 8000. Un seul manquant → GRAPHITI_LIVE_BLOCKED.

---

**Q2. Pourquoi `source_mode = LOCAL_GRAPHITI_INDEX_FALLBACK` ?**

`build_memory_response_chain()` appelle `_neo4j_available()` qui retourne `False` dès que `NEO4J_PASSWORD` est vide, sans tester le port 7688. Le code saute immédiatement à `_load_local_graphiti_index()` → JSONL local 3267 items. Le fallback V20 frozen HTTP n'est pas tenté dans ce cas (il n'est déclenché que quand Neo4j est live mais retourne 0 résultats).

---

**Q3. Est-ce que 8011 et la V20 frozen sont accessibles depuis 8000 ?**

OUI. Port 8011 : open (confirmé par `port_8011_open: True` implicite dans le blocker qui ne mentionne que le password). Client HTTP `graphiti_v20_readonly_client.graphiti_v20_get()` fonctionne déjà (les routes `/api/graphiti/*` le prouvent). `_query_graphiti_frozen_http_once()` contacte `http://127.0.0.1:8011/graph/v20/frozen/context` et `…/search` — le code existe et est opérationnel.

---

**Q4. Qu'est-ce qui différencie le chemin status vs le chemin mémoire ?**

| | `/api/graphiti/status` | `build_memory_response_chain()` |
|---|---|---|
| Mécanisme | `graphiti_v20_get()` → HTTP 8011 | `_neo4j_available()` → env var check |
| Dépendance NEO4J_PASSWORD | Aucune | Bloqueur immédiat |
| Résultat actuel | FROZEN_READONLY ✓ | LOCAL_GRAPHITI_INDEX_FALLBACK |

La route status est un pur proxy HTTP. La chaîne mémoire a une branche Neo4j qui vérifie les credentials avant tout.

---

**Q5. Quelle est la vraie source de mémoire utilisée pour répondre à Brody ?**

`_graphiti_readonly_indexes/GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854/graphiti_readonly_records_v2.jsonl` — 3267 records. Scoring keyword simple (`_query_local_index()`). Les records incluent `text_excerpt` (extrait du preview Neo4j original). La chaîne hydrate→engine fonctionne sur ce dataset → `material_quality: USABLE_MATERIAL`.

---

**Q6. `material_quality = USABLE_MATERIAL` est-il fiable ?**

Fonctionnellement oui : les réponses Brody sont générées et cohérentes. Structurellement, ce n'est pas le même dataset que le V20 frozen (167 nodes / 477 rels / 20 episodes de graph structuré). Le JSONL local est un index plat avec scoring lexical — plus large (3267 items) mais moins curé. Qualité : adéquate pour le contexte advisory, pas identique au graph V20.

---

**Q7. Configuration minimale pour passer à `GRAPHITI_LIVE_READONLY_PASS` ?**

**Une seule variable d'environnement** dans le processus Brody 8000 :

```bash
NEO4J_PASSWORD=<mot_de_passe_neo4j>
```

Port 7688 ✓ déjà ouvert. Port 8011 ✓ déjà ouvert. Aucun changement de code requis. Si Neo4j tourne sans authentification, n'importe quelle valeur non-vide suffit (le check est `bool(os.environ.get("NEO4J_PASSWORD"))`).

---

**Q8. Changements de code pour utiliser 8011 comme source mémoire quand Neo4j est inaccessible ?**

Dans `brody_memory_response_chain_adapter.py`, fonction `build_memory_response_chain()`, après le check `if not neo4j_ok:`, ajouter une tentative V20 frozen HTTP AVANT `_load_local_graphiti_index()` :

```python
if not neo4j_ok:
    # Phase F17B proposition (NOT APPLIED HERE — audit only)
    # Try V20 frozen HTTP first (live_neo4j_dependency: false)
    graphiti_http_queries = [primary_q] + list(fallback_qs) + [query, user_message]
    graphiti_items, graphiti_effective_query, graphiti_attempts = _query_graphiti_frozen_http_ladder(
        graphiti_http_queries, limit=limit)
    if graphiti_items:
        # → source_mode: GRAPHITI_V20_FROZEN_HTTP_PRIMARY
        ...
    # Only then fall back to local JSONL
    records = _load_local_graphiti_index(workspace)
    ...
```

`_query_graphiti_frozen_http_ladder()` est déjà implémentée (Phase 12B). Elle contacte `http://127.0.0.1:8011/graph/v20/frozen/context` et `…/search`. Le code de normalisation des items est prêt. Aucune nouvelle dépendance requise.

---

## SECTION F — DIAGNOSTIC FINAL

### Cause racine

```
CAUSE_ROOT: NEO4J_PASSWORD not set dans l'environnement du processus Brody 8000
EFFET_DIRECT: _probe_graphiti() → GRAPHITI_LIVE_BLOCKED
EFFET_SECONDAIRE: build_memory_response_chain() → LOCAL_GRAPHITI_INDEX_FALLBACK
NOTE: Neo4j tourne (port 7688 open). ObsidiaShell tourne (port 8011 open).
      Le blocage est UNIQUEMENT une variable d'environnement manquante.
```

### Deux chemins disponibles pour corriger

| Option | Type | Effort | Résultat |
|---|---|---|---|
| **F17B-ENV** : Ajouter `NEO4J_PASSWORD` au process 8000 | Config | Minimal | GRAPHITI_LIVE_READONLY_PASS + Neo4j live chain |
| **F17B-CODE** : Utiliser 8011 frozen HTTP comme fallback primaire quand neo4j_ok=False | Code | 1 fichier modifié | GRAPHITI_V20_FROZEN_HTTP_PRIMARY sans Neo4j credentials |

Les deux options respectent les boundaries KX108_ONLY, readonly, no_graphiti_write.

### Résumé des statuts

| Couche | Statut actuel | Statut cible (F17B) |
|---|---|---|
| `graphiti_status` (probe) | GRAPHITI_LIVE_BLOCKED | GRAPHITI_LIVE_READONLY_PASS (si F17B-ENV) |
| Routes `/api/graphiti/*` | FROZEN_READONLY ✓ | Inchangé |
| `memory_response_chain_snapshot.source_mode` | LOCAL_GRAPHITI_INDEX_FALLBACK | GRAPHITI_V20_FROZEN_HTTP_PRIMARY (si F17B-CODE) ou Neo4j live |
| `material_quality` | USABLE_MATERIAL | USABLE_MATERIAL (maintenu) |
| Réponses Brody | Fonctionnelles | Fonctionnelles |

---

## SECTION G — FICHIERS PRODUITS PAR F17A

| Fichier | Rôle |
|---|---|
| `docs/runtime/F17A_8000_BRODY_GRAPHITI_PAYLOAD.json` | Payload complet d'une réponse Brody chat réelle (70 clés) |
| `docs/runtime/F17A_8011_GRAPHITI_V20_PROBE.json` | Probe complet de tous les endpoints 8011 |
| `docs/runtime/OBSIDIA_F17A_GRAPHITI_8000_8012_REAL_PARITY_AUDIT_20260528_040000.md` | Ce rapport |

---

## SECTION H — BOUNDARIES VÉRIFIÉES

```
GRAPHITI_WRITE=false (aucune écriture dans ce rapport)
MEMORY_WRITE=false
KERNEL_MUTATION=false
X108_MUTATION=false
EMITS_ACT=false
EMITS_VERDICT=false
NO_PATCH_APPLIED=true (audit only)
KX108_ONLY=true
```

---

```
F17A_AUDIT_COMPLETE=true
CAUSE_ROOT_IDENTIFIED=true (NEO4J_PASSWORD not set in 8000 process env)
8011_REACHABLE_FROM_8000=true (port open, client opérationnel)
V20_FROZEN_CODE_PATH_EXISTS=true (_query_graphiti_frozen_http_ladder already implemented)
PATCH_NOT_APPLIED=true (awaiting F17B user validation)
```
