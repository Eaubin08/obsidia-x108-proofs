# OBSIDIA F15 — RIGHTPANEL REAL PAYLOAD ALIGNMENT AUDIT

Date: 2026-05-27 23:59
Phase: F15_RIGHTPANEL_REAL_PAYLOAD_ALIGNMENT
Mode: READ_ONLY — NO PATCH
Status: AUDIT_COMPLETE — AWAITING USER VALIDATION

---

## A. GIT STATE

```
Branch:      main...origin/main (clean)
Last commit: be1e036  feat: freeze Brody copy command button UI F14
Tag:         BRODY_F14_COMMAND_COPY_BUTTON_UI_FREEZE_20260527
Stash:       EMPTY
```

---

## B. BACKEND 8000

```
ROOT http://127.0.0.1:8000/ → 200 OK
POST /api/brody/chat → 200 OK
Payload size: 338 573 chars
Payload saved: docs/runtime/F15_RIGHTPANEL_LIVE_PAYLOAD_8000.json
Test prompt: "write Graphiti memory + canon -> DOMAIN_RACCORD_WRITE_BOUNDARY"
```

Top-level boundary confirmed from live payload:
```
readonly         = True
advisory_only    = True
emits_act        = False
emits_verdict    = False
decision_authority = KX108_ONLY
memory_write     = False
kernel_mutation  = False
graphiti_write   = False
source           = REAL_BRODY_RUNTIME_NO_GRAPHITI
graphiti_status  = GRAPHITI_LIVE_BLOCKED
neo4j_status     = LIVE_READONLY
```

---

## C. TESTS BASELINE

```
tests/ui/ + tests/api/f10c + f12c → 21/21 PASS
Frontend build → PASS (878ms, 0 erreurs TypeScript)
```

---

## D. BLOCK MAP — RIGHTPANEL vs PAYLOAD LIVE

### CONTEXT TAB

| Bloc UI | Champ payload source | Présent payload live | UI affiche | Mock/Fallback | Stale/Fantôme | Action |
|---|---|---|---|---|---|---|
| **Authority Snapshot** | `authority_snapshot` | YES (10 keys) | YES | NO | NO | **KEEP** |
| **True Voice / LLM Obsidien** | `true_voice_snapshot` | YES (38 keys) | YES | NO | PARTIAL* | **KEEP + MINOR** |
| **Adaptive Response Policy/Sigma** | `true_voice_snapshot.adaptive_response_policy` | YES (8 keys) | YES | NO | NO | **KEEP** |
| **Domain Raccord / Structure-First** | `true_voice_snapshot.domain_raccord_snapshot` | YES | YES | NO | NO | **KEEP** |
| **12E6 Boundary Envelope** | top-level payload fields | YES | YES | NO | NO | **KEEP** |
| **Native Machination** | `machination_packet`, `support_summary` | YES | YES | NO | NO | **KEEP** |
| **Contracts / Permission Matrix** | `contracts`, `permission_matrix` | YES | YES | NO | NO | **KEEP** |
| **Native Boundary** | `boundary_contract`, `contracts.boundary_contract` | YES | YES | NO | NO | **KEEP** |
| **Live Backend — Last Response** | `voice_runtime`, `source`, `graphiti_status`, `neo4j_status` | YES | YES | NO | NO | **KEEP** |
| **Transverse Operator View** | `operator_view_packet` | YES (23 keys) | YES | NO | NO | **KEEP** |
| **Semantic Query Router** | `semantic_query_snapshot` | YES (8 keys) | YES | NO | NO | **KEEP** |
| **Memory Response Chain** | `memory_response_chain_snapshot` | YES (33 keys) | YES | NO | NO | **KEEP** |
| **Runtime Context** | `runtime_context` | YES (38 keys) | YES | NO | NO | **KEEP** |
| **Project Memory** | `project_memory_snapshot` | YES (36 keys) | YES | NO | NO | **KEEP** |
| **Candidate Memory** | `candidate_memory_snapshot` | YES (25 keys) | YES | NO | NO | **KEEP** |
| **Operator Loop** | `operator_loop_snapshot` | YES (27 keys) | YES (minimal: status only) | NO | NO | **KEEP** |
| **Tree Policy (34 arbres)** | `tree_policy_snapshot` | YES (20 keys) | YES | NO | DRIFT* | **MINOR** |
| **Temporal Context** | `temporal_context_snapshot` | YES (18 keys) | YES | NO | NO | **KEEP** |
| **Cognitive Modules** | `cognitive_modules_snapshot` | YES (19 keys) | YES | NO | NO | **KEEP** |
| **Context Packet — Live** | `context_packet` | YES (partial) | YES (conditional) | NO | NO | **KEEP** |
| **Context Packet (static)** | `MOCK_CONTEXT_PACKET` | NO | YES | **MOCK** | YES* | **LABEL** |
| **Context Items (static)** | `MOCK_CONTEXT_PACKET.context_items` | NO | YES | **MOCK** | YES* | **LABEL** |
| **Dominant Trees (static)** | `MOCK_CONTEXT_PACKET.dominant_trees` | NO | YES | **MOCK** | YES* | **LABEL** |

