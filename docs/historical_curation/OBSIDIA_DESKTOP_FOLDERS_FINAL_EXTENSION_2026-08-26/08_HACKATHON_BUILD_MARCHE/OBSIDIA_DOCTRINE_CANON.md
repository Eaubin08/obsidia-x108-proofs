# OBSIDIA DOCTRINE CANON — Comment Obsidia pense chaque concept

> Version : V2 — Corrections V1 appliquées  
> Marqueurs : [E] = Explicit source | [I] = Inferred | [P] = Proposed  
> Règle : ne jamais présenter la définition classique comme suffisante

---

## 1. RAG — Retrieval-Augmented Generation

**Définition classique insuffisante :**  
RAG = embedding + retrieval + génération augmentée. L'agent utilise le contexte récupéré pour répondre.

**Définition Obsidia :**  
RAG = construction du **Context Packet**. Le résultat n'est pas une réponse augmentée — c'est un signal structuré transmis à X108 Gate. Le contexte récupéré ne peut pas décider. Jamais.

**Mécanisme interne [E] :**
- `context_packet_builder_v2.py` assemble depuis : brody_response, graphiti_context, memory_candidates, source_labels
- Packet immuable une fois construit (`readonly=True`)
- Transmis via `POST /readonly-ingress` (X108 Gate)
- Fraîcheur validée via `POST /oracle/freshness`
- 16 routes sémantiques (`brody_semantic_query_router.py`) orientent la requête vers Neo4j

**Source exacte :** `CONTEXT_PACKET_BUILDER_V2.md`, `CONTEXT_SIGNAL_ONLY_POLICY_V1.md` [E]

**Invariant :** `decision_authority="KX108_ONLY"` dans chaque ContextPacketV2 [E]

**Métriques naturelles :**
- `oracle_freshness_gate` (FRESH/STALE/HOLD) — via `/oracle/freshness`
- `packets_accepted` / `violations` — via `/readonly-ingress`
- `route_hit_rate` — 16 routes canonical vs GENERAL fallback [I]

**Phrase jury :** _"Contexte ≠ décision. Le RAG produit un signal. X108 Gate décide."_

---

## 2. RCHF / RLHF — Reinforcement from Human/Contextual Feedback

**Définition classique insuffisante :**  
RLHF = reward model entraîné sur préférences humaines → mise à jour des poids du modèle.

**Définition Obsidia :**  
RCHF = **pipeline candidat mémoire**. Le feedback devient un candidat. Le candidat attend. Rien ne s'auto-applique.

**Mécanisme interne [E] :**
- Étape `FEEDBACK_CAPTURED` (step 9/11) → `MEMORY_CANDIDATE_BUILT` (step 10/11) [E]
- `build_memory_candidate_v2()` : candidate_id, content_hash (SHA-256), source_type, status
- Stocké dans `memory_candidates.jsonl` en mode APPEND_ONLY
- `auto_promotion_allowed=False` dans chaque candidat [E]
- `gates_required=6` avant toute promotion [E — `brody_candidate_memory_adapter.py`]

**Source exacte :** `MEMORY_CANDIDATE_LEDGER_V1.md`, `MEMORY_PROMOTION_MANUAL_ONLY_V1.md`, `FEEDBACK_MEMORY_CANDIDATE_POLICY_V0.md` [E]

**Invariant :** `auto_promotion_blocked=True`, `requires_human_review=True` — ABSOLUTE [E]

**Métriques naturelles :**
- `candidate_ledger_count` — nb de candidats accumulés
- `auto_promotion_rate` → doit être 0.0 strictement [E]
- `gates_required` = 6 — toujours 6 pour toute promotion [E]

**Phrase jury :** _"Feedback ≠ auto-apprentissage. Le feedback entre en candidature — l'humain décide de la promotion."_

---

## 3. Mémoire Candidate

**Définition classique insuffisante :**  
Base vectorielle mise à jour automatiquement par l'agent après chaque interaction.

**Définition Obsidia :**  
La mémoire est **APPEND_ONLY + review humaine**. Il n'existe pas de mise à jour automatique de la mémoire opérationnelle.

