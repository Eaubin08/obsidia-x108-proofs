# OBSIDIA METRICS FROM DOCTRINE — Métriques issues de la logique Obsidia uniquement

> Mode : AUDIT READONLY — extraction depuis sources primaires  
> **Principe :** ces métriques ne viennent pas d'un framework externe (MLflow, W&B, etc.)  
> Elles émergent directement des invariants, contrats et lifecycle documentés dans les sources.  
> Marqueurs : [E] = Explicite | [I] = Inféré de la structure | [P] = Proposé (logique cohérente)

---

## Catégorie 1 — Métriques de Gouvernance (Chaîne de décision)

Ces métriques évaluent si la **chaîne de gouvernance est respectée**, pas si l'action a réussi.

### 1.1 — Completion Rate Lifecycle

**Définition :** taux d'actions qui complètent les 11 étapes sans court-circuit.  
**Source :** ACTION_LIFECYCLE_CONTRACT_V0.md [E]  
**Formule :** `nb_actions_CLOSED / nb_actions_INPUT_CAPTURED`  
**Attendu :** 100% — aucun saut de gate documenté  
**Signaux d'alerte :** action CLOSED sans passage par OS3_TICKETED [I]

### 1.2 — Gate Pass Rate par étape

**Définition :** pour chaque gate, taux de passage vs blocage.

| Gate | Étape | Métrique |
|------|-------|----------|
| PERIPHERY_SCORED | Scoring périphérie | % d'actions scorées |
| X108_EVALUATED | Évaluation souveraine | % évaluées par X108 |
| OS3_TICKETED | Preuve formelle | % avec SovereignTicket |
| WORLD_ACTION_DRY_RUN_READY | Readiness | % dry-run ready |

[I depuis lifecycle]

### 1.3 — Taux de Non-Action Légitime (O1)

**Définition :** taux d'actions stoppées légitimement avant exécution.  
**Source :** O1_NON_ACTION_LEGITIME.md [E]  
**Formule :** `nb_non_actions_legitimes / nb_actions_candidates`  
**Interprétation :** un taux élevé = gouvernance fonctionnelle, pas un échec système.

### 1.4 — Taux de Blocage Structurel (O2 / BLOCK S4)

**Définition :** taux d'actions bloquées pour irréversibilité détectée.  
**Source :** O2_IRREVERSIBILITE_STRUCTURELLE.md + Bank Scenarios [E]  
**Attendu :** 100% des Scenario 3 (Blocked Hard) → BLOCK S4 [E]

---

## Catégorie 2 — Métriques de Mémoire / RCHF

Ces métriques évaluent la santé du **pipeline candidat mémoire**.

### 2.1 — Taux d'Accumulation Candidats

**Définition :** nb de candidats mémoire créés par session.  
**Source :** MEMORY_CANDIDATE_LEDGER_V1.md + FEEDBACK_MEMORY_CANDIDATE_POLICY_V0.md [E]  
**Formule :** `nb_MEMORY_CANDIDATE_BUILT / nb_FEEDBACK_CAPTURED`  
**Attendu :** égal à 1 (chaque feedback → 1 candidat) [I]

### 2.2 — Taux de Review Humaine

**Définition :** proportion de candidats ayant reçu une review humaine.  
**Source :** MEMORY_PROMOTION_MANUAL_ONLY_V1.md [E]  
**Formule :** `nb_candidats_reviewed / nb_candidats_ledger`  
**Attendu :** review avant toute promotion — taux de promotion sans review = 0 [E]

### 2.3 — Zero Auto-Promotion Rate

**Définition :** confirmation que `auto_promotion_blocked = True` est respecté.  
**Source :** MEMORY_PROMOTION_MANUAL_ONLY_V1.md [E]  
**Formule :** `nb_promotions_auto / total_promotions` = 0 strictement  
**Violation :** si > 0 → breach du contrat [E]

### 2.4 — Dry-Run Import Rate

**Définition :** proportion d'imports Graphiti passant par le dry-run (module 11).  
**Source :** brody_full_runtime_orchestrator.py [E]  
**Attendu :** 100% avant tout import réel [E]

---

## Catégorie 3 — Métriques de Signal Contextuel (RAG)

Ces métriques évaluent la **qualité du signal** produit par le Context Packet.

### 3.1 — Fraîcheur Oracle

**Définition :** âge moyen du contexte récupéré (staleness).  
**Source :** `POST /oracle/freshness` [E]  
**Formule :** timestamp_signal vs timestamp_now → delta moyen  
**Attendu :** défini par le seuil oracle configuré dans X108 [I]

### 3.2 — Route Sémantique Hit Rate