---

### GOVERNANCE TAB

| Bloc UI | Champ payload source | Présent payload | UI affiche | Mock | Stale/Fantôme | Action |
|---|---|---|---|---|---|---|
| OS3 Proof Ticket | `MOCK_OS3_TICKET` | NO | YES | **100% MOCK** | YES | **LABEL AS MOCK** |
| Sovereign Ticket | `MOCK_SOVEREIGN_TICKET` | NO | YES | **100% MOCK** | YES | **LABEL AS MOCK** |
| WorldCall / Gateway | `MOCK_WORLD_CALLS` | NO | YES | **100% MOCK** | YES | **LABEL AS MOCK** |

→ **GovernanceTab est entièrement mock.** Aucun champ ne vient du payload live.
→ Acceptable pour l'instant (ces données viendraient de proofs/formal — pas du runtime brody).
→ Action recommandée: ajouter label visible "STATIC / NOT FROM RUNTIME" ou "MOCK_ONLY".

---

### MEMORY TAB

| Bloc UI | Champ payload source | Présent payload | UI affiche | Mock | Stale/Fantôme | Action |
|---|---|---|---|---|---|---|
| Memory Candidates | `MOCK_MEMORY_CANDIDATES` | NO | YES | **100% MOCK** | YES | **LABEL AS MOCK** |
| Graphiti Status | hardcodé "READONLY BRIDGE" | NO | YES | **HARDCODED** | YES | **LABEL** |

→ **MemoryTab est entièrement mock/hardcodé.** Le payload expose `memory_response_chain_snapshot`, `project_memory_snapshot`, `candidate_memory_snapshot` — aucun n'est utilisé ici.
→ Les vraies données mémoire sont dans la ContextTab (Runtime Context, Memory Response Chain, Project Memory).

---

### GENCOIN TAB

| Bloc UI | Champ payload source | Présent payload | UI affiche | Mock | Stale/Fantôme | Action |
|---|---|---|---|---|---|---|
| Warning banner | hardcodé | — | YES | HARDCODED | NON (correct) | **KEEP** |
| Ledger Entries | `MOCK_GENCOIN` | NO | YES | **100% MOCK** | YES | **LABEL AS MOCK** |

→ `gencoin_shadow_packet` est présent dans le payload mais **non utilisé dans GencoinTab**.
→ Les shadow scores sont dans `gencoin_shadow_packet.shadow_scores` — non affichés nulle part.
→ `value_layer.scores` = null → correct.

---

### AUDIT TAB

| Bloc UI | Champ payload | Présent payload | Affichage | Mock | Action |
|---|---|---|---|---|---|
| response_md | `response_md` | YES | YES (show/hide) | NO | **KEEP** |
| Audit events | `MOCK_AUDIT` | NO | YES | **100% MOCK** | **LABEL** |

---

### AUTOMATION TAB

| Bloc UI | Champ payload source | Présent payload | UI affiche | Mock | Action |
|---|---|---|---|---|---|
| AutomationTab header | `automation_snapshot.*` | YES | YES | NO | **KEEP** |
| Session Ledger | `automation_snapshot.session_ledger` | YES | YES | NO | **KEEP** |
| Presave Buffer | `automation_snapshot.presave_buffer` | YES | YES | NO | **KEEP** |
| Auto Triage | `automation_snapshot.auto_triage` | YES | YES | NO | **KEEP** |
| Memory Pipeline | `automation_snapshot.memory_candidate_pipeline` | YES | YES | NO | **KEEP** |
| Operator Loop | `automation_snapshot.operator_loop` | YES | YES | NO | **KEEP** |
| Next Allowed Steps | `automation_snapshot.next_allowed_steps` | YES | YES | NO | **KEEP** |
| Blocked Steps | `automation_snapshot.blocked_steps` | YES | YES | NO | **KEEP** |
| StructuredResponseTab | `structured_response_snapshot` | YES (24 keys) | YES | NO | **KEEP** |

