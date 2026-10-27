# OBSIDIA CONCEPT DOCTRINE — 15 Concepts expliqués selon la logique Obsidia/X108

> Mode : AUDIT READONLY — extraction depuis sources primaires  
> Source : obsidia-x108-proofs_REMOTE_A5F21C6B (34 fichiers lus)  
> Marqueurs : [EXPLICITE] = tiré verbatim des sources | [INFERE] = déduit de la structure | [PROPOSE] = extension logique non encore codée

---

## 1. RAG — Retrieval-Augmented Generation

**Formulation classique :** embedding + retrieval + génération augmentée.

**Formulation Obsidia :**  
Le RAG n'est pas une technique de génération améliorée — c'est la mécanique du **Context Packet**.  
Le Context Packet est la seule forme légitime d'apport d'information externe dans le système.  
Il porte un invariant absolu : `decision_authority = "KX108_ONLY"`. [EXPLICITE — CONTEXT_PACKET_BUILDER_V2.md]  
Le contexte récupéré est un **signal**, jamais une décision. [EXPLICITE — CONTEXT_SIGNAL_ONLY_POLICY_V1.md]  
Un agent qui reçoit un context packet **ne peut pas** en déduire une autorisation d'agir.

**Mécanisme Obsidia :**
- Ingestion via `/readonly-ingress` (route X108, READONLY) [EXPLICITE — routes/x108.py]
- Fraîcheur évaluée via `/oracle/freshness` [EXPLICITE — routes/x108.py]
- 15 routes sémantiques dans `brody_semantic_query_router.py` orientent la requête vers Neo4j [EXPLICITE]
- Résultat = signal contextuel → transmis à X108, jamais auto-exécuté

**Ce qui ne change PAS :**  
Même si le RAG retourne une réponse parfaite, X108 reste seul juge de l'action.

---

## 2. RCHF / RLHF — Reinforcement from Human/Contextual Feedback

**Formulation classique :** reward model entraîné sur préférences humaines, mise à jour des poids.

**Formulation Obsidia :**  
Le RCHF n'est pas un mécanisme d'entraînement — c'est le **pipeline candidat mémoire**.  
Chaque interaction produit un feedback → lequel devient un `memory_candidate` → stocké en attente. [EXPLICITE — FEEDBACK_MEMORY_CANDIDATE_POLICY_V0.md]

**Règles absolues :**
- `auto_promotion_allowed = False` [EXPLICITE — MEMORY_PROMOTION_MANUAL_ONLY_V1.md]
- `auto_promotion_blocked = True` [EXPLICITE]
- `requires_human_review = True` [EXPLICITE]
- Le ledger est `APPEND_ONLY` [EXPLICITE — MEMORY_CANDIDATE_LEDGER_V1.md]

**Mécanisme Obsidia :**
- Feedback capturé (étape 9 du lifecycle : `FEEDBACK_CAPTURED`) [EXPLICITE — ACTION_LIFECYCLE_CONTRACT_V0.md]
- → `MEMORY_CANDIDATE_BUILT` (étape 10)
- Candidat stocké dans Neo4j via `brody_candidate_memory_adapter.py` [EXPLICITE]
- Promotion : revue humaine unique, jamais automatique
- Dry-run d'import possible via `graphiti_import_dry_run` (module 11 de Brody) [EXPLICITE]

**Ce qui ne change PAS :**  
Brody ne s'auto-améliore pas. Le feedback informe, il ne modifie pas le kernel.

---

## 3. Mémoire

**Formulation classique :** base de connaissances, embeddings, graph, retrieval.

**Formulation Obsidia :**  
La mémoire est une infrastructure à **plusieurs strates distinctes** avec droits stricts par strate.

| Strate | Nature | Droit d'écriture |
|--------|--------|-----------------|
| Candidats | APPEND_ONLY, en attente review | Append uniquement (système) |
| Opérationnelle | Neo4j / Graphiti | Humain après review |
| Session | `session_memory_ledger` (module 5 Brody) | Brody (lecture seule externe) |
| Scellée | `memory/logs/sealed` (route X108) | Aucun — archivé |

**Règle absolue :** `memory_write_allowed = False` pour tous les agents [EXPLICITE — NON_SOVEREIGN_AGENT_CONTRACT_V0.md]  
**Lecture :** `/memory/candidates/read` — route dédiée [EXPLICITE — routes/x108.py]  
**Append candidat :** `/memory/candidates/append` [EXPLICITE — routes/x108.py]  
**Replay :** `/memory/replay/session` et `/memory/replay/coherence` [EXPLICITE — routes/x108.py]

