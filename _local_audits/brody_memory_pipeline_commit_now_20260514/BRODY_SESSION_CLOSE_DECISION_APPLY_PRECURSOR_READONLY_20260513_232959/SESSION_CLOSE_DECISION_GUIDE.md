# SESSION_CLOSE_DECISION_GUIDE
**Timestamp :** 20260513_232959  
**Mode :** READONLY — Template à remplir — NO_APPLY  
**Autorité :** KX108_ONLY

---

## Objectif

Ce guide accompagne `SESSION_CLOSE_DECISION_TEMPLATE.jsonl`.

Le template contient 51 candidats mémoire issus de la session 2026-05-13.  
Pour chaque candidat, l'opérateur humain renseigne `human_decision` et `reason`.

Ces décisions débloquent ensuite `post_human_review_memory_triage_readonly`.

---

## Classes de décision

| Classe | Définition | Effet sur la mémoire |
|---|---|---|
| **CRISTAL** | Connaissance stable, sources + matière + axes + résonance. Valeur durable. | Candidat pour import Graphiti (après post_human_review + graphiti_candidate_prep) |
| **TRANSITION** | Structure partielle. Nécessite revue humaine. Valeur potentielle mais incertaine. | Mis en attente — ne passe pas en mémoire sans décision CRISTAL explicite |
| **NEANT** | Commande terminal, artefact jetable, aucune valeur mémorielle. | Rejeté — ne va pas en mémoire |
| **REFLEX** | Alerte reflex détectée (kernel_mutation, x108_merge, etc.). Valeur possible mais risque boundary. | Revue humaine obligatoire avant tout traitement |

---

## Règles de remplissage

1. `human_decision` : l'une de `"CRISTAL"`, `"TRANSITION"`, `"NEANT"`, `"REFLEX"`.
2. `reason` : phrase courte justifiant la décision (max 200 chars).
3. `allowed_for_post_human_review` : `true` si CRISTAL ou TRANSITION explicitement retenu, `false` si NEANT.
4. Ne jamais modifier `memory_write_allowed`, `graphiti_write_allowed`, `neo4j_write_allowed` — toujours `false`.
5. Ne pas appliquer les décisions — ce fichier est un template opérateur uniquement.

---

## Précurseur requis par post_human_review

Le module `post_human_review_memory_triage_readonly_v1.py` vérifie :

```
source_summary.status == BRODY_SESSION_CLOSE_DECISION_APPLY_READONLY_V1_PASS
gate_patch == V1_3_CANONICAL_POINTER_RECORDS_SUPPORT_FALLBACK
len(decisions) == 51 exactement
```

Ce template produit les 51 décisions requises. Une fois rempli, il génère le précurseur.

---

## Groupes de candidats

| Groupe | Source | Candidats |
|---|---|---|
| A | Auto-triage test records (session_ledger_test.jsonl) | 5 |
| B | Reflex test (kernel_mutation + x108_merge) | 1 |
| C | Real-state classification components (decision_matrix.csv) | 16 |
| D | Session audit steps (GROUP_A directories, steps 1-8) | 18 |
| E | Artefacts session courante (TLA, LOW_MATERIAL, patch, etc.) | 11 |
| **Total** | | **51** |

---

## Guardrails — ne jamais lever

```
memory_write_allowed   = false  (always)
graphiti_write_allowed = false  (always)
neo4j_write_allowed    = false  (always)
DECISION_AUTHORITY     = KX108_ONLY
```