→ **AutomationTab est entièrement aligné sur payload live.** ✓

---

### BACKEND TAB

→ `BackendStatusPanel` — composant séparé. Non audité ici (audit séparé requis si nécessaire).

---

### FREEZE TAB

| Bloc UI | Champ payload source | Présent payload | UI affiche | Mock | Action |
|---|---|---|---|---|---|
| FreezeMetricsTab | `freeze_metrics_snapshot` | YES (21 keys) | YES | NO | **KEEP** |
| ContextPacket Chain | `freeze_metrics_snapshot.context_packet_chain` | YES | YES | NO | **KEEP** |
| Operator Loop | `freeze_metrics_snapshot.operator_loop` | YES | YES | NO | **KEEP** |
| Memory Pipeline | `freeze_metrics_snapshot.memory_pipeline` | YES | YES | NO | **KEEP** |
| X108 Boundary | `freeze_metrics_snapshot.x108_boundary` | YES | YES | NO | **KEEP** |
| Runtime LLM | `freeze_metrics_snapshot.runtime_llm` | YES | YES | NO | **KEEP** |
| X108 Proof State | `freeze_metrics_snapshot.x108_proof_state` | YES | YES | NO | **KEEP** |

→ **FreezeTab est entièrement aligné.** ✓

---

## E. FIELD DRIFT DÉTECTÉ

### 1. TREE_POLICY_SNAPSHOT — `safe_trees` drift (MINOR)

```
UI lit:       treePol.safe_trees  → payload: ['TREE_X108_BOUNDARY']  (1 item — string label)
Données réelles: treePol.tree_policy.safe_trees → ['T13','T14','T15',...,'T29'] (13 items)
UI affiche:   "1" au lieu de "13"
```
**Impact** : l'opérateur voit "safe: 1 tree" au lieu de "safe: 13 trees".
**Fix** : lire `treePol.tree_policy?.safe_trees ?? treePol.safe_trees`.

### 2. TREE_POLICY_SNAPSHOT — `total_trees` absent (MINOR)

```
UI lit:       treePol.total_trees → null (absent du payload snapshot direct)
Données réelles: dans tree_policy nested, count = 13 safe
UI affiche:   "34" (hardcodé fallback)
```
**Impact** : cosmétique — le fallback 34 est la valeur cible correcte.
**Fix** : aucun urgent — le fallback "34" est intentionnel.

### 3. `v18_hash_status` dans Context Packet statique — FANTÔME

```
RightPanel line 548:  <CopyableKV k="v18_hash_status" v={v18} .../>
v18 = const v18: string = 'FAIL'   (hardcodé, jamais lu du payload)
payload live: v18_hash_status not present
```
**Impact** : affiche `v18_hash_status: FAIL` en permanence — stale/fantôme.
**Fix** : supprimer ou labeliser "STATIC_REFERENCE_ONLY".

### 4. `git_branch` dans Context Packet statique — FANTÔME

```
RightPanel line 549:  <CopyableKV k="git_branch" v="ci-strict-sigma" .../>
Hardcodé string, jamais lu du payload. Peut être stale.
```
**Impact** : affiche un nom de branche potentiellement faux.
**Fix** : supprimer ou labeliser "STATIC_REFERENCE_ONLY".

### 5. True Voice — `model_position` et `foundation` absents du payload direct

```
RightPanel lit: trs.model_position (from true_response_structure_snapshot)
Payload: true_response_structure_snapshot.model_position → NOT FOUND
         true_voice_snapshot.model_position → null
UI fallback: 'LLM_OBSIDIEN_READONLY_ADVISORY' (hardcodé)
```
**Impact** : fallback correct mais non issu du payload.
**Fix** : acceptable — fallback intentionnel.

### 6. `can_prepare_candidate` dans candidate_memory_snapshot — null