---

## 4. Loop / Boucle Opérateur

**Formulation classique :** boucle ReAct, planification autonome, exécution itérative.

**Formulation Obsidia :**  
La loop n'est pas autonome — c'est une **boucle opérateur-contrôlée**.  
`brody_execute_allowed = False` [EXPLICITE — brody_operator_loop_adapter.py]  
`human_operator_required = True` [EXPLICITE — brody_operator_loop_adapter.py]

**Mécanisme :**  
Brody peut proposer des actions → mais chaque itération de la boucle attend la validation humaine avant de continuer.  
L'adaptateur (`brody_operator_loop_adapter.py`) est l'interface entre la cognition Brody et la boucle d'exécution réelle.

**Ce que la loop fait :**  
- Reçoit l'input → construit un `action_candidate`
- Évalue via PERIPHERY_SCORED → SIGMA_ROUTED → X108_EVALUATED [EXPLICITE — lifecycle]
- Propose le résultat à l'opérateur humain
- Attend l'approbation → seulement alors avance

---

## 5. Automatisation

**Formulation classique :** pipeline automatisé, agents autonomes, no-human-in-loop.

**Formulation Obsidia :**  
L'automatisation Obsidia est **conditionnelle et auditée**, jamais aveugle.  
Chaque script d'automatisation porte `DRY_RUN_ONLY: bool = True` par défaut. [EXPLICITE — tous les scripts audit]  
Le dictionnaire `_BOUNDARY` contient tous les flags d'autorisation à `False`. [EXPLICITE — tous les scripts]  
L'automatisation réelle nécessite un `SovereignTicket` validé par X108. [EXPLICITE — COGNITION_TO_ACTION_GOVERNANCE_V1.md]

**Concrètement :**  
- `brody_full_runtime_orchestrator.py` orchestre 12 modules [EXPLICITE]
- Statuts des modules : LIVE / BLOCKED / OFFLINE / BACKEND_STUB [EXPLICITE]
- Modules bloqués = fonctionnent en mode stub (observables, non exécutants)

---

## 6. Agents

**Formulation classique :** agents autonomes avec mémoire, outils, capacité d'agir.

**Formulation Obsidia :**  
Tous les agents Obsidia sont **non-souverains**. [EXPLICITE — NON_SOVEREIGN_AGENT_CONTRACT_V0.md]  
Contrat d'agent non-souverain (invariants absolus) :
```
can_emit_act = false
can_authorize = false
can_mutate_kernel = false
can_write_memory = false
```

**Principe clé :** Capacité ≠ Autorité [EXPLICITE — CAPABILITY_IS_NOT_AUTHORITY_V1.md]  
Un agent peut générer un output — cela ne l'autorise pas à agir.  
Chaque agent est un **gate existant wrappé**, pas un acteur autonome. [EXPLICITE — AGENT_TO_GATE_MAPPING_V0.md]

**22 arbres Brody (T13-T34) — classification :**
- 13 sûrs (T13-T19, T23, T25-T29) : Art, Philosophie, Spiritualité, Relation, Collectif, Transmission, Culture, Temps, Histoire, Cohérence, Vérité, Valeur, Finalité
- 3 bloqués action (T20-T22) : Action, Création, Transformation
- 1 bloqué mémoire (T24) : Mémoire
- 5 bloqués AGI (T30-T34) : Cognitif Global, Flux, Connexions, Optimisation, Stabilité

---

## 7. Brody

**Ce que Brody n'est pas :** un assistant autonome, un décideur, un acteur.  
**Ce que Brody est :** un moteur de réponse advisory-only. [EXPLICITE — BRODY_NO_DECISION_POLICY_V1.md]

**Formule absolue :** _"Brody répond. Brody ne décide pas."_ [EXPLICITE]  
`advisory_only = True` | `emits_act = False` [EXPLICITE]

