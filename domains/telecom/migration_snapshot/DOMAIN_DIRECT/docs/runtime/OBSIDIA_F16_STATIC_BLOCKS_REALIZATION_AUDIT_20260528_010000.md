# OBSIDIA F16 — STATIC BLOCKS REALIZATION AUDIT

Date: 2026-05-28
Phase: F16_REALIZE_STATIC_BLOCKS_FROM_LIVE_PAYLOAD
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
branch               : main...origin/main
```

---

## B. PAYLOAD LIVE SAUVEGARDÉ

```
docs/runtime/F16_LIVE_PAYLOAD_8000.json
Query: "write Graphiti memory + canon -> DOMAIN_RACCORD_WRITE_BOUNDARY"
70 top-level keys
```

---

## C. ENDPOINT AUDIT — TOUS LES ENDPOINTS RÉPONDENT 200

| Endpoint | Status | Contenu clé |
|---|---|---|
| `/api/os3/tickets` | 200 | `tickets: []` — vide |
| `/api/worldcalls` | 200 | `calls: []` — vide, `dry_run_only: true` |
| `/api/worldcalls/sovereign-tickets` | 200 | `tickets: []` — vide |
| `/api/memory/candidates` | 200 | `candidates: [1 item]`, `total: 1` |
| `/api/gencoin` | 200 | `entries: []` — vide, `is_real_token: false` |
| `/api/audit/events` | 200 | `events: []` — vide, `total: 0` |
| `/api/graphiti/status` | 200 | `graphiti_status: FROZEN_READONLY`, `entity_count: 167`, `relation_count: 477` |

---

## D. SOURCE AUDIT — OBSIDIACLIENT.TS

**Constat critique** : `obsidiaClient.ts` a **déjà implémenté** toutes les fonctions client live.
`RightPanel.tsx` ne les appelle **PAS** — il importe `MOCK_*` directement depuis `mockData.ts`.

| Fonction client | Endpoint appelé | Status |
|---|---|---|
| `getOS3Ticket()` | `/api/os3/tickets` | Existe, endpoint vide |
| `getSovereignTickets()` | `/api/worldcalls/sovereign-tickets` | Existe, endpoint vide |
| `getWorldCalls()` | `/api/worldcalls` | Existe, endpoint vide |
| `getMemoryCandidates()` | `/api/memory/candidates` | Existe, 1 candidat live |
| `getGencoinLedger()` | `/api/gencoin` | Existe, entries vide |
| `getAuditEvents()` | `/v1/audit/chain` | **CHEMIN INCORRECT** — devrait être `/api/audit/events` |

**Autre constat** : `ENGINE_BASE` defaults to `http://127.0.0.1:8012` dans obsidiaClient.ts.
Les env vars VITE_ENGINE_API_BASE / VITE_BRODY_API_URL doivent être définies pour pointer vers 8000.
Le comportement actuel fonctionne grâce aux env vars locales — le défaut code est incorrect.

**App.tsx** : passe `lastBackendPayload` à `RightPanel` — payload disponible en prop.

---

## E. ANALYSE PAR BLOC — ACTION RECOMMANDÉE

---

### 1. DOMINANT TREES

**Source mock actuelle** : `MOCK_CONTEXT_PACKET.dominant_trees = [0, 7, 11, 27, 28, 29]` (IDs statiques)

**Source live disponible** : **OUI**
- `payload.tree_signal_packet.dominant_trees.dominant_ids = [23, 24, 25]`
- `payload.tree_signal_packet.dominant_trees.dominant_names = ['ARBRE_23__Arbre_du_Temps', 'ARBRE_24__Arbre_de_la_Memoire', 'ARBRE_25__Arbre_de_l_Histoire']`
- `payload.tree_signal_packet.tree_count = 34`
- Champ payload exact : `tree_signal_packet.dominant_trees.dominant_ids` + `.dominant_names`

**Action recommandée** : `REALIZE_FROM_PAYLOAD`

