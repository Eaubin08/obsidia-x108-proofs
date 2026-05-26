# BRODY TREE POLICY BINDING REPORT
Date: 2026-05-20
Verdict: BRODY_TREE_POLICY_BOUND_PASS

---

## Fichier créé

```
apps/obsidia_api/brody_tree_policy.py
```

Source : `T13_T34_SIGNAL_DISCOVERY_READONLY_20260514_025500`
Signal retenu : `PATH_SLUG` — `n.path CONTAINS slug`

---

## Arbres safe (13 arbres, 117 candidats)

| ID | Nom | Famille |
|---|---|---|
| T13 | Arbre de l'Art | III_CONNAISSANCE |
| T14 | Arbre de la Philosophie | III_CONNAISSANCE |
| T15 | Arbre de la Spiritualite | III_CONNAISSANCE |
| T16 | Arbre de la Relation | IV_RELATIONNELS_SOCIAUX |
| T17 | Arbre du Collectif | IV_RELATIONNELS_SOCIAUX |
| T18 | Arbre de la Transmission | IV_RELATIONNELS_SOCIAUX |
| T19 | Arbre de la Culture | IV_RELATIONNELS_SOCIAUX |
| T23 | Arbre du Temps | VI_TEMPORELS_MEMORIELS |
| T25 | Arbre de l'Histoire | VI_TEMPORELS_MEMORIELS |
| T26 | Arbre de la Coherence | VII_META_STRUCTURELS |
| T27 | Arbre de la Verite | VII_META_STRUCTURELS |
| T28 | Arbre de la Valeur | VII_META_STRUCTURELS |
| T29 | Arbre de la Finalite | VII_META_STRUCTURELS |

Usage : signal contextuel readonly — pas de déclencheur d'action.

---

## Arbres bloqués (9 arbres, 81 documents)

### BLOCKED_ACTION_TRIGGER — T20, T21, T22 (V_ACTION_TRANSFORMATION)

| ID | Nom |
|---|---|
| T20 | Arbre de l'Action |
| T21 | Arbre de la Creation |
| T22 | Arbre de la Transformation |

Ne peuvent pas être utilisés comme déclencheurs d'action.
Peuvent être cités comme contexte conceptuel.

### BLOCKED_DIRECT_MEMORY_WRITE — T24 (VI_TEMPORELS_MEMORIELS)

| ID | Nom |
|---|---|
| T24 | Arbre de la Memoire |

Ne peut pas déclencher d'écriture Graphiti/Neo4j directe.

### BLOCKED_AGI_LAYER — T30-T34 (VIII_OBSIDIA_AGI)

| ID | Nom |
|---|---|
| T30 | Arbre Cognitif Global |
| T31 | Arbre des Flux |
| T32 | Arbre des Connexions |
| T33 | Arbre de l'Optimisation |
| T34 | Arbre de la Stabilite |

Ne peuvent pas activer de couche décisionnelle AGI.

---

## Intégration

La politique est intégrée dans `brody_rights_authority_matrix.py` :
- `TREE_SIGNAL_REQUEST` → `CONTEXT_DIAGNOSTIC` → réponse liste arbres safe/bloqués
- `tree_policy` est attaché à chaque `authority_snapshot`

La politique est aussi intégrée dans `brody_v1_4_12a_final_answer_adapter.py` :
- `response_mode == "CONTEXT_DIAGNOSTIC"` + `request_type == TREE_SIGNAL_REQUEST` → pool `tree_signal`
- Le final_answer liste les arbres safe et bloqués avec leurs raisons

---

## API

`authority_snapshot.tree_policy` est présent dans chaque réponse `/api/brody/chat` :
```json
{
  "safe_trees": ["T13", "T14", "T15", "T16", "T17", "T18", "T19",
                 "T23", "T25", "T26", "T27", "T28", "T29"],
  "safe_count": 13,
  "safe_docs": 117,
  "blocked_action": ["T20", "T21", "T22"],
  "blocked_memory": ["T24"],
  "blocked_agi": ["T30", "T31", "T32", "T33", "T34"],
  "signal_method": "PATH_SLUG",
  "total_trees": 22,
  "blocked_total": 9
}
```

---

## Tests

```
tests/api/test_brody_tree_policy.py — 42 tests PASS
  - get_tree_policy_snapshot: counts, lists, source
  - is_tree_safe / is_tree_blocked: T13-T34 all classified correctly
  - get_tree_usage_note: safe, blocked_action, blocked_memory, blocked_agi, summary
  - API: authority_snapshot.tree_policy present in all requests
  - Blocked trees: no action trigger in API
```

---

## Verdict

```
BRODY_TREE_POLICY_BOUND_PASS
```