**Mécanisme interne [E] :**
```
Candidat créé → content_hash SHA-256 → ledger APPEND_ONLY
→ presave_buffer → auto_triage_intake → graphiti_review_gate
→ graphiti_import_dry_run (obligatoire avant tout import)
→ graphiti_guarded_manual_apply (GUARDED_MANUAL_ONLY)
```

**Source exacte :** `MEMORY_CANDIDATE_LEDGER_V1.md`, `brody_candidate_memory_adapter.py` [E]

**Invariant :** `memory_write_allowed=False` pour tous les agents — enforced à construction-time [E]

**Métriques naturelles :**
- `candidate_ledger_count` — compteur APPEND_ONLY
- `zero_auto_promotion_rate` — toujours 0.0 [E]
- `dry_run_import_rate` — 100% avant tout import réel [I]

**Phrase jury :** _"La mémoire s'accumule. Elle ne s'écrit pas d'elle-même."_

---

## 4. Loop Opérateur

**Définition classique insuffisante :**  
Boucle ReAct / agentique : planification autonome, exécution itérative, pas d'humain dans la boucle.

**Définition Obsidia :**  
La loop est **opérateur-contrôlée**. Brody prépare et structure. L'humain valide. X108 Gate autorise.

**Mécanisme interne [E — brody_operator_loop_adapter.py] :**
```python
brody_role = "PREPARE_AND_STRUCTURE_ONLY"
human_role = "VALIDATE_AND_OPERATE"
x108_role  = "DECIDE_AND_AUTHORIZE"
brody_execute_allowed = False
human_operator_required = True
receipt_schema_only = True
execution_allowed = False
```

**7 composants de la loop [E] :**
```
command_gate, human_command_packet, control_loop, execution_line,
execution_receipt, handoff_line, final_baseline
```

**Source exacte :** `brody_operator_loop_adapter.py` [E]

**Invariant :** `brody_execute_allowed=False` — non configurable [E]

**Métriques naturelles :**
- `components_pass_count` — nb de composants en état PASS (sur 7 total)
- `human_validation_required` — toujours true [E]

**Phrase jury :** _"La boucle propose. L'humain avance. X108 autorise."_

---

## 5. Automatisation

**Définition classique insuffisante :**  
Pipeline autonome, agents exécutent sans intervention humaine.

**Définition Obsidia :**  
L'automatisation est **conditionnelle et auditée**. Chaque script porte `DRY_RUN_ONLY=True` par défaut. Le dictionnaire `_BOUNDARY` (18 flags tous False) encode structurellement l'impossibilité d'agir.

**Mécanisme interne [E] :**
```python
# SOV envelope — brody_full_runtime_orchestrator.py
SOV = {
    "allowed_to_decide": False, "allowed_to_act": False,
    "emits_act": False, "emits_verdict": False,
    "emits_allow_hold_block": False,
    "kernel_mutation": False, "x108_mutation": False,
    "memory_write": False, "graphiti_write": False,
    "neo4j_write": False, "real_action": False,
    "decision_authority": "KX108_ONLY",
}
```

**Source exacte :** `brody_full_runtime_orchestrator.py` (SOV), `WORLD_ACTION_DRY_RUN_POLICY_V0.md` [E]

**Invariant :** DRY_RUN_ONLY par défaut — aucune action réelle sans SovereignTicket [E]

**Métriques naturelles :**
- `boundary_violation_rate` → 0.0 strictement [E]
- `dry_run_compliance_rate` → 1.0 attendu [E]

**Phrase jury :** _"L'automatisation Obsidia est prouvable : chaque étape est auditée avant d'exister."_

---

## 6. Agents Non-Souverains

**Définition classique insuffisante :**  
Agents autonomes avec mémoire, outils, capacité d'agir dans le monde.

**Définition Obsidia :**  
Tous les agents sont **non-souverains**. Leur contrat est enforced structurellement à construction-time.

**Mécanisme interne [E — NON_SOVEREIGN_AGENT_CONTRACT_V0.md] :**
```python
can_emit_act = false
can_authorize = false
can_mutate_kernel = false
can_write_memory = false
decision_authority = "KX108_ONLY"
```

**Patterns interdits [E — CAPABILITY_IS_NOT_AUTHORITY_V1.md] :**
```
Brody émettant ACT        → FORBIDDEN
Mémoire auto-promouvant   → FORBIDDEN
Périphérie émettant BLOCK/ALLOW souverain → FORBIDDEN
Blockchain sans SovereignTicket → FORBIDDEN
```