**Architecture Brody (12 modules) :**
1. `terminal_structural_dialogue` — dialogue structuré
2. `local_response_engine` — réponse locale
3. `context_packet_query` — requête Context Packet
4. `content_hydration` — hydratation contenu
5. `session_memory_ledger` — ledger session
6. `session_presave_buffer` — buffer pré-sauvegarde
7. `memory_scheduler` — planificateur mémoire
8. `post_human_review_memory_triage` — triage post-review humaine
9. `auto_triage_memory_intake` — intake triage auto (candidats uniquement)
10. `candidate_export_for_graphiti` — export candidat
11. `graphiti_import_dry_run` — dry-run import Graphiti
12. `graphiti_review_gate` — gate review Graphiti

**15 routes sémantiques :**  
X108, 34_ARBRES, OBSIDIA_BRODY_ROLE, RESPONSE_QUALITY, ACTION_BOUNDARY, CREATOR_CONTEXT, MEMORY_QUERY, OPERATOR_LOOP, RIGHTS_ACTION, PROOF_QUERY, GENCOIN, WORLD_MEMORY, CURRENT_STATE, COGNITIVE_LAYERS, TEMPORAL_CONTEXT [EXPLICITE — brody_semantic_query_router.py]

**Matrix droits Brody :**  
22 arbres mappés — `Répondre ≠ Décider` est le principe central. [EXPLICITE — brody_rights_authority_matrix.py]

---

## 8. X108 — Kernel Souverain

**Ce que X108 est :** l'unique autorité de décision du système. [EXPLICITE — partout]  
`decision_authority = "KX108_ONLY"` est un invariant absolu répété dans chaque couche.

**14+ routes de l'API X108 :**
- `POST /cognitive/shazam` — identification cognitive
- `POST /cognitive/dominant-trees` — arbres dominants
- `POST /math/lyapunov` — stabilité Lyapunov
- `POST /math/pog` — Proof of Governance
- `GET /memory/candidates/read` — lecture candidats
- `POST /memory/candidates/append` — append candidat
- `POST /math/trust-path` — chemin de confiance
- `POST /cognitive/regime-classify` — classification régime
- `POST /oracle/freshness` — fraîcheur oracle
- `POST /timeverse/sync` — sync temporelle
- `POST /memory/replay/session` — replay session
- `POST /memory/replay/coherence` — cohérence replay
- `GET /memory/logs/sealed` — logs scellés
- `GET /status` — état système
- `POST /readonly-ingress` — ingestion READONLY

**Boundary X108 (inviolable) :**
```python
_BOUNDARY = {"readonly": True, "emits_act": False}
```
[EXPLICITE — routes/x108.py]

---

## 9. OS3 — Preuve, Ticket, Replay

**Formulation Obsidia :**  
OS3 est la couche de **preuve formelle et d'auditabilité** de chaque action.  
Chaque action critique doit être OS3-ticketée avant d'être exécutée. [EXPLICITE — ACTION_LIFECYCLE_CONTRACT_V0.md]

**Ce qu'OS3 produit :**
- Hash fermé de l'action candidate [EXPLICITE — OS3_PROOF_TICKET_SCHEMA_V0.md]
- Ticket souverain (`SovereignTicket`) [EXPLICITE — COGNITION_TO_ACTION_GOVERNANCE_V1.md]
- Manifeste de replay [EXPLICITE — OS3_REPLAY_MANIFEST_V0.md]

**Loi O7 (Auditabilité Native) :**  
_"Chaque projection, contexte ou signal doit être traçable, rejouable et inspectable."_ [EXPLICITE]

---

## 10. Gouvernance — Chemin Fidèle (Chaîne Complète)

**Formulation Obsidia :**  
La gouvernance est une **chaîne séquentielle avec gates**, pas une architecture plate.

```
Cognition (signal)
  → Context Packet
    → X-108 Kernel (évaluation)
      → OS3 Proof (hash + ticket)
        → ProofOfGovernance
          → SovereignTicket
            → Gateway
              → WorldActionBus
                → Act (si et seulement si tout le chemin est validé)
```
[EXPLICITE — COGNITION_TO_ACTION_GOVERNANCE_V1.md]

**Lifecycle complet (11 étapes) :**
```
INPUT_CAPTURED → ACTION_CANDIDATE_BUILT → PERIPHERY_SCORED →
SIGMA_ROUTED → X108_EVALUATED → OS3_TICKETED →
GENCOIN_EVALUATED → WORLD_ACTION_DRY_RUN_READY →
FEEDBACK_CAPTURED → MEMORY_CANDIDATE_BUILT → CLOSED
```
[EXPLICITE — ACTION_LIFECYCLE_CONTRACT_V0.md]

