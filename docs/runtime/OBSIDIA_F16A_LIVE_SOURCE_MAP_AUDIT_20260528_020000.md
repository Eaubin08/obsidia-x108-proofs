# OBSIDIA F16A — LIVE SOURCE MAP AUDIT

Date: 2026-05-28
Phase: F16A_LIVE_SOURCE_MAP_AUDIT
Status: READ_ONLY — STOP BEFORE PATCH

---

## BOUNDARY

```
MODE         = READ_ONLY
NO_PATCH     = true
KX108_ONLY   = true
ADVISORY_ONLY= true
```

---

## A. GIT

```
git log -1 --oneline : 653a4c7 feat: freeze F15C strict live surface repair
git tag              : BRODY_F15C_LIVE_SURFACE_STRICT_REPAIR_20260528
branch               : main
```

---

## B. PAYLOAD LIVE

```
docs/runtime/F16A_LIVE_PAYLOAD_8000.json
Query: "write Graphiti memory + canon -> DOMAIN_RACCORD_WRITE_BOUNDARY"
70 top-level keys
```

---

## C. ENDPOINTS — STATUTS

| Endpoint | Status | Contenu |
|---|---|---|
| `/api/os3/tickets` | 200 | `tickets: []` — stub vide |
| `/api/worldcalls` | 200 | `calls: []` — stub vide, `dry_run_only: true` |
| `/api/worldcalls/sovereign-tickets` | 200 | `tickets: []` — stub vide |
| `/api/memory/candidates` | 200 | `candidates: [1 item]`, `total: 1` |
| `/api/gencoin` | 200 | `entries: []` — vide, `is_real_token: false` |
| `/api/audit/events` | 200 | `events: []` — stub vide |
| `/api/graphiti/status` | 200 | `graphiti_status: FROZEN_READONLY`, `entity_count: 167`, `relation_count: 477` |

---

## D. SOURCES REPO — REGISTRES RÉELS DÉCOUVERTS

| Fichier | Contenu | Utilisable |
|---|---|---|
| `audit/world_action_bus.jsonl` | **191 events réels** — event_id, action_id, world_call_class, intent, domain, blocked, timestamp | OUI — source principale audit + worldcall |
| `audit/sovereign_tickets.jsonl` | **6 tickets réels** — ticket_id, action_id, os3_ticket_id, scope, x108_gate, autonomy_level, hash | OUI — source principale sovereign tickets |
| `audit/gencoin_ledger.jsonl` | **N'EXISTE PAS** — fichier absent | NON |
| `docs/runtime/*.md` | **87 rapports freeze/proof réels** — F1 → F15C + Phases 7-12 | OUI — source OS3 proof artifacts |
| `_local_audits/memory_candidate_ledger.jsonl` | Ledger candidats mémoire (référencé dans code) | OUI (via runtime) |

---

## E. RECADRAGE POLITIQUE — PRIORITÉ DES SOURCES

```
1. USE_EXISTING_RUNTIME_PACKET        — packet / snapshot Brody 8000
2. USE_EXISTING_SNAPSHOT              — snapshot runtime disponible
3. USE_EXISTING_REPORT_OR_MANIFEST    — freeze report / manifest / git tag réel
4. USE_EXISTING_REGISTRY              — registre fichier réel dans repo
5. CREATE_READONLY_VIEW_OVER_REAL_SOURCE — vue readonly sur source réelle
6. CREATE_LIVE_EMPTY_REGISTRY         — DERNIER RECOURS SEULEMENT si aucune source n'existe
```

```
INTERDIT : mock comme source runtime, faux tickets, faux events, hardcode décoratif
AUTORISÉ : 0 entrées réelles = donnée réelle honnête
```

---

## F. CARTE DES SOURCES PAR BLOC

---

### 1. DOMINANT TREES (ContextTab)