**Source exacte :** `NON_SOVEREIGN_AGENT_CONTRACT_V0.md`, `CAPABILITY_IS_NOT_AUTHORITY_V1.md` [E]

**Invariant :** Capability (pouvoir faire) ≠ Authority (droit de faire) [E] STABLE

**Métriques naturelles :**
- `non_sovereign_contract_violations` → 0 strictement [E]
- `capability_authority_leak_rate` → 0.0 [E]

**Phrase jury :** _"Capacité ≠ autorité. Pouvoir générer un output ≠ être autorisé à agir."_

---

## 7. Brody

**Définition classique insuffisante :**  
Assistant IA avec capacité de répondre et d'agir.

**Définition Obsidia :**  
Brody = **moteur advisory-only**. Il répond, analyse, prépare, structure — mais ne décide jamais.

**Mécanisme interne [E] :**
```python
# brody_full_runtime_orchestrator.py
emits_act = False
emits_verdict = False
advisory_only = True  # BRODY_NO_DECISION_POLICY_V1.md
decision_authority = "KX108_ONLY"
```

**Ce que Brody peut faire [E — BRODY_NO_DECISION_POLICY_V1.md] :**
- Répondre à des questions
- Analyser et diagnostiquer
- Suggérer HOLD/BLOCK comme input advisory à Sigma (jamais comme verdict)
- Préparer des context packets candidats
- Router les requêtes sémantiques (16 routes)

**Ce que Brody ne peut PAS faire [E] :**
- Émettre ALLOW / BLOCK / ACT comme verdict souverain
- Décider de l'approbation d'une action
- Override X108
- Écrire en mémoire
- Muter le kernel

**11 catégories d'intent [E — brody_rights_authority_matrix.py] :**
```
PURE_RESPONSE, CAPABILITY_SCOPE, CONTEXT_ANALYSIS, STRUCTURAL_PREPARATION,
MEMORY_CANDIDATE, OPERATOR_COMMAND_PROPOSAL, EXTERNAL_ACCESS_REQUEST,
ACTION_OR_ACT_REQUEST, MEMORY_WRITE_REQUEST, TREE_SIGNAL_REQUEST, PRIORITY_ADVISORY
```

**Source exacte :** `BRODY_NO_DECISION_POLICY_V1.md`, `brody_rights_authority_matrix.py`, `brody_full_runtime_orchestrator.py` [E]

**Invariant :** _"Brody répond. Brody ne décide pas."_ ABSOLUTE [E]

**Phrase jury :** _"Brody répond. Brody ne décide pas. Band montre la coordination. Obsidia gouverne le chemin."_

---

## 8. X108 Gate / Authority Surface

**Définition classique insuffisante :**  
Module d'évaluation ou de scoring parmi d'autres agents.

**Définition Obsidia :**  
X108 = **unique gate d'autorité**. Pas un agent. Une surface de décision souveraine exposée dans Band.

**Mécanisme interne [E — routes/x108.py] :**
```python
_BOUNDARY = {
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
    "decision_authority": "KX108_ONLY",
}
router = APIRouter(prefix="/api/x108")
```

**14 routes (évaluation, preuve, mémoire, replay) [E] :**
- Cognitive : `/shazam`, `/dominant-trees`, `/regime-classify`
- Math : `/lyapunov`, `/pog`, `/trust-path`
- Oracle : `/oracle/freshness`, `/timeverse/sync`
- Memory : `/candidates/read`, `/candidates/append`, `/logs/sealed`
- Replay : `/replay/session`, `/replay/coherence`
- Ingress : `/readonly-ingress`

**Source exacte :** `routes/x108.py`, `COGNITION_TO_ACTION_GOVERNANCE_V1.md` [E]

**Invariant :** `decision_authority="KX108_ONLY"` partout — non délégable [E]

**Métriques naturelles :**
- `x108_gate` (ALLOW→ACT_SIMULATED / HOLD / BLOCK)
- `lyapunov_stable` (bool)
- `pog_valid` (bool)
- `coherence_score` (float 0.0-1.0)
- `trust_path_depth` (int) [I]

**Phrase jury :** _"X108 garde l'autorité. C'est une gate — pas un agent."_