**Plan** :
- Lire `live.tree_signal_packet` dans ContextTab
- Afficher `dominant_trees.dominant_ids` avec `dominant_names`
- Si `tree_signal_packet` absent : afficher `NO_LIVE_DOMINANT_TREES_IN_PAYLOAD`
- Supprimer référence à `MOCK_CONTEXT_PACKET.dominant_trees`

---

### 2. GRAPHITI STATUS (MemoryTab)

**Source mock actuelle** : static `"READONLY BRIDGE"` hardcodé dans MemoryTab

**Source live disponible** : **OUI — déjà dans payload**
- `payload.graphiti_status = 'GRAPHITI_LIVE_BLOCKED'`
- `payload.neo4j_status = 'LIVE_READONLY'`
- `payload.graphiti_blocker = 'NEO4J_PASSWORD not set'`
- Endpoint live : `/api/graphiti/status` → `graphiti_status: FROZEN_READONLY`, `entity_count: 167`, `relation_count: 477`

**Note** : Deux statuses différents — payload = runtime Brody (BLOCKED), endpoint = freeze graph (FROZEN_READONLY). Les deux sont vrais, de perspectives différentes.

**Champ payload exact** : `live.graphiti_status`, `live.neo4j_status`, `live.graphiti_blocker`

**Action recommandée** : `REALIZE_FROM_PAYLOAD`

**Plan** :
- Dans MemoryTab, lire `graphiti_status`/`neo4j_status`/`graphiti_blocker` du payload passé en prop
- MemoryTab doit accepter `live?: Record<string,unknown>` prop (comme ContextTab et AuditTab)
- Supprimer les valeurs hardcodées `"READONLY BRIDGE"`, `false`, `false`, `"KX108_ONLY"`

---

### 3. MEMORY CANDIDATES (MemoryTab)

**Source mock actuelle** : `MOCK_MEMORY_CANDIDATES` (4 candidats statiques fictifs)

**Source live disponible** : **OUI — dans payload ET endpoint**

**Payload** : `payload.candidate_memory_snapshot.latest_candidates` — 3 candidats réels (total: 85)
```
candidate_id: 7bd6bdde...  status: CANDIDATE_ONLY  content_summary: 'User queried balance...'
```

**Endpoint** : `/api/memory/candidates` → 1 candidat (`status: CANDIDATE_ONLY, content_summary: 'API memory query'`)

**Note** : Les candidats du payload (`candidate_memory_snapshot.latest_candidates`) sont plus riches (85 au total, 3 premiers fournis). L'endpoint retourne seulement 1 entrée API-level.

**Champ payload exact** : `live.candidate_memory_snapshot.latest_candidates` (array) + `candidate_ledger_count`

**Action recommandée** : `REALIZE_FROM_PAYLOAD`

**Plan** :
- Dans MemoryTab, utiliser `live.candidate_memory_snapshot` passé en prop
- Afficher `latest_candidates` (les N premiers, avec status, content_summary)
- Afficher `candidate_ledger_count` comme compteur total
- Si `candidate_memory_snapshot` absent : afficher `NO_LIVE_MEMORY_CANDIDATE_LIST_IN_PAYLOAD`
- Supprimer `MOCK_MEMORY_CANDIDATES`

---

### 4. GENCOIN (GencoinTab)

**Source mock actuelle** : `MOCK_GENCOIN` (entrées de ledger fictives)

**Source live disponible** :

**Pour le ledger** : **NON** — `/api/gencoin` → `entries: []`, 0 entrées
**Pour le shadow packet** : **OUI** — `payload.gencoin_shadow_packet`
```
version: GENCOIN_SHADOW_VALUE_PACKET_V1
mode: SHADOW_READONLY
usable_shadow_value: false  (scores null — pas encore calibré)
shadow_scores: cognitive_value=null, proof_value=null...
reason: GENCOIN_SHADOW_NOT_USABLE_SIGMA_NOT_USABLE_FOR_GENCOIN...
```

