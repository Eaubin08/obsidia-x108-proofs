# CLASSIC vs OBSIDIA — Tableau de comparaison doctrine

> Source : extraction depuis obsidia-x108-proofs_REMOTE_A5F21C6B  
> Marqueurs : [E] = Explicite dans les sources | [I] = Inféré | [P] = Proposé (extension logique)

---

## Lecture du tableau

Chaque ligne oppose :
- **Colonne CLASSIQUE** : ce que la technique fait dans un système standard
- **Colonne OBSIDIA** : ce que la même technique fait dans ta logique, avec les contraintes réelles du code
- **Colonne INVARIANT** : la règle qui ne change jamais dans Obsidia, indépendamment du contexte

---

| Concept | Formulation Classique | Formulation Obsidia | Invariant Obsidia |
|---------|----------------------|---------------------|-------------------|
| **RAG** | Retrieval → augmente la génération → l'agent décide | Context Packet → signal uniquement → X108 décide seul | `decision_authority = "KX108_ONLY"` [E] |
| **RLHF / RCHF** | Feedback humain → reward model → mise à jour poids | Feedback → memory_candidate → APPEND_ONLY → review humaine manuelle | `auto_promotion_blocked = True` [E] |
| **Mémoire** | Base vectorielle interrogeable, mise à jour par l'agent | Strates séparées (candidat / opérationnelle / session / scellée), droits par strate | `memory_write_allowed = False` pour tous agents [E] |
| **Agent** | Entité autonome avec tools, mémoire, boucle d'action | Gate existant wrappé, non-souverain, advisory uniquement | `can_emit_act = false` [E] |
| **Loop** | ReAct / planification autonome itérative | Boucle opérateur : Brody propose, humain valide, puis avance | `brody_execute_allowed = False` [E] |
| **Automatisation** | Pipeline autonome, aucun humain dans la boucle | DRY_RUN_ONLY par défaut, _BOUNDARY tous flags False | `DRY_RUN_ONLY: bool = True` [E] |
| **Brody** | Assistant IA avec capacité d'agir | Moteur advisory-only, 22 arbres, 12 modules, aucune décision | `emits_act = False`, `advisory_only = True` [E] |
| **X108** | Module de scoring ou d'évaluation parmi d'autres | Unique autorité de décision, kernel souverain, 14+ routes | `decision_authority = "KX108_ONLY"` partout [E] |
| **Gouvernance** | Politique de garde-fous, règles d'usage | Chaîne séquentielle avec gates : Cognition → CP → X108 → OS3 → POG → Ticket → Gateway → Bus → Act | Chaque étape = gate bloquant [E] |
| **OS3** | Logger ou audit post-hoc | Proof formelle pré-action : hash, ticket souverain, manifeste replay | Auditabilité native O7 [E] |
| **Contexte** | Input enrichi qui oriente la réponse de l'agent | Signal : enrichit l'évaluation X108, n'autorise rien | "Contexte = signal. Signal ≠ décision." [E] |
| **Capability** | Pouvoir faire = pouvoir agir | Pouvoir générer ≠ autorisation d'agir | Principe STABLE `CAPABILITY_IS_NOT_AUTHORITY` [E] |
| **Mémoire Candidate** | Auto-save, auto-index, retrieval automatique | APPEND_ONLY, promotion manuelle, `requires_human_review = True` | `auto_promotion_blocked = True` [E] |
| **Scénarios Test** | Tests fonctionnels : l'action réussit ou échoue | Épreuves de gouvernance : la chaîne de décision est-elle correctement suivie ? | BLOCK S4 = succès si bloqué par gouvernance [E] |
| **Preuve / Audit** | CI/CD post-commit, tests de régression | OS3-proof pré-action + verify_all + PROOFKIT + Merkle + replay | `PROOFKIT_REPORT.json` ancre RSSI interne [E] |
| **Hackathon** | Démo d'agent autonome résolvant un problème en temps réel | Démo de gouvernance : montrer la chaîne, pas juste le résultat | La valeur = la traçabilité, pas la vitesse [I] |
| **Jeux / Simulateurs** | Environnement gym, reward shaping, épisodes | Bank Scenarios : 3 cas (Normal/Suspicious/Blocked Hard) = tests de souveraineté | BLOCK S4 = gouvernance fonctionnelle [E] |
| **Arbres Cognitifs** | Knowledge graph, ontologie, catégories | 34 Arbres (T01-T34) : map de la cognition avec droits de réponse distincts | T20-T22 bloqués action, T30-T34 bloqués AGI [E] |

---

## Résumé en une phrase par concept

| Concept | Phrase doctrine |
|---------|----------------|
| RAG | Le contexte enrichit — il ne décide pas. |
| RCHF | Le feedback entre en candidature — il ne s'auto-promeut pas. |
| Mémoire | La mémoire s'accumule — elle ne s'écrit pas d'elle-même. |
| Agent | L'agent répond — il n'agit pas. |
| Loop | La boucle propose — l'humain avance. |
| Brody | Brody répond. Brody ne décide pas. |
| X108 | X108 est l'unique juge. Toujours. |
| OS3 | Chaque action laisse une preuve avant d'exister. |
| Gouvernance | Le chemin complet est la seule voie légitime. |
| Capability | Pouvoir ≠ droit. |

---

*Extraction READONLY — aucun fichier source modifié.*  
*Généré le 2026-06-10*