---

## 9. OS3 — Preuve / Replay

**Définition classique insuffisante :**  
Logger post-hoc ou audit trail après les faits.

**Définition Obsidia :**  
OS3 = **preuve formelle pré-action**. La preuve existe avant que l'action n'existe.

**Mécanisme interne [E] :**
```
Action candidate → OS3_TICKETED (step 6/11) → hash + SovereignTicket + ProofOfGovernance
→ Replay manifest (rejouable à tout moment)
→ /memory/logs/sealed (audit permanent)
```

**Loi O7 [E — O7_AUDITABILITE_NATIVE.md] :**  
_"Chaque projection, contexte ou signal doit être traçable, rejouable et inspectable."_

**Source exacte :** `OS3_PROOF_TICKET_SCHEMA_V0.md`, `OS3_REPLAY_MANIFEST_V0.md`, `routes/x108.py` `/math/pog` [E]

**Invariant :** `OS3_TICKETED` précède `WORLD_ACTION_DRY_RUN_READY` [E — lifecycle]

**Métriques naturelles :**
- `proof_coverage_rate` → 1.0 attendu (toutes actions ticketées) [E]
- `replay_coherence_score` (0.0-1.0 via `/replay/coherence`) [E]
- `boundary_violations` dans replay → 0 attendu [E]

**Phrase jury :** _"Chaque action laisse une preuve avant d'exister."_

---

## 10. Dry-Run

**Définition classique insuffisante :**  
Test en sandbox avant déploiement réel.

**Définition Obsidia :**  
Dry-run = **état par défaut permanent**. Pas un mode de test — c'est la posture normale. Passer hors dry-run nécessite un SovereignTicket X108 explicite.

**Mécanisme interne [E] :**
- `DRY_RUN_ONLY: bool = True` dans tous les scripts audit
- `WORLD_ACTION_DRY_RUN_READY` (step 8/11) — readiness seulement, pas exécution
- `ACTION_CANDIDATE_TO_WORLD_ACTION_FLOW_V0.md` : "Aucun ACT monde réel dans ce patch"

**Source exacte :** `WORLD_ACTION_DRY_RUN_POLICY_V0.md`, `ACTION_CANDIDATE_TO_WORLD_ACTION_FLOW_V0.md` [E]

**Invariant :** La sortie du dry-run est `ACT_SIMULATED` dans Band — jamais `ACT` brut [P — correction V2]

**Phrase jury :** _"ACT_SIMULATED signifie autorisé en simulation. Jamais action réelle exécutée."_

---

## 11. Jeux / Simulateurs / Éducation Agentique

**Définition classique insuffisante :**  
Environnements gym, reward shaping, épisodes, policy learning.

**Définition Obsidia :**  
Les scénarios sont des **épreuves de gouvernance**, pas des tests de performance. Le succès = la chaîne de décision correctement suivie — même si l'action n'est pas exécutée.

**Mécanisme interne [E — docs/BANK_SCENARIOS.md] :**
```
Scenario 1 (Normal) :       x108_gate=ALLOW    → demo: ACT_SIMULATED
Scenario 2 (Suspicious) :   pas de ALLOW path   → demo: HOLD (Loi O1)
Scenario 3 (Blocked Hard) : x108_gate=BLOCK S4  → demo: BLOCK (Loi O2)
```

**Fuzz Scale [E — docs/P2_BANK_FUZZ_SCALE_SCOPE.md] :**
```
1k cases   = public validation tier
10k cases  = stress tier (ready-to-run)
100k cases = stress tier (ready-to-run)
```

**Invariants fuzz [E] :** `unsafe_allow_count=0`, `softer_drift_count=0`, `clean_rejection_count` maximal

**Éducation [E — docs/education/README.md] :** `ADVISORY_ONLY` — "X108 decides"

**Source exacte :** `BANK_SCENARIOS.md`, `P2_BANK_ADVERSARIAL_SCOPE.md`, `P2_BANK_FUZZ_SCALE_SCOPE.md`, `education/README.md` [E]

**Phrase jury :** _"Nos scénarios ne testent pas si l'action réussit. Ils testent si la gouvernance est suivie."_

---

*Extraction READONLY — aucun fichier source modifié.*  
*Généré le 2026-06-10*