**Note** : Aucun ledger live. Le `gencoin_shadow_packet` est réel mais ses scores sont null (non calibrés). C'est la vérité actuelle du système.

**Champ payload exact** : `live.gencoin_shadow_packet` (mode, usable_shadow_value, shadow_scores, reason)

**Action recommandée** : `REALIZE_FROM_PAYLOAD` pour shadow packet + `HIDE_NO_LIVE_SOURCE` pour ledger

**Plan** :
- Afficher `gencoin_shadow_packet` : mode, usable_shadow_value, reason
- Pour ledger : afficher `NO_LIVE_GENCOIN_LEDGER_IN_PAYLOAD — entries=0`
- Supprimer `MOCK_GENCOIN.map()`

---

### 5. AUDIT EVENTS (AuditTab)

**Source mock actuelle** : `MOCK_AUDIT` (6 events statiques fictifs)

**Source live disponible** :

**Payload** : `payload.audit_event` — **1 event par réponse**
```
event_id: audit_brody_real_e9466dd328f2
type: brody_real_response
description: write Graphiti memory + canon -> DOMAIN_RACCORD_WRITE_BOUNDARY
result: OK
timestamp: 2026-05-27T23:06:51.328067+00:00
```

**Endpoint** : `/api/audit/events` → `events: [], total: 0`

**Note** : Le payload donne 1 audit event live par réponse Brody. L'endpoint est vide (pas d'historique persisté côté backend). `getAuditEvents()` dans obsidiaClient appelle `/v1/audit/chain` — **chemin incorrect** (bug existant, hors scope F16 UI).

**Champ payload exact** : `live.audit_event` (single object per response)

**Action recommandée** : `REALIZE_FROM_PAYLOAD`

**Plan** :
- Afficher `live.audit_event` si présent (single live event per Brody response)
- Supprimer `MOCK_AUDIT.map()`
- Si `audit_event` absent : `NO_LIVE_AUDIT_EVENT_IN_PAYLOAD`
- Note lisible : "Audit live = 1 event par réponse Brody. Historique persisté : endpoint /api/audit/events (vide actuellement)"

---

### 6. OS3 PROOF TICKET (GovernanceTab)

**Source mock actuelle** : `MOCK_OS3_TICKET` (ticket fictif avec merkle_hash, lean_ref, tla_ref)

**Source live disponible** : **PARTIELLE**
- `/api/os3/tickets` répond 200 mais `tickets: []` — vide
- `getOS3Ticket()` dans obsidiaClient existe mais retombe sur mock si vide

**Champ payload exact** : Aucun champ `os3_ticket` dans le payload Brody

**Action recommandée** : `HIDE_NO_LIVE_SOURCE`

**Plan** :
- Supprimer `MOCK_OS3_TICKET` affiché
- Afficher : `NO_LIVE_OS3_PROOF_TICKET — /api/os3/tickets: 0 tickets`
- Garder note : "Endpoint /api/os3/tickets existe — connecté quand tickets présents"
- Ne PAS montrer de faux ticket proof

---

### 7. SOVEREIGN TICKET / WORLDCALL (GovernanceTab)

**Source mock actuelle** : `MOCK_SOVEREIGN_TICKET`, `MOCK_WORLD_CALLS`

**Source live disponible** : **NON**
- `/api/worldcalls` → `calls: []` — vide, `dry_run_only: true`
- `/api/worldcalls/sovereign-tickets` → `tickets: []` — vide

**Champ payload exact** : Aucun champ worldcall / sovereign_ticket dans le payload Brody

**Action recommandée** : `HIDE_NO_LIVE_SOURCE`

**Plan** :
- Supprimer `MOCK_WORLD_CALLS.map()` et `MOCK_SOVEREIGN_TICKET` affichés
- Afficher : `NO_LIVE_WORLD_CALLS — /api/worldcalls: 0 calls`
- Afficher : `NO_LIVE_SOVEREIGN_TICKETS — /api/worldcalls/sovereign-tickets: 0 tickets`
- Garder note : "Endpoints existent — connectés quand données présentes"