| Champ | Valeur |
|---|---|
| Mock source actuelle | `MOCK_CONTEXT_PACKET.dominant_trees = [0,7,11,27,28,29]` |
| Payload live | ✅ `tree_signal_packet.dominant_trees.dominant_ids` + `.dominant_names` |
| Endpoint live | — (pas d'endpoint dédié) |
| Fichier repo | — |
| Rapport/freeze | — |

**Action : USE_EXISTING_RUNTIME_PACKET**

Plan F16B :
- RightPanel ContextTab lit `live.tree_signal_packet` depuis prop
- Affiche `dominant_ids` avec `dominant_names` (ex. `ARBRE_23__Arbre_du_Temps`)
- Affiche `tree_count` (34 arbres)
- Fallback : `NO_TREE_SIGNAL_PACKET_IN_PAYLOAD`
- Supprimer `StaticDemoSection label="Dominant Trees"` (remplacé par bloc live)

---

### 2. GRAPHITI STATUS (MemoryTab)

| Champ | Valeur |
|---|---|
| Mock source actuelle | hardcodé `"READONLY BRIDGE"`, `false`, `false`, `"KX108_ONLY"` |
| Payload live | ✅ `graphiti_status = 'GRAPHITI_LIVE_BLOCKED'` + `neo4j_status = 'LIVE_READONLY'` + `graphiti_blocker` |
| Endpoint live | ✅ `/api/graphiti/status` → `FROZEN_READONLY`, `entity_count: 167`, `relation_count: 477` |
| Fichier repo | — |

**Action : USE_EXISTING_RUNTIME_PACKET (primaire) + USE_EXISTING_ENDPOINT (complémentaire)**

Note : Deux statuts vrais de perspectives différentes :
- Payload = Brody runtime → `GRAPHITI_LIVE_BLOCKED` (NEO4J_PASSWORD not set)
- Endpoint = freeze graph → `FROZEN_READONLY` (167 entités, 477 relations)
Afficher les deux avec leurs sources respectives.

Plan F16B :
- MemoryTab accepte `live?: Record<string,unknown>` prop
- Lit `live.graphiti_status`, `live.neo4j_status`, `live.graphiti_blocker` depuis payload
- Peut aussi afficher endpoint status séparément (appel `getGraphitiStatus()`)
- Supprimer `StaticDemoSection label="Memory Candidates / Graphiti Status"` (remplacé)

---

### 3. MEMORY CANDIDATES (MemoryTab)

| Champ | Valeur |
|---|---|
| Mock source actuelle | `MOCK_MEMORY_CANDIDATES` (4 candidats fictifs) |
| Payload live | ✅ `candidate_memory_snapshot.latest_candidates` (3 premiers / 85 total) |
| Endpoint live | ✅ `/api/memory/candidates` → 1 entrée réelle |
| Fichier repo | ✅ `_local_audits/memory_candidate_ledger.jsonl` (via runtime) |

**Action : USE_EXISTING_RUNTIME_PACKET**

Note : Payload `candidate_memory_snapshot` est plus riche (85 total, 3 premiers exposés) que l'endpoint (1 entrée synthétique). Payload = source principale.

Plan F16B :
- MemoryTab lit `live.candidate_memory_snapshot.latest_candidates`
- Affiche `candidate_ledger_count` comme compteur total
- Fallback : `NO_CANDIDATE_MEMORY_SNAPSHOT_IN_PAYLOAD`

---

### 4. GENCOIN SHADOW (GencoinTab)

| Champ | Valeur |
|---|---|
| Mock source actuelle | `MOCK_GENCOIN` (shadow + ledger fictifs) |
| Payload live | ✅ `gencoin_shadow_packet` — mode=`SHADOW_READONLY`, `usable_shadow_value=false`, scores=null, reason |
| Endpoint live | ✅ `/api/gencoin` → `entries: []`, `is_real_token: false` |
| Fichier repo | ❌ `audit/gencoin_ledger.jsonl` — ABSENT |
| Note calibration | Shadow scores null — non calibré. C'est la vérité système actuelle. |

**Action : USE_EXISTING_RUNTIME_PACKET (shadow) + CREATE_LIVE_EMPTY_REGISTRY (ledger)**

Justification LIVE_EMPTY_REGISTRY pour ledger : `audit/gencoin_ledger.jsonl` absent, `read_ledger()` retourne `[]`, aucune entrée métier réelle. Le rapport explique l'absence.

Plan F16B :
- GencoinTab accepte `live?: Record<string,unknown>` prop
- Affiche `gencoin_shadow_packet` : mode, usable_shadow_value, reason, shadow_scores
- Pour ledger : `LIVE_EMPTY_REGISTRY — entries=0 — gencoin_ledger.jsonl absent`
- Supprimer `StaticDemoSection label="Ledger Entries"` (remplacé)

---

### 5. AUDIT EVENTS (AuditTab)

| Champ | Valeur |
|---|---|
| Mock source actuelle | `MOCK_AUDIT` (6 events fictifs) |
| Payload live | ✅ `audit_event` — 1 event réel par réponse Brody |
| Endpoint live | ✅ `/api/audit/events` → 0 events (stub) |
| Fichier repo | ✅ `audit/world_action_bus.jsonl` — **191 events réels** |

**Action : USE_EXISTING_RUNTIME_PACKET (payload event) + CREATE_READONLY_VIEW_OVER_REAL_SOURCE (world_action_bus)**

Note : `audit/world_action_bus.jsonl` contient les vrais événements de bus avec `event_id`, `action_id`, `world_call_class`, `intent`, `domain`, `dry_run_only`, `blocked`, `timestamp`. C'est une source réelle — l'endpoint `/api/audit/events` doit la servir.

Plan F16B backend :
- `routes/audit.py` : lire `audit/world_action_bus.jsonl` et retourner les N derniers events
- Champs : `event_id`, `action_id`, `world_call_class`, `intent`, `domain`, `blocked`, `timestamp`
- `source: "audit/world_action_bus.jsonl"`, `readonly: true`, `decision_authority: "KX108_ONLY"`

Plan F16C UI :
- AuditTab affiche `live.audit_event` (payload, 1 event par réponse)
- AuditTab affiche aussi les events du bus via endpoint (191 réels)
- Supprimer `StaticDemoSection label="Audit Events"` (remplacé)

---

### 6. OS3 PROOF TICKET (GovernanceTab)

| Champ | Valeur |
|---|---|
| Mock source actuelle | `MOCK_OS3_TICKET` (merkle_hash fictif, lean_ref fictif) |
| Payload live | ❌ Pas de champ `os3_ticket` dans le payload Brody |
| Endpoint live | ✅ `/api/os3/tickets` → 0 tickets (stub) |
| Fichier repo | ✅ **87 rapports freeze/proof réels** dans `docs/runtime/` (F1→F15C, Phases 7-12) |
| Git tags | ✅ `BRODY_F15C_LIVE_SURFACE_STRICT_REPAIR_20260528` et autres |

**Action : USE_EXISTING_REPORT_OR_MANIFEST**

Note : Les rapports freeze de `docs/runtime/` sont les vrais artifacts de preuve de la machination Obsidia. Ce sont des documents structurés attestant l'état du système à chaque phase. Ils constituent la source légitime pour le bloc OS3 Proof, même sans ticket OS3 formel en base.

Plan F16B backend :
- `routes/os3.py` : lister les rapports de `docs/runtime/*.md` (glob) comme proof artifacts
- Retourner : `source: "docs/runtime/"`, `artifact_count: N`, `latest: <nom du dernier rapport>`, `type: "FREEZE_REPORT"`, `readonly: true`, `decision_authority: "KX108_ONLY"`
- NE PAS fabriquer de merkle_hash, de lean_ref fictif

Plan F16C UI :
- GovernanceTab affiche les vrais freeze reports comme proof artifacts
- Affiche nom, date, phase pour les N derniers
- Supprimer `MOCK_OS3_TICKET`

---

### 7. SOVEREIGN TICKET (GovernanceTab)

| Champ | Valeur |
|---|---|
| Mock source actuelle | `MOCK_SOVEREIGN_TICKET` (fictif) |
| Payload live | ❌ Pas de champ `sovereign_ticket` dans le payload Brody |
| Endpoint live | ✅ `/api/worldcalls/sovereign-tickets` → 0 (stub) |
| Fichier repo | ✅ `audit/sovereign_tickets.jsonl` — **6 tickets réels** |

**Action : CREATE_READONLY_VIEW_OVER_REAL_SOURCE**

Tickets réels disponibles :
```json
ticket_id, action_id, os3_ticket_id, scope, x108_gate (ALLOW/HOLD), autonomy_level, dry_run_only, world_call_class, hash
```

Plan F16B backend :
- `routes/worldcalls.py` : lire `audit/sovereign_tickets.jsonl` pour `/api/worldcalls/sovereign-tickets`
- Retourner les tickets réels avec `source: "audit/sovereign_tickets.jsonl"`, `readonly: true`, `decision_authority: "KX108_ONLY"`

Plan F16C UI :
- GovernanceTab affiche tickets réels (ticket_id, x108_gate, world_call_class)
- Supprimer `MOCK_SOVEREIGN_TICKET`

---

### 8. WORLDCALL / GATEWAY (GovernanceTab)

| Champ | Valeur |
|---|---|
| Mock source actuelle | `MOCK_WORLD_CALLS` (fictif) |
| Payload live | ❌ Pas de champ worldcall dans le payload Brody |
| Endpoint live | ✅ `/api/worldcalls` → 0 calls (stub) |
| Fichier repo | ✅ `audit/world_action_bus.jsonl` — **191 events réels** |

**Action : CREATE_READONLY_VIEW_OVER_REAL_SOURCE**

Events réels disponibles :
```json
event_id, action_id, sovereign_ticket_id, world_call_class, action_risk_class, intent, domain, dry_run_only, blocked, block_reason, timestamp
```

Plan F16B backend :
- `routes/worldcalls.py` : lire `audit/world_action_bus.jsonl` pour `/api/worldcalls`
- Retourner les N derniers events avec `source: "audit/world_action_bus.jsonl"`, `readonly: true`, `decision_authority: "KX108_ONLY"`, `dry_run_only: true`

Plan F16C UI :
- GovernanceTab affiche calls réels (action_id, intent, world_call_class, domain, blocked)
- Supprimer `MOCK_WORLD_CALLS`

---

### 9. CONTEXT PACKET (ContextTab)

| Champ | Valeur |
|---|---|
| Mock source actuelle | `cp_a1b2c3d4` statique — supprimé en F15B |
| Payload live | ✅ `context_packet` — packet_id live (`cp_brody_real_...`) |

**Action : USE_EXISTING_RUNTIME_PACKET — DÉJÀ RÉALISÉ EN F15B**

Aucune action F16 nécessaire pour ce bloc.

---

## G. RÉSUMÉ DES ACTIONS — RECADRAGE INTÉGRÉ

| Bloc | Source live disponible | Action F16B/C |
|---|---|---|
| Dominant Trees | `tree_signal_packet` (payload) | **USE_EXISTING_RUNTIME_PACKET** |
| Graphiti Status | `graphiti_status` (payload) + `/api/graphiti/status` | **USE_EXISTING_RUNTIME_PACKET + ENDPOINT** |
| Memory Candidates | `candidate_memory_snapshot` (payload) | **USE_EXISTING_RUNTIME_PACKET** |
| Gencoin Shadow | `gencoin_shadow_packet` (payload) | **USE_EXISTING_RUNTIME_PACKET** |
| Gencoin Ledger | `audit/gencoin_ledger.jsonl` ABSENT | **CREATE_LIVE_EMPTY_REGISTRY** (dernier recours justifié) |
| Audit Events | `audit_event` (payload) + `audit/world_action_bus.jsonl` (191 events) | **USE_EXISTING_RUNTIME_PACKET + CREATE_READONLY_VIEW** |
| OS3 Proof Ticket | `docs/runtime/` 87 rapports freeze réels | **USE_EXISTING_REPORT_OR_MANIFEST** |
| Sovereign Ticket | `audit/sovereign_tickets.jsonl` (6 tickets réels) | **CREATE_READONLY_VIEW_OVER_REAL_SOURCE** |
| WorldCall / Gateway | `audit/world_action_bus.jsonl` (191 events réels) | **CREATE_READONLY_VIEW_OVER_REAL_SOURCE** |
| Context Packet | payload (déjà réalisé F15B) | DONE |

**Pas de HIDE_NO_LIVE_SOURCE.**
**LIVE_EMPTY_REGISTRY limité à gencoin ledger uniquement (source réelle absente, justification documentée).**

---

## H. PROPS NÉCESSAIRES POUR F16C (UI)

```
MemoryTab  → live?: Record<string,unknown>  (graphiti_status, neo4j_status, graphiti_blocker, candidate_memory_snapshot)
GencoinTab → live?: Record<string,unknown>  (gencoin_shadow_packet)
AuditTab   → live?: Record<string,unknown>  (audit_event)
ContextTab → live?: Record<string,unknown>  (tree_signal_packet — déjà prop?)
GovernanceTab → pas de payload champ; lit via endpoints /api/os3, /api/worldcalls, /api/worldcalls/sovereign-tickets
```

`App.tsx → RightPanel` : `lastBackendPayload` déjà passé en prop. RightPanel doit transmettre vers MemoryTab / GencoinTab / AuditTab / ContextTab.

---

## I. BUGS À CORRIGER (hors scope F16 UI)

1. `getAuditEvents()` dans `obsidiaClient.ts` appelle `/v1/audit/chain` — chemin incorrect → `/api/audit/events`
2. `ENGINE_BASE` default = `http://127.0.0.1:8012` — devrait être 8000

---

## STOP — EN ATTENTE VALIDATION F16A

```
F16A_READ_ONLY_COMPLETE=true
NO_PATCH_APPLIED=true
LIVE_SOURCES_MAPPED=true
RECADRAGE_INTEGRE=true
LIVE_EMPTY_REGISTRY_JUSTIFIED_FOR_GENCOIN_LEDGER_ONLY=true
AWAITING_USER_VALIDATION=true
```