**Définition :** taux de requêtes matchant une route sémantique connue (vs fallback).  
**Source :** brody_semantic_query_router.py — 15 routes [E]  
**Formule :** `nb_requetes_routees / nb_requetes_total`  
**Attendu :** proche de 1 pour une session bien cadrée [I]

### 3.3 — Signal → Décision Leak Rate

**Définition :** taux d'instances où un signal contextuel a produit une décision sans passage par X108.  
**Source :** CONTEXT_SIGNAL_ONLY_POLICY_V1.md [E]  
**Attendu :** 0 strictement — invariant absolu [E]  
**Violation :** si > 0 → breach de l'invariant fondamental

---

## Catégorie 4 — Métriques d'Auditabilité (OS3)

Ces métriques évaluent la **complétude de la trail d'audit**.

### 4.1 — Proof Coverage

**Définition :** proportion d'actions avec un SovereignTicket OS3.  
**Source :** OS3_PROOF_TICKET_SCHEMA_V0.md [E]  
**Formule :** `nb_actions_OS3_ticketed / nb_actions_X108_evaluated`  
**Attendu :** 100% [E]

### 4.2 — Replay Coherence Score

**Définition :** taux de sessions rejouables avec résultat cohérent.  
**Source :** `POST /memory/replay/coherence` [E]  
**Attendu :** cohérence totale → score = 1.0 pour sessions bien formées [I]

### 4.3 — Sealed Logs Integrity

**Définition :** vérification que les logs scellés n'ont pas été modifiés post-scellement.  
**Source :** `GET /memory/logs/sealed` [E]  
**Mécanisme :** hash comparison à chaque lecture [I]

---

## Catégorie 5 — Métriques de Boundary (Sécurité Doctrine)

Ces métriques vérifient que **les flags de boundary restent à False**.

### 5.1 — Boundary Violation Rate

**Définition :** nb de fois où un flag `_BOUNDARY` passe à True sans autorisation.  
**Source :** tous les scripts audit (18 flags) [E]  
**Attendu :** 0 strictement — chaque violation est un breach [E]

**Flags surveillés :**
```python
runtime_modified, sigma_modified, routes_modified, srl_modified,
connectors_modified, source_packs_modified, proofs_modified,
lean_proofs_modified, act_enabled, memory_write_enabled,
graphiti_write_enabled, neo4j_write_enabled, kernel_mutation_enabled,
x108_merge_enabled, github_pushed, github_pr_created,
public_release_created
```
[E — scripts audit]

### 5.2 — DRY_RUN_ONLY Compliance

**Définition :** tous les scripts d'audit exécutés en mode dry-run.  
**Source :** tous les scripts P80 [E]  
**Attendu :** `DRY_RUN_ONLY: bool = True` présent dans chaque script [E]

---

## Catégorie 6 — Métriques Cognitives (Arbres / Lyapunov)

Ces métriques évaluent la **santé cognitive du système**.

### 6.1 — Arbre Dominant Score

**Définition :** quels arbres T01-T34 sont dominants dans une session.  
**Source :** `POST /cognitive/dominant-trees` [E]  
**Utilisation :** détecter si des arbres bloqués (T20-T34) sont sur-activés [I]

### 6.2 — Lyapunov Stability Index

**Définition :** mesure la stabilité de la trajectoire cognitive.  
**Source :** `POST /math/lyapunov` [E]  
**Interprétation :** valeur proche de 0 = trajectoire stable ; divergence = instabilité [I]

### 6.3 — Cognitive Regime Classification

**Définition :** quel régime cognitif est actif (exploration / exploitation / blocage).  
**Source :** `POST /cognitive/regime-classify` [E]  
**Utilisation :** adapter la stratégie de réponse selon le régime [I]

### 6.4 — Trust Path Depth

**Définition :** longueur du chemin de confiance validé par X108.  
**Source :** `POST /math/trust-path` [E]  
**Interprétation :** chemin plus long = plus de gates validés = plus de confiance [I]

---

## Résumé — Métriques prioritaires pour une démo hackathon

| Métrique | Valeur cible | Ce qu'elle prouve |
|---------|-------------|------------------|
| Zero Auto-Promotion Rate | 0.0 | RCHF Obsidia respecté |
| Signal → Décision Leak Rate | 0.0 | Invariant Context Signal Only |
| Boundary Violation Rate | 0.0 | Aucun breach de gouvernance |
| Proof Coverage (OS3) | 1.0 | Auditabilité native complète |
| Gate Pass Rate X108 | 1.0 | Toutes les actions passent par le kernel |
| Taux Non-Action Légitime (O1) | variable | Gouvernance active — pas juste performance |
| BLOCK S4 sur Scenario 3 | 100% | Irréversibilité correctement bloquée |

---

*Extraction READONLY — aucun fichier source modifié.*  
*Généré le 2026-06-10*
