# HACKATHON ARCHITECTURE CANON — Obsidia Band V2

> Mode : AUDIT READONLY  
> Corrections V1 appliquées : X108 = Gate (pas agent), verdicts normalisés, Band = cockpit  
> Marqueurs : [E] = Explicit source | [I] = Inferred | [P] = Proposed

---

## Architecture globale

```
BAND (Surface visible / Cockpit / Coordination Layer)
  │
  ▼
INPUT CAPTURE
  │   [E] ACTION_LIFECYCLE_CONTRACT_V0.md : INPUT_CAPTURED (step 1/11)
  ▼
BRODY ORCHESTRATION SURFACE
  │   [E] brody_full_runtime_orchestrator.py : 13 modules, SOV envelope
  │   Brody rôle : PREPARE_AND_STRUCTURE_ONLY
  │   brody_execute_allowed = False
  │   emits_act = False
  ▼
CONTEXT PACKET / RAG SURFACE
  │   [E] CONTEXT_PACKET_BUILDER_V2.md : ContextPacketV2
  │   decision_authority = "KX108_ONLY"
  │   context_signal_only = True
  │   allowed_to_decide = False, allowed_to_act = False
  ▼
SEMANTIC ROUTER
  │   [E] brody_semantic_query_router.py : 16 routes + NEXT_STEPS compound
  │   Normalisation UTF-8 mojibake → canonical queries → Neo4j
  │   PERIPHERY_SCORED (step 3/11)
  ▼
DOMAIN RISK / TREE POLICY SURFACE
  │   [E] brody_tree_policy.py : 22 arbres T13-T34
  │   [E] brody_rights_authority_matrix.py : 11 catégories, classify_request_authority()
  │   SIGMA_ROUTED (step 4/11)
  ▼
X108 GATE / AUTHORITY SURFACE  ← jamais un "agent" — c'est une gate d'autorité
  │   [E] routes/x108.py : _BOUNDARY={readonly:True, emits_act:False}
  │   14 routes sous /api/x108
  │   x108_role = "DECIDE_AND_AUTHORIZE"
  │   X108_EVALUATED (step 5/11)
  ▼
OS3 PROOF / REPLAY SURFACE
  │   [E] OS3_PROOF_TICKET_SCHEMA_V0.md : hash + ticket + replay
  │   [E] /math/pog : Proof of Governance
  │   OS3_TICKETED (step 6/11)
  ▼
GENCOIN EVALUATED (step 7/11)
  │   [E] CAPABILITY_IS_NOT_AUTHORITY_V1.md : "Gencoin minting — Not a real token — ledger only"
  ▼
DRY-RUN READINESS
  │   [E] WORLD_ACTION_DRY_RUN_POLICY_V0.md : readiness uniquement
  │   [E] ACTION_CANDIDATE_TO_WORLD_ACTION_FLOW_V0.md
  │   Verdict Band : ACT_SIMULATED / HOLD / BLOCK
  │   WORLD_ACTION_DRY_RUN_READY (step 8/11)
  ▼
FEEDBACK / RCHF SURFACE
  │   [E] FEEDBACK_MEMORY_CANDIDATE_POLICY_V0.md
  │   FEEDBACK_CAPTURED (step 9/11)
  ▼
MEMORY CANDIDATE
  │   [E] MEMORY_CANDIDATE_LEDGER_V1.md : APPEND-ONLY
  │   [E] brody_candidate_memory_adapter.py : gates_required=6, auto_promotion=False
  │   MEMORY_CANDIDATE_BUILT (step 10/11)
  ▼
REPLAY
  │   [E] /memory/replay/session + /memory/replay/coherence
  │   CLOSED (step 11/11)
```

---

## Détail par couche

---

### Couche 1 — BAND (Surface visible / Cockpit)

| Champ | Valeur |
|-------|--------|
| **Rôle** | Surface de coordination visible. Expose les agents Band. Ne gouverne pas. |
| **Source** | `COGNITION_TO_ACTION_GOVERNANCE_V1.md` [E] |
| **Autorise** | Coordination des surfaces visibles, affichage des états |
| **Interdit** | Prendre des décisions, émettre ACT, court-circuiter X108 |
| **Métriques associées** | Voir DASHBOARD_FIELDS_CANON.md |
| **Preuve attendue** | SOV envelope visible dans chaque réponse |
| **Visibilité Band** | Toujours visible — c'est la couche Band elle-même |

---

### Couche 2 — Brody Orchestration Surface