---

## 11. Capability ≠ Authority

**Formulation Obsidia :**  
_"Pouvoir générer un output ≠ être autorisé à agir."_ [EXPLICITE — CAPABILITY_IS_NOT_AUTHORITY_V1.md]  
Statut : STABLE, core principle.

C'est le principe qui bloque les agents non-souverains : ils peuvent calculer, répondre, proposer — mais aucune capacité technique ne leur confère une autorisation d'agir dans le monde réel.

---

## 12. DRY_RUN_ONLY

**Formulation Obsidia :**  
Pattern de sécurité appliqué dans tous les scripts d'audit et de vérification.

```python
DRY_RUN_ONLY: bool = True
_BOUNDARY = {
    "runtime_modified": False,
    "sigma_modified": False,
    "act_enabled": False,
    "memory_write_enabled": False,
    "graphiti_write_enabled": False,
    "neo4j_write_enabled": False,
    "kernel_mutation_enabled": False,
    "github_pushed": False,
    "github_pr_created": False,
    "public_release_created": False,
    # ... 18 flags au total, tous False
}
```
[EXPLICITE — tous les scripts audit P80]

**Principe :** un script peut vérifier toute la chaîne sans jamais activer une action réelle.  
La preuve d'auditabilité est dissociée de l'autorisation d'exécution.

---

## 13. 34 Arbres — Matrice de Pensée

**Formulation Obsidia :**  
34 arbres organisent la cognition et les droits de réponse de Brody. [EXPLICITE — brody_tree_policy.py]

**Structure complète T01-T34 :**
- T01-T12 : Arbre de l'Humain, Conscience, Perception, Sens, Émotion, Corps, Relation, Collectif, Culture, Temps, Espace, Cosmos
- T13-T29 : Arbres sûrs (Art, Philosophie, Spiritualité, Relation, Collectif, Transmission, Culture, Temps, Histoire, Cohérence, Vérité, Valeur, Finalité, Mémoire-lecture)
- T20-T22 : Bloqués action (Action, Création, Transformation) — `SIGNAL_METHOD=PATH_SLUG`
- T24 : Bloqué mémoire
- T30-T34 : Bloqués AGI (Cognitif Global, Flux, Connexions, Optimisation, Stabilité)

---

## 14. Jeux / Simulateurs / Scénarios Test

**Formulation Obsidia :**  
Les scénarios de test sont des **environnements de simulation gouvernée**.

**Bank Scenarios (3 cas) :**
- Scenario 1 — Normal : ALLOW (chemin standard validé)
- Scenario 2 — Suspicious : pas de ALLOW (signal insuffisant → non-action légitime, O1)
- Scenario 3 — Blocked Hard : BLOCK S4 (blocage structurel, irréversibilité, O2)
[EXPLICITE — docs/BANK_SCENARIOS.md]

**Philosophie :** les scénarios ne sont pas des cas de test fonctionnels — ce sont des **épreuves de gouvernance**. Le succès n'est pas "l'action accomplie" mais "la chaîne de décision correctement suivie".

---

## 15. Source of Truth / Proof Repository

**Formulation Obsidia :**  
`obsidia-x108-proofs` est le **périmètre de preuve et d'audit**. [EXPLICITE — SOURCE_OF_TRUTH_POLICY_V0.md]  
Ce dépôt = preuve, pas runtime.

**8 Lois Constitutionnelles (O1-O8) :**
- O1 : Non-Action Légitime — la non-action peut être le seul choix légitime
- O2 : Irréversibilité Structurelle — toute action irréversible = frontière structurelle
- O3 : Épreuve Temporelle X-108 — action critique = épreuve temporelle préalable + X108
- O4 : Non-Arbitrage Conflit — X108 ne tranche pas les conflits de valeurs
- O5 : Élimination Décisionnelle — réduire les options non-nécessaires
- O6 : Mémoire Négative — ce qui ne doit pas être rappelé est tracé mais non promu
- O7 : Auditabilité Native — tout signal = traçable, rejouable, inspectable
- O8 : Séparation Cognition/Action — cognition = contexte périphérique ; action = souveraineté X108
[EXPLICITE — 02_CONSTITUTION_LOIS_OBSIDIENNES/]

---

*Extraction READONLY — aucun fichier source modifié.*  
*Généré le 2026-06-10 depuis obsidia-x108-proofs_REMOTE_A5F21C6B*
