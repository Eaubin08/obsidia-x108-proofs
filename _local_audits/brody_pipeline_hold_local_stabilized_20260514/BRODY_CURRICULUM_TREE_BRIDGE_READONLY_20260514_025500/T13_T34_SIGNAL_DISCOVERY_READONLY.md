# T13-T34 SIGNAL DISCOVERY — READONLY
## Mission: BRODY_CURRICULUM_TREE_BRIDGE_READONLY
## Timestamp: 20260514_025500
## Result: PATH_B SIGNAL FOUND — 22/22 trees, 117 safe candidates

---

## Méthode de discovery

4 signaux testés en READONLY sur BrodyMemoryDoc (3267 nodes) :

| Signal | Requête | Résultat |
|---|---|---|
| title_regex | `n.title =~ '.*_Tnn__.*'` | 0/22 trees |
| source_path_slug | `n.source CONTAINS folder OR n.path CONTAINS folder` | 22/22 trees |
| text_preview_slug | `n.text_preview CONTAINS folder` | 22/22 trees |
| text_preview_keyword | `n.text_preview CONTAINS keyword` | Bruit — non utilisé |

**Signal retenu : PATH_SLUG** (field = `n.path`)

---

## PATH_B — Découverte clé

Chaque arbre T13-T34 possède **9 BrodyMemoryDoc** dont le champ `path` contient le slug canonique du dossier :

```
n.path CONTAINS 'ARBRE_nn__CanonicalName'
```

### 9 types de documents par arbre

| Titre | Description |
|---|---|
| README.md | Vue d'ensemble de l'arbre |
| activation_rules.md | Règles d'activation |
| definition.md | Définition canonique |
| examples_events.md | Exemples et événements |
| links_to_other_trees.json | Liens inter-arbres |
| node_registry.json | Registre des nœuds |
| risks_confusions.md | Risques et confusions |
| tensor_coordinates.json | Coordonnées tensorielles |
| tests.md | Tests associés |

### Tags existants (uniformes)

Tous ces docs ont déjà : `['34_arbres', 'agents', 'proof', 'source_doc']` (±audit, readonly, x108)

---

## Distribution par arbre

| Arbre | Nom canon | Famille | Path count | Safe | Statut |
|---|---|---|---|---|---|
| T13 | Arbre de l'Art | III_CONNAISSANCE | 9 | ✅ | PATH_B_CANDIDATE |
| T14 | Arbre de la Philosophie | III_CONNAISSANCE | 9 | ✅ | PATH_B_CANDIDATE |
| T15 | Arbre de la Spiritualite | III_CONNAISSANCE | 9 | ✅ | PATH_B_CANDIDATE |
| T16 | Arbre de la Relation | IV_RELATIONNELS_SOCIAUX | 9 | ✅ | PATH_B_CANDIDATE |
| T17 | Arbre du Collectif | IV_RELATIONNELS_SOCIAUX | 9 | ✅ | PATH_B_CANDIDATE |
| T18 | Arbre de la Transmission | IV_RELATIONNELS_SOCIAUX | 9 | ✅ | PATH_B_CANDIDATE |
| T19 | Arbre de la Culture | IV_RELATIONNELS_SOCIAUX | 9 | ✅ | PATH_B_CANDIDATE |
| T20 | Arbre de l'Action | V_ACTION_TRANSFORMATION | 9 | ❌ | BLOCKED_ACTION_TRIGGER |
| T21 | Arbre de la Creation | V_ACTION_TRANSFORMATION | 9 | ❌ | BLOCKED_ACTION_TRIGGER |
| T22 | Arbre de la Transformation | V_ACTION_TRANSFORMATION | 9 | ❌ | BLOCKED_ACTION_TRIGGER |
| T23 | Arbre du Temps | VI_TEMPORELS_MEMORIELS | 9 | ✅ | PATH_B_CANDIDATE |
| T24 | Arbre de la Memoire | VI_TEMPORELS_MEMORIELS | 9 | ❌ | BLOCKED_DIRECT_MEMORY_WRITE |
| T25 | Arbre de l'Histoire | VI_TEMPORELS_MEMORIELS | 9 | ✅ | PATH_B_CANDIDATE |
| T26 | Arbre de la Coherence | VII_META_STRUCTURELS | 9 | ✅ | PATH_B_CANDIDATE |
| T27 | Arbre de la Verite | VII_META_STRUCTURELS | 9 | ✅ | PATH_B_CANDIDATE |
| T28 | Arbre de la Valeur | VII_META_STRUCTURELS | 9 | ✅ | PATH_B_CANDIDATE |
| T29 | Arbre de la Finalite | VII_META_STRUCTURELS | 9 | ✅ | PATH_B_CANDIDATE |
| T30 | Arbre Cognitif Global | VIII_OBSIDIA_AGI | 9 | ❌ | BLOCKED_AGI_LAYER |
| T31 | Arbre des Flux | VIII_OBSIDIA_AGI | 9 | ❌ | BLOCKED_AGI_LAYER |
| T32 | Arbre des Connexions | VIII_OBSIDIA_AGI | 9 | ❌ | BLOCKED_AGI_LAYER |
| T33 | Arbre de l'Optimisation | VIII_OBSIDIA_AGI | 9 | ❌ | BLOCKED_AGI_LAYER |
| T34 | Arbre de la Stabilite | VIII_OBSIDIA_AGI | 9 | ❌ | BLOCKED_AGI_LAYER |

---

## Totaux

| Catégorie | Arbres | Docs |
|---|---|---|
| Safe PATH_B candidates | 13 | 117 |
| Blocked (action/memory/AGI) | 9 | 81 |
| **Total T13-T34** | **22** | **198** |

---

## Prochaine étape

**BRODY_PATH_B_TAGGING_DRY_RUN_READONLY** : générer les 117 candidats d'écriture via PATH_SLUG, passer en gate, puis write autorisé.

Cette écriture étendrait la couverture tagging de 48 → 165 nodes (T01-T29 sauf T20-T22, T24).

---

## Invariants

- Aucune écriture dans cette mission
- Signal découvert en READONLY
- DECISION_AUTHORITY=KX108_ONLY