| Champ | Valeur |
|-------|--------|
| **Rôle** | Orchestrer les modules, produire contexte et réponses advisory |
| **Source** | `brody_full_runtime_orchestrator.py`, `brody_operator_loop_adapter.py` [E] |
| **Autorise** | Répondre, analyser, préparer context packets, proposer candidates |
| **Interdit** | Émettre ACT, décider, écrire mémoire, exécuter sans humain |
| **Métriques** | runtime_chain status (LOADED/FAILED), source (REAL_BRODY_/BACKEND_STUB_) |
| **Preuve attendue** | `brody_execute_allowed=False` dans chaque snapshot |
| **Visibilité Band** | "Brody Orchestration Surface" |

**Modules orchestrés (13) [E — brody_full_runtime_orchestrator.py] :**
```
terminal_structural_dialogue   → LIVE / FAILED
local_response_engine          → LIVE / LOADED
context_packet_query           → LOADED / NOT_FOUND
content_hydration              → LOADED / NOT_FOUND
session_memory_ledger          → DISABLED / LOADED
session_presave_buffer         → LOADED / NOT_FOUND
memory_scheduler               → LOADED / NOT_FOUND
post_human_review_triage       → LOADED / NOT_FOUND
auto_triage_memory_intake      → LOADED / NOT_FOUND
candidate_export_for_graphiti  → LOADED_BUT_GRAPHITI_OFFLINE
graphiti_import_dry_run        → LOADED_BUT_GRAPHITI_OFFLINE
graphiti_review_gate           → LOADED_BUT_GRAPHITI_OFFLINE
graphiti_guarded_manual_apply  → LOADED_BUT_GRAPHITI_OFFLINE
```

**Sovereignty Envelope [E] :**
```python
readonly=True, allowed_to_decide=False, allowed_to_act=False,
emits_act=False, emits_verdict=False, emits_allow_hold_block=False,
kernel_mutation=False, decision_authority="KX108_ONLY",
memory_write=False, graphiti_write=False, neo4j_write=False
```

---

### Couche 3 — Context Packet / RAG Surface

| Champ | Valeur |
|-------|--------|
| **Rôle** | Assembler le signal contextuel depuis sources multiples → X108 |
| **Source** | `CONTEXT_PACKET_BUILDER_V2.md`, `CONTEXT_SIGNAL_ONLY_POLICY_V1.md` [E] |
| **Inputs** | action_id, brody_response, graphiti_context, memory_candidates, source_labels |
| **Output** | ContextPacketV2 : immutable, signal_only, decision_authority=KX108_ONLY |
| **Autorise** | Assembler, structurer, transmettre en readonly-ingress |
| **Interdit** | Décider, modifier après build, bypass X108, execute |
| **Métriques** | oracle_freshness (via `/oracle/freshness`), packets_accepted, violations |
| **Preuve** | `allowed_to_decide=False`, `allowed_to_act=False` dans chaque packet |
| **Visibilité Band** | "Context Packet / RAG Surface" |

**Invariant absolu [E — CONTEXT_SIGNAL_ONLY_POLICY_V1.md] :**
> _"Contexte = signal. Signal ≠ décision."_

---

### Couche 4 — Domain Risk / Tree Policy Surface

| Champ | Valeur |
|-------|--------|
| **Rôle** | Classifier la requête, activer les bons arbres, scorer la périphérie |
| **Source** | `brody_tree_policy.py`, `brody_rights_authority_matrix.py` [E] |
| **Autorise** | Citer arbres safe (T13-T19, T23, T25-T29), activer signaux contextuels readonly |
| **Interdit** | Déclencher T20-T22 comme action, écrire via T24, activer T30-T34 AGI |
| **Métriques** | PERIPHERY_SCORED, tree activations, request_type classificated |
| **Preuve** | `signal_method="PATH_SLUG"`, arbres bloqués cités mais non activés |
| **Visibilité Band** | "Domain Risk / Tree Policy Surface" |

**22 arbres T13-T34 [E — brody_tree_policy.py] :**
```
SAFE (13):     T13=Art, T14=Philosophie, T15=Spiritualite, T16=Relation, T17=Collectif,
               T18=Transmission, T19=Culture, T23=Temps, T25=Histoire, T26=Coherence,
               T27=Verite, T28=Valeur, T29=Finalite
BLOCKED ACT:   T20=Action, T21=Creation, T22=Transformation
BLOCKED MEM:   T24=Memoire
BLOCKED AGI:   T30=Cognitif Global, T31=Flux, T32=Connexions, T33=Optimisation, T34=Stabilite
```

---

### Couche 5 — X108 Gate / Authority Surface

> **CORRECTION V1 OBLIGATOIRE** : X108 n'est PAS un agent. C'est une gate d'autorité exposée dans Band.