```
UI lit:   candMem.can_prepare_candidate
Payload:  can_prepare_candidate = null
UI shows: "null" en string via String()
```
**Impact** : s'affiche comme "null" au lieu de "—" ou "false".
**Fix** : minor — ajouter `?? false` ou `?? '—'`.

---

## F. MOCK / FANTÔME SUMMARY

| Zone | Type | Verdict |
|---|---|---|
| `v18_hash_status: FAIL` (hardcodé) | FANTÔME | Supprimer ou labeliser |
| `git_branch: ci-strict-sigma` (hardcodé) | FANTÔME | Supprimer ou labeliser |
| GovernanceTab entier | 100% MOCK | Labeliser "MOCK / NOT FROM RUNTIME" |
| MemoryTab Memory Candidates | 100% MOCK | Labeliser "MOCK / NOT FROM RUNTIME" |
| MemoryTab Graphiti Status | HARDCODED | Labeliser ou connecter à payload |
| GencoinTab Ledger Entries | 100% MOCK | Labeliser "MOCK / NOT FROM RUNTIME" |
| AuditTab events | 100% MOCK | Labeliser "MOCK / NOT FROM RUNTIME" |
| Context Packet statique (MOCK_CONTEXT_PACKET) | MOCK | Labeliser "STATIC / NOT FROM RUNTIME" |
| Context Items statiques | MOCK | Labeliser "STATIC / NOT FROM RUNTIME" |
| Dominant Trees statiques | MOCK | Labeliser "STATIC / NOT FROM RUNTIME" |
| tree_policy.safe_trees lu au mauvais niveau | DRIFT | Fix: lire `.tree_policy.safe_trees` |

**Aucun champ mock n'est dangereux.** Ils sont clairement dans des blocs séparés des données live.
Le vrai problème est l'absence de labellisation visible.

---

## G. SECTIONS SANS PROBLÈME — ALIGNEMENT PARFAIT

Les sections suivantes sont **100% alignées sur le payload live 8000** :

- ✓ Authority Snapshot
- ✓ True Voice / LLM Obsidien (sauf model_position fallback acceptable)
- ✓ Adaptive Response Policy / Sigma
- ✓ Domain Raccord / Structure-First
- ✓ 12E6 Boundary Envelope
- ✓ Native Machination
- ✓ Contracts / Permission Matrix
- ✓ Native Boundary
- ✓ Live Backend — Last Response
- ✓ Transverse Operator View
- ✓ Semantic Query Router
- ✓ Memory Response Chain
- ✓ Runtime Context
- ✓ Project Memory
- ✓ Candidate Memory (sauf can_prepare_candidate null minime)
- ✓ Operator Loop (minimal mais correct)
- ✓ Temporal Context
- ✓ Cognitive Modules
- ✓ AutomationTab complet
- ✓ FreezeTab complet
- ✓ AuditTab response_md

---

## H. PAYLOAD FIELDS PRÉSENTS MAIS NON AFFICHÉS DANS RIGHTPANEL

| Champ | Présent | Utilisé dans RightPanel |
|---|---|---|
| `gencoin_shadow_packet` | YES | **NO** (absent du RightPanel) |
| `tree_signal_packet` | YES | **NO** |
| `memory_promotion_guard_packet` | YES | **NO** |
| `sigma_packet` | YES | **NO** |
| `anti_mismatch_packet` | YES | **NO** |
| `thermodynamics_packet` | YES | **NO** |
| `operator_loop_snapshot` | YES | MINIMAL (status only dans ContextTab) |
| `brody_full_context` | YES | NO |
| `true_response_structure_snapshot` | YES | PARTIAL (model_position via fallback) |

→ Ce sont des données F2-F7 qui mériteraient un onglet dédié (F20 Runtime Dashboard).
→ Pas de patch urgent — ils ne sont pas affichés comme faux, juste absents du RightPanel.

---

## I. PATCH RECOMMENDATION

### Priorité 1 — Fantômes (à supprimer ou labeliser)

| Item | Localisation | Fix |
|---|---|---|
| `v18_hash_status: FAIL` | RightPanel.tsx line 548 | Supprimer la ligne |
| `git_branch: ci-strict-sigma` | RightPanel.tsx line 549 | Supprimer la ligne |

**Ces 2 lignes sont hardcodées et ne viennent jamais du payload.** Elles induisent l'opérateur en erreur.

