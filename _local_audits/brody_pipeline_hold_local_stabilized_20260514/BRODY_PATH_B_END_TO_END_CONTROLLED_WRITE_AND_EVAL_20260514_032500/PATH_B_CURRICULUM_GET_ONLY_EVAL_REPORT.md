# PATH_B CURRICULUM GET-ONLY EVAL REPORT
## Phase 6 — BRODY_PATH_B_END_TO_END_CONTROLLED_WRITE_AND_EVAL
## Timestamp: 20260514_032500

---

## Résumé exécutif

Évaluation GET-ONLY de tous les stages curriculum après écriture PATH_B Tier 1.
**5/6 stages EVAL_PASS — 1/6 EVAL_PASS_PARTIAL (MONDE_LARGE, 9 arbres bloqués).**
Aucun write en eval. Node count = 3267 (invariant préservé).

---

## Résultats par stage

| Stage          | Trees requis | Testables | Bloqués | PASS | Verdict              |
|----------------|:------------:|:---------:|:-------:|:----:|----------------------|
| FRANCAIS       | 3            | 3         | 0       | 3    | **EVAL_PASS**        |
| LOGIQUE        | 5            | 5         | 0       | 5    | **EVAL_PASS**        |
| MATHS_SIMPLES  | 6            | 6         | 0       | 6    | **EVAL_PASS**        |
| SCIENCE        | 5            | 5         | 0       | 5    | **EVAL_PASS**        |
| PHYSIQUE       | 6            | 6         | 0       | 6    | **EVAL_PASS**        |
| MONDE_LARGE    | 13           | 4         | 9       | 4    | **EVAL_PASS_PARTIAL**|

---

## Détail par arbre (non-bloqués uniquement)

| Tree | Nom                        | Nodes | Preview | Titres | PASS |
|------|----------------------------|:-----:|:-------:|:------:|:----:|
| T04  | Arbre du Sens              | 4     | 4       | 4      | OUI  |
| T06  | Arbre de la Comprehension  | 4     | 4       | 4      | OUI  |
| T07  | Arbre de l'Organisation    | 4     | 4       | 4      | OUI  |
| T08  | Arbre de la Pensee         | 4     | 4       | 4      | OUI  |
| T09  | Arbre de l'Intelligence    | 4     | 4       | 4      | OUI  |
| T10  | Arbre du Langage           | 4     | 4       | 4      | OUI  |
| T11  | Arbre de la Science        | 4     | 4       | 4      | OUI  |
| T12  | Arbre de la Technique      | 4     | 4       | 4      | OUI  |
| T14  | Arbre de la Philosophie    | 9     | 9       | 9      | OUI  |
| T16  | Arbre de la Relation       | 9     | 9       | 9      | OUI  |
| T17  | Arbre du Collectif         | 9     | 9       | 9      | OUI  |
| T18  | Arbre de la Transmission   | 9     | 9       | 9      | OUI  |
| T19  | Arbre de la Culture        | 9     | 9       | 9      | OUI  |
| T23  | Arbre du Temps             | 9     | 9       | 9      | OUI  |
| T25  | Arbre de l'Histoire        | 9     | 9       | 9      | OUI  |
| T26  | Arbre de la Coherence      | 9     | 9       | 9      | OUI  |
| T27  | Arbre de la Verite         | 9     | 9       | 9      | OUI  |

---

## Arbres bloqués (non testés)

| Tree | Nom                          | Raison                      |
|------|------------------------------|-----------------------------|
| T20  | Arbre de l'Action            | BLOCKED_ACTION_TRIGGER      |
| T21  | Arbre de la Creation         | BLOCKED_ACTION_TRIGGER      |
| T22  | Arbre de la Transformation   | BLOCKED_ACTION_TRIGGER      |
| T24  | Arbre de la Memoire          | BLOCKED_DIRECT_MEMORY_WRITE |
| T30  | Arbre Cognitif Global        | BLOCKED_AGI_LAYER           |
| T31  | Arbre des Flux               | BLOCKED_AGI_LAYER           |
| T32  | Arbre des Connexions         | BLOCKED_AGI_LAYER           |
| T33  | Arbre de l'Optimisation      | BLOCKED_AGI_LAYER           |
| T34  | Arbre de la Stabilite        | BLOCKED_AGI_LAYER           |

---

## Progression curriculum — avant vs après PATH_B

| Stage         | Avant PATH_B        | Après PATH_B          | Delta                        |
|---------------|---------------------|-----------------------|------------------------------|
| FRANCAIS      | EVAL_PASS           | EVAL_PASS             | inchangé (déjà complet)      |
| LOGIQUE       | EVAL_PASS_PARTIAL   | **EVAL_PASS**         | +T26+T27 tagged -> FULL      |
| MATHS_SIMPLES | EVAL_PASS_PARTIAL   | **EVAL_PASS**         | +T26 tagged -> FULL          |
| SCIENCE       | EVAL_PASS_PARTIAL   | **EVAL_PASS**         | +T14+T26+T27 tagged -> FULL  |
| PHYSIQUE      | EVAL_FAIL           | **EVAL_PASS**         | +T23+T25+T26+T27 -> FULL     |
| MONDE_LARGE   | NO_TEST_POSSIBLE    | **EVAL_PASS_PARTIAL** | +T16+T17+T18+T19 testables   |

---

## Invariants vérifiés

- node_count_post_eval = 3267 (inchangé)
- no_write_in_eval = true
- blocked_trees_tagged = 0
- excluded_nodes_unmodified = true (PWV_11)
