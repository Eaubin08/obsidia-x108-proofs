# PROPOSED TAGGING RULES — READONLY
## Mission: BRODY_CANONICAL_TREE_TAGGING_BRIDGE_READONLY
## Timestamp: 20260514_012910
## Status: PROPOSAL_ONLY — requires KX108 gate before execution
## Decision authority: KX108_ONLY

---

## Règles fondamentales (non négociables)

### RULE_01 — Source unique autorisée
La **seule** source autorisée pour assigner un `canonical_tree_id` est `arbres_34.canon.json`.
Aucune autre source ne peut servir de base pour l'assignation d'un arbre ou d'une famille.

### RULE_02 — Extraction tree_id par regex titre uniquement
L'extraction du tree_id DOIT utiliser l'expression régulière `_T(\d+)__` sur le champ `BrodyMemoryDoc.title` uniquement.
Zéro devinette. Zéro inférence sémantique. Zéro match approximatif.

```python
import re
match = re.search(r'_T(\d+)__', title)
if match:
    tree_num = match.group(1).zfill(2)   # "4" → "04"
    canonical_tree_id = f"T{tree_num}"    # "T04"
```

### RULE_03 — Assignation famille via lookup arbres_34.canon.json uniquement
La `canonical_family_id` DOIT provenir du lookup `id → family` dans `arbres_34.canon.json`.
Format id dans le fichier : `"01".."34"` (numeric string, pas `T01`).
Lookup : `id == tree_num` → `family` (ex: `"04"` → `"I_FONDAMENTAUX"`).

### RULE_04 — Zéro heuristique
`no_heuristic_tagging = true`
Aucune règle de type "si le titre contient 'mémoire' alors T24". Interdit.

### RULE_05 — Zéro LLM-guess
`no_llm_guessing = true`
Le LLM ne peut pas assigner une famille à partir du contenu textuel du document. Interdit.

### RULE_06 — Zéro invention
`no_invention = true`
Aucune famille inventée (pas de "API_FAMILY", "WEB_FAMILY", "BUSINESS_FAMILY", etc.).
Les familles autorisées sont strictement : I_FONDAMENTAUX, II_COGNITIFS, III_SOCIAUX, IV_OPERATIONNELS, V_SYSTEMIQUES, VI_DYNAMIQUES, VII_META_STRUCTURELS, VIII_OBSIDIA_AGI.

### RULE_07 — Append-only — tags existants préservés
Les tags existants sur un BrodyMemoryDoc ne doivent **jamais** être supprimés.
Opération : append uniquement. Les `new_tags_proposed` s'ajoutent à `existing_tags_preserved`.

### RULE_08 — PENDING_ADDITIONAL_SIGNAL pour docs sans _Tnn__
Tout BrodyMemoryDoc dont le title ne contient pas `_Tnn__` DOIT être marqué `PENDING_ADDITIONAL_SIGNAL`.
`boundary_status = NOT_TAGGABLE_PENDING_SIGNAL`.
Aucune action d'écriture sur ces documents.

### RULE_09 — Gate KX108 obligatoire avant toute écriture
`boundary_all_false = true` jusqu'à ouverture du gate.
Toute écriture Neo4j (`SET n.tags = ...`) nécessite :
1. KX108 gate explicitement ouvert
2. WRITABLE_MEMORY_PROTOCOL activé
3. human_operator_required = true à chaque écriture

### RULE_10 — boundary_all_false jusqu'à ouverture du gate
`neo4j_write = false`
`graphiti_write = false`
`memory_intake = false`
`runtime_binding_allowed = false`
Tant que le gate n'est pas ouvert par l'opérateur.

---

## Règles de qualité (tagging basis)

| Situation | tagging_basis | confidence_source_based | boundary_status |
|---|---|---|---|
| `_Tnn__` trouvé dans title | TITLE_REGEX_MATCH | 0.99 | TAGGABLE_WITH_GATE |
| Tree_id trouvé, lookup canon OK | REGISTRY_LOOKUP | 0.99 | TAGGABLE_WITH_GATE |
| Pas de `_Tnn__` dans title | PENDING_ADDITIONAL_SIGNAL | 0.0 | NOT_TAGGABLE_PENDING_SIGNAL |
| Opérateur fournit mapping explicite | OPERATOR_EXPLICIT | 1.0 | TAGGABLE_WITH_GATE |
| Heuristique / LLM-guess | HEURISTIC / LLM_GUESS | INTERDIT | BLOCKED |

---

## Règles de confidence

- `confidence_source_based = 0.99` : match structurel direct `_Tnn__` + lookup canon → résultat certain
- `confidence_source_based = 0.0` : aucun signal structurel dans le titre → ne pas taguer
- `confidence_source_based < 0.5` : non taggable sans signal supplémentaire
- Seuil minimum pour écriture : `0.9` (source_based uniquement, jamais LLM-inféré)

---

## Tags autorisés à ajouter (PATH_A)

Pour chaque BrodyMemoryDoc avec `_Tnn__` confirmé :
- `T{nn}` — ex: `T04`
- `canonical_family_id` — ex: `I_FONDAMENTAUX`
- `canonical_tree_name` — ex: `Arbre_du_Sens` (optionnel, opérateur décide)
- `folder_slug` — ex: `ARBRE_04__Arbre_du_Sens` (optionnel, opérateur décide)

---

## Séquence d'exécution PATH_A (READONLY design uniquement)

```
1. Charger arbres_34.canon.json → dict {id: {name, folder, family}}
2. MATCH (n:BrodyMemoryDoc) WHERE n.tags CONTAINS '34_arbres' RETURN n.id, n.title, n.tags
3. Pour chaque doc : regex _T(\d+)__ sur title
4. Si match : lookup canon → {tree_id, family_id, tree_name, folder_slug}
5. Construire CANONICAL_MEMORY_TAGGING_UNIT
6. boundary_status = TAGGABLE_WITH_GATE, requires_operator_review = true
7. Stocker dans TAGGING_DRY_RUN_PLAN.jsonl (READONLY — pas d'écriture Neo4j)
8. Soumettre pour KX108 gate review
9. Si gate open : SET n.tags = n.tags + [T{nn}, family_id] (append only)
10. Valider : MATCH (n:BrodyMemoryDoc) WHERE 'T04' IN n.tags RETURN count(n)
```

---

## Invariants vérifiables

```
ASSERT: count(existing_tags_before) <= count(tags_after)          # append only
ASSERT: canonical_tree_id MATCHES ^T(0[1-9]|[12][0-9]|3[0-4])$  # T01..T34
ASSERT: canonical_family_id IN [I_FONDAMENTAUX..VIII_OBSIDIA_AGI] # 8 familles
ASSERT: tagging_basis != HEURISTIC                                  # no heuristic
ASSERT: tagging_basis != LLM_GUESS                                 # no LLM guess
ASSERT: confidence_source_based >= 0.9 OR boundary_status = NOT_TAGGABLE
```