| Champ | Valeur |
|-------|--------|
| **Rôle** | Gate d'autorité unique. Seul décideur du système. |
| **Source** | `routes/x108.py`, `COGNITION_TO_ACTION_GOVERNANCE_V1.md` [E] |
| **Boundary** | `_BOUNDARY = {"readonly": True, "emits_act": False, "memory_write": False, "decision_authority": "KX108_ONLY"}` |
| **Autorise** | Évaluer, scorer, prouver, ticketer — mais toujours en boundary readonly |
| **Interdit** | Émettre ACT réel, modifier mémoire, court-circuiter OS3 |
| **Métriques** | x108_gate (ALLOW→ACT_SIMULATED / HOLD / BLOCK), lyapunov_stable, coherence_score, trust_path_depth |
| **Preuve** | SovereignTicket + ProofOfGovernance (via `/math/pog`) |
| **Visibilité Band** | "X108 Gate / Authority Surface" |

**14 routes explicites [E — routes/x108.py, prefix=/api/x108] :**
```
POST /cognitive/shazam          — signature cognitive
POST /cognitive/dominant-trees  — arbres dominants
POST /math/lyapunov             — stabilité Lyapunov
POST /math/pog                  — Proof of Governance
GET  /memory/candidates/read    — lecture candidats
POST /memory/candidates/append  — append candidat
POST /math/trust-path           — chemin de confiance
POST /cognitive/regime-classify — classification régime
POST /oracle/freshness          — fraîcheur oracle
POST /timeverse/sync            — sync temporelle
POST /memory/replay/session     — replay session
POST /memory/replay/coherence   — cohérence replay
GET  /memory/logs/sealed        — logs scellés
POST /readonly-ingress          — ingestion READONLY
```

---

### Couche 6 — OS3 Proof / Replay Surface

| Champ | Valeur |
|-------|--------|
| **Rôle** | Preuve formelle pré-action : hash + ticket + manifeste replay |
| **Source** | `OS3_PROOF_TICKET_SCHEMA_V0.md`, `OS3_REPLAY_MANIFEST_V0.md`, `/math/pog` [E] |
| **Autorise** | Produire hash, générer SovereignTicket, créer manifeste replay |
| **Interdit** | Décider, émettre ACT, modifier ticket après génération |
| **Métriques** | proof_hash, sovereign_ticket_id, replay_coherence_score, boundary_ok_count |
| **Preuve** | `SESSION_REPLAY_READONLY_PASS` ou `COHERENCE_COMPUTED_READONLY` |
| **Visibilité Band** | "OS3 Proof / Replay Surface" |

**Loi O7 [E — O7_AUDITABILITE_NATIVE.md] :**
> _"Chaque projection, contexte ou signal doit être traçable, rejouable et inspectable."_

---

### Couche 7 — Feedback / RCHF Surface

| Champ | Valeur |
|-------|--------|
| **Rôle** | Capturer le feedback, créer le candidat mémoire, APPEND_ONLY |
| **Source** | `FEEDBACK_MEMORY_CANDIDATE_POLICY_V0.md`, `MEMORY_CANDIDATE_LEDGER_V1.md`, `brody_candidate_memory_adapter.py` [E] |
| **Autorise** | Append candidat, lire ledger, préparer review |
| **Interdit** | Auto-promouvoir, écrire mémoire opérationnelle, décider de la promotion |
| **Métriques** | candidate_ledger_count, gates_required=6, auto_promotion=False |
| **Preuve** | `auto_promotion_blocked=True`, `requires_human_review=True` |
| **Visibilité Band** | "Feedback / RCHF Surface" |

**Invariant absolu [E — MEMORY_PROMOTION_MANUAL_ONLY_V1.md] :**
> _"La promotion mémoire est exclusivement manuelle."_

---

## Règles architecturales globales

| Règle | Source | Valeur |
|-------|--------|--------|
| Décision authority | Toutes les couches [E] | KX108_ONLY — jamais délégué |
| Verdict Band | Sources + correction V2 | HOLD / BLOCK / ACT_SIMULATED — jamais ACT brut |
| Aucun score → ACT | CROSS_LAYER_STABILIZATION_MATRIX_V0.md [E] | Aucun score ne produit ACT directement |
| Cognition ≠ autorisation | COGNITION_TO_ACTION_GOVERNANCE_V1.md [E] | "Brody response ≠ governance verdict" |
| Capability ≠ Authority | CAPABILITY_IS_NOT_AUTHORITY_V1.md [E] | STABLE, core principle |

---

*Extraction READONLY — aucun fichier source modifié.*  
*Généré le 2026-06-10*