---

### 8. CONTEXT PACKET (ContextTab — dominant_trees)

**Source mock actuelle** : `MOCK_CONTEXT_PACKET.dominant_trees = [0,7,11,27,28,29]`

**Source live disponible** : **OUI** — voir §1 (Dominant Trees — REALIZE_FROM_PAYLOAD via tree_signal_packet)

**Note** : `payload.context_packet` est live (`packet_id: cp_brody_real_...`) mais n'a pas de `dominant_trees` ni `context_items`. Seul `tree_signal_packet.dominant_trees` contient les IDs réels.

**Action recommandée** : Couvert par §1 — `REALIZE_FROM_PAYLOAD`

---

## RÉSUMÉ DES ACTIONS

| Bloc | Source mock | Source live | Action |
|---|---|---|---|
| Dominant Trees | MOCK_CONTEXT_PACKET.dominant_trees | `tree_signal_packet.dominant_trees` | **REALIZE_FROM_PAYLOAD** |
| Graphiti Status | hardcodé | `payload.graphiti_status` + `.neo4j_status` | **REALIZE_FROM_PAYLOAD** |
| Memory Candidates | MOCK_MEMORY_CANDIDATES | `candidate_memory_snapshot.latest_candidates` | **REALIZE_FROM_PAYLOAD** |
| Gencoin Shadow | MOCK_GENCOIN | `gencoin_shadow_packet` (real, scores null) | **REALIZE_FROM_PAYLOAD** |
| Gencoin Ledger | MOCK_GENCOIN entries | `/api/gencoin` → 0 entries | **HIDE_NO_LIVE_SOURCE** |
| Audit Events | MOCK_AUDIT | `payload.audit_event` (1 per response) | **REALIZE_FROM_PAYLOAD** |
| OS3 Proof Ticket | MOCK_OS3_TICKET | `/api/os3/tickets` → 0 tickets | **HIDE_NO_LIVE_SOURCE** |
| Sovereign Ticket | MOCK_SOVEREIGN_TICKET | `/api/worldcalls/sovereign-tickets` → 0 | **HIDE_NO_LIVE_SOURCE** |
| WorldCall / Gateway | MOCK_WORLD_CALLS | `/api/worldcalls` → 0 calls | **HIDE_NO_LIVE_SOURCE** |

---

## BUGS IDENTIFIÉS (hors scope F16 UI — à noter)

1. `getAuditEvents()` dans obsidiaClient.ts appelle `/v1/audit/chain` — chemin incorrect. Le bon chemin est `/api/audit/events`.
2. `ENGINE_BASE` default = `http://127.0.0.1:8012` — devrait être 8000 (comme corrigé dans brody_chat.py). Fonctionne grâce aux env vars locales.
3. `API_BASE` default = `http://127.0.0.1:8011` — port inconnu, probablement aussi piloté par env vars.

---

## PROPS NÉCESSAIRES POUR F16 PATCH

**GovernanceTab** : doit recevoir `live?: Record<string,unknown>` pour lire `audit_event` (non, audit est dans AuditTab) — non nécessaire
**MemoryTab** : doit recevoir `live?: Record<string,unknown>` pour lire `candidate_memory_snapshot`, `graphiti_status`, `neo4j_status`, `graphiti_blocker`
**GencoinTab** : doit recevoir `live?: Record<string,unknown>` pour lire `gencoin_shadow_packet`
**GovernanceTab** : aucun payload disponible pour les 3 blocs → HIDE. Pas de prop nécessaire.

**App.tsx → RightPanel** : `lastBackendPayload` déjà passé en prop. Il faut transmettre ce prop vers GovernanceTab/MemoryTab/GencoinTab/AuditTab depuis RightPanel.

---

## STOP — EN ATTENTE VALIDATION

```
F16_AUDIT_READ_ONLY_COMPLETE=true
NO_PATCH_APPLIED=true
AWAITING_USER_VALIDATION=true
```