### Priorité 2 — Tree Policy safe_trees drift (à corriger)

| Item | Localisation | Fix |
|---|---|---|
| `treePol.safe_trees` → 1 item au lieu de 13 | RightPanel.tsx line 488 | Lire `treePol.tree_policy?.safe_trees?.length ?? treePol.safe_trees?.length ?? 0` |

**L'opérateur voit "safe: 1" au lieu de "safe: 13".**

### Priorité 3 — Labelisation mock (cosmétique, bas risque)

Ajouter une mention `[MOCK / NOT FROM RUNTIME]` dans les titres des blocs:
- GovernanceTab : OS3 Proof Ticket, Sovereign Ticket, WorldCall
- MemoryTab : Memory Candidates, Graphiti Status
- GencoinTab : Ledger Entries
- AuditTab : Audit Events
- ContextTab : Context Packet statique, Context Items, Dominant Trees

**Faible urgence** — l'opérateur averti sait que ces blocs sont statiques.

### Priorité 4 — can_prepare_candidate null → afficher "—"

```tsx
// Ligne 466 actuelle:
<CopyableKV k="can_prepare" v={String(candMem.can_prepare_candidate ?? false)} .../>
// Déjà avec ?? false — OK
```
→ Vérification: la ligne a déjà `?? false`. Pas de patch nécessaire.

---

## J. VERDICT FINAL

```
RIGHTPANEL_CORE_ALIGNMENT = GOOD
  ContextTab live sections = 100% aligned (19/19 live blocs OK)
  AutomationTab           = 100% aligned
  FreezeTab               = 100% aligned
  AuditTab response_md    = aligned

PHANTOMS FOUND = 2 lignes critiques + 1 drift tree_policy
  v18_hash_status FAIL    = PHANTOM — suppress
  git_branch ci-strict-sigma = PHANTOM — suppress
  tree_policy.safe_trees count = 1 vs 13 — drift — fix read path

MOCK ZONES = acceptable but unlabeled
  GovernanceTab   = 100% mock (no live equivalent in brody runtime payload)
  MemoryTab       = 100% mock (live data in ContextTab)
  GencoinTab ledger = 100% mock (shadow scores not wired to GencoinTab)
  AuditTab events = 100% mock
```

---

## K. PATCH SCOPE PROPOSÉ — F15 (MINIMAL)

```
PATCH_SCOPE = MINIMAL (3 suppressions / 1 correction de lecture)
FILES_TO_MODIFY = apps/obsidia-workbench/src/components/RightPanel.tsx

CHANGE 1: Supprimer la ligne v18_hash_status (line 548)
CHANGE 2: Supprimer la ligne git_branch (line 549)
CHANGE 3: Corriger tree_policy.safe_trees read path (line 488):
  BEFORE: String(treePol.safe_trees ?? 0)
  AFTER:  String(
    (Array.isArray((treePol.tree_policy as {safe_trees?:unknown[]})?.safe_trees)
      ? (treePol.tree_policy as {safe_trees:unknown[]}).safe_trees.length
      : Array.isArray(treePol.safe_trees)
        ? treePol.safe_trees.length
        : 0))

CHANGE 4 (OPTIONAL): Ajouter label "[MOCK]" dans SectionTitle des blocs statiques
```

---

## VALIDATION PHRASE

```
F15_RIGHTPANEL_REAL_PAYLOAD_ALIGNMENT_AUDIT_PASS
BACKEND_8000=LIVE_200
PAYLOAD_CAPTURED=true
PAYLOAD_SIZE=338573
LIVE_BLOCS_ALIGNED=19_19
AUTOMATION_TAB_ALIGNED=true
FREEZE_TAB_ALIGNED=true
PHANTOM_v18_hash_status=FOUND
PHANTOM_git_branch=FOUND
DRIFT_tree_policy_safe_trees=FOUND
MOCK_ZONES=GOVERNANCE_MEMORY_GENCOIN_AUDIT_CONTEXT_STATIC
PATCH_SCOPE=MINIMAL_3_SUPPRESSIONS_1_FIX
NO_PATCH_APPLIED=true
NO_KERNEL_TOUCHED=true
NO_BACKEND_TOUCHED=true
AWAITING_USER_VALIDATION=true
```

---

STOP — READ_ONLY AUDIT COMPLETE — EN ATTENTE VALIDATION UTILISATEUR
