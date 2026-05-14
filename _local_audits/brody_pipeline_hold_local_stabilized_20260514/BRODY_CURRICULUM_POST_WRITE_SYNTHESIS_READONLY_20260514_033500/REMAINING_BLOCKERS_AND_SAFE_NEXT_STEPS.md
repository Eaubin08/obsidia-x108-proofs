# REMAINING BLOCKERS AND SAFE NEXT STEPS
## BRODY_CURRICULUM_POST_WRITE_SYNTHESIS_READONLY
## Timestamp: 20260514_033500

---

## Blockers actifs

### BLOCKER_1 — PATH_B Tier 2 non écrit (78 candidats TEXT_PREVIEW_GENUINE)

| Propriété | Valeur |
|-----------|--------|
| Signal | TEXT_PREVIEW_SLUG (confidence 0.88) |
| Candidats | 78 nodes |
| Statut | REVIEW_REQUIRED — gate opérateur non ouvert |
| Impact curriculum | MONDE_LARGE : +0 (ces nodes appartiennent aux mêmes arbres T13-T19/T23/T25-T29) |
| Prochaine étape | BRODY_CANONICAL_TAGGING_TIER2_DRY_RUN_READONLY + gate |
| Phrase de déblocage | "J'autorise l'écriture PATH_B Tier 2 des 78 candidats TEXT_PREVIEW_GENUINE valides" |

### BLOCKER_2 — MONDE_LARGE partiel (9 arbres bloqués par design)

| Propriété | Valeur |
|-----------|--------|
| Arbres bloqués | T20/T21/T22 (ACTION_TRIGGER), T24 (DIRECT_MEMORY_WRITE), T30-T34 (AGI_LAYER) |
| Impact | MONDE_LARGE restera EVAL_PASS_PARTIAL jusqu'à déverrouillage explicite |
| Raison du blocage | Pas un problème de signal — décision architecturale opérateur |
| Prochaine étape | PATH_C (nouveau périmètre) — nécessite décision opérateur arbre par arbre |
| Note | T16/T17/T18/T19 = EVAL_PASS (4/4 testables passent) |

### BLOCKER_3 — MULTI_TREE ambiguity non résolue (2 nodes)

| Propriété | Valeur |
|-----------|--------|
| Node | GRAPHITI_V2_000694 (demo_output_context_packet.json) |
| Problème | Apparaît dans T18 ET T26 — impossible d'assigner un seul arbre sans décision opérateur |
| Statut | REVIEW_REQUIRED_MULTI_TREE — exclu de tous les plans actifs |
| Prochaine étape | Inspection opérateur : quelle famille est canonique ? |

### BLOCKER_4 — GROUP_A commit en attente (136 fichiers stagés)

| Propriété | Valeur |
|-----------|--------|
| Fichiers stagés | 136 |
| Message préparé | "audit: Brody readonly steps 1-8 + sigma cleanup 2026-05-13" |
| Statut | Dry-run fait. Aucun commit sans autorisation explicite. |
| Prochaine étape | Autorisation opérateur → git commit |

### BLOCKER_5 — Schéma mémoire utilisateur non déployé

| Propriété | Valeur |
|-----------|--------|
| Labels manquants | BrodyUserMemory, BrodyAgentMemory, BrodySessionMemory, BrodyCaseMemory, BrodyBoundaryMemory |
| Statut | PENDING — pipeline stable mais schema non actif |
| Impact | BrodyMemoryDoc reste "fourre-tout" — separation en couches non faite |
| Prochaine étape | BRODY_MEMORY_SCHEMA_DESIGN_READONLY (design seul, readonly) |

### BLOCKER_6 — Runtime binding non autorisé

| Propriété | Valeur |
|-----------|--------|
| Statut | RUNTIME_BINDING_ALLOWED = false |
| Raison | X108_MERGE non autorisé. Décision KX108_ONLY. |
| Prochaine étape | BRODY_RUNTIME_BINDING_RISK_REVIEW_READONLY (parallel-available) |

---

## Prochains paliers recommandés

### Palier A — Immédiat, sans risque (recommandé en premier)

**Option A1 : GROUP_A commit**
- 136 fichiers stagés — dry-run fait
- Message déjà préparé
- Risque : faible (commits audit)
- Trigger : "Commit GROUP_A"

**Option A2 : BRODY_RUNTIME_BINDING_RISK_REVIEW_READONLY**
- Audit readonly en parallèle
- Aucun write requis
- Évalue les risques du runtime binding avant PATH_C
- Trigger : lancer la mission

### Palier B — Expansion corpus (après A)

**BRODY_CANONICAL_TAGGING_TIER2_DRY_RUN_READONLY**
- Sécurise les 78 candidats TEXT_PREVIEW_GENUINE
- Produit plan JSONL Tier 2 + gate
- Augmente couverture par arbre (9→18 nodes par tree si validé)
- Trigger : lancer la mission (readonly), puis gate opérateur

### Palier C — Déblocage MONDE_LARGE (décision opérateur requise)

**PATH_C : déblocage arbre par arbre**
- T20-T22 : évaluer si action_trigger requis ou supprimable
- T24 : évaluer si direct_memory_write peut être sandboxé
- T30-T34 : évaluer maturité AGI-layer
- Trigger : décision opérateur explicite par arbre + gate KX108

### Palier D — Schema mémoire (planification long terme)

**BRODY_MEMORY_SCHEMA_DESIGN_READONLY**
- Définir 5 labels manquants
- Mapper BrodyMemoryDoc existant vers couches
- Prépare séparation user/agent/session/case/boundary
- Trigger : lancer la mission (readonly)

---

## Ce qui ne requiert pas d'action supplémentaire

- LOW_MATERIAL : RESOLVED
- External fetch GET-only : VALIDATED
- Boucle opérateur : VALIDATED
- FRANCAIS/LOGIQUE/MATHS_SIMPLES/SCIENCE/PHYSIQUE : EVAL_PASS
- Rollback disponible : PATH_A + PATH_B plans prêts
- BrodyImportedMemory batch : stable, intègre
