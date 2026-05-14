# BRODY CANONICAL TREE TAGGING BRIDGE — READONLY REPORT
## Mission: BRODY_CANONICAL_TREE_TAGGING_BRIDGE_READONLY
## Timestamp: 20260514_012910
## Status: COMPLETE | READONLY
## Decision authority: KX108_ONLY

---

## Problème initial

**FAMILY_LEVEL_TAGGING_ABSENT** — identifié lors de BRODY_WORLD_TREE_GET_ONLY_TEST_READONLY (20260514_011350).

- `34_arbres` tag présent sur **2739/3267** BrodyMemoryDoc
- Tags famille spécifiques (I_FONDAMENTAUX, T01, T04, etc.) : **0 nodes**
- Conséquence : impossible de filtrer le corpus par famille/arbre dans Neo4j
- Bloquant pour : séparation couches mémoire (BrodyUserMemory, BrodyAgentMemory, etc.)

---

## Q1 — Quelle source canonique utiliser pour le tagging ?

**Réponse : arbres_34.canon.json (SRC_001)**

- Path: `obsidia-engine-candidate/.../04_ARBRES_34_TENSOR_MATRIX/arbres_34.canon.json`
- Contenu : 34 arbres, champs `id` (01..34), `name`, `folder`, `family`, `non_decision`
- Statut : STABLE_FREEZE
- Confidence : 0.99
- Également disponible : `arbres_34.registry.json` (SRC_002) — complémentaire

---

## Q2 — Les métriques kernel IR peuvent-elles être utilisées ?

**Réponse : NON — advisory seulement**

L'IR Alphabet (READ, PARSE, NORMALIZE, PROJECT_CONTEXT, TRACE, AUDIT...) définit des **opérations**, pas des appartenances famille-arbre. Assigner un BrodyMemoryDoc à une famille via ces tokens nécessiterait une table de mapping explicite — ce qui constituerait une heuristique. **BLOQUÉ** par règle anti-invention.

---

## Q3 — L'alphabet Reverse OS peut-il être utilisé ?

**Réponse : NON — potentiel futur uniquement**

`reverse_os_interlanguage_canon_v1.json` contient des concepts avec domaines (memoire_fractale, agents_obsidiens) mais **aucun tree_id/family_id explicite**. Inférer la famille = heuristique. `reverse_os.registry.json` = vide (`{}`). Potentiel futur si opérateur fournit table concept→arbre.

---

## Q4 — OS Trad / Reverse Language peuvent-ils être utilisés ?

**Réponse : NON**

`test_T01_T02_os_trad_module.py` : T01/T02 dans les noms de fonctions = **IDs de TEST**, pas IDs d'arbres (coïncidence de nomenclature). OS Trad = protocole de traduction/proposition d'opérations, pas taxonomie arbre-famille.

---

## Q5 — Combien de docs sont directement taggables ?

**Réponse : 48 sur 2739 (1.8%)**

- 48 BrodyMemoryDoc ont `_Tnn__` dans le titre → match structurel direct → confidence 0.99
- 2691 restants : `PENDING_ADDITIONAL_SIGNAL` — ne peuvent pas être taggés sans signal explicite
- 528 docs n'ont pas le tag `34_arbres` — hors corpus

---

## Q6 — Quel chemin de tagging est recommandé ?

**Réponse : PATH_A — registry_34_tree_direct**

| Chemin | Statut | Maturity | Confidence | Coverage |
|---|---|---|---|---|
| **PATH_A** — registry_34_tree_direct | **READY_PENDING_GATE** | HIGH | 0.99 | 48 (1.8%) |
| PATH_B — kernel_metric_bridge | BLOCKED | NONE | 0.10 | — |
| PATH_C — alphabet_bridge | BLOCKED | LOW | 0.20 | — |
| PATH_D — os_trad_reverse_language_bridge | BLOCKED | NONE | 0.05 | — |
| PATH_E — hybrid_bridge | PENDING_OPERATOR_INPUT | LOW | 0.70 | — |

---

## Q7 — Comment fonctionne PATH_A ?

```
1. Charger arbres_34.canon.json → dict {id: {name, folder, family}}
2. MATCH (n:BrodyMemoryDoc) WHERE n.tags CONTAINS '34_arbres'
3. Pour chaque doc : regex _T(\d+)__ sur BrodyMemoryDoc.title
4. Si match : tree_num = zfill(2) → lookup → {T{nn}, family_id, tree_name, folder_slug}
5. Construire CANONICAL_MEMORY_TAGGING_UNIT (boundary_status=TAGGABLE_WITH_GATE)
6. Stocker dans TAGGING_DRY_RUN_PLAN.jsonl — pas d'écriture Neo4j
7. Soumettre PLAN.jsonl pour KX108 gate review
8. Si gate open : SET n.tags = n.tags + [T{nn}, family_id]  -- append only
```

**Exemples :**

| Title | Tree ID | Family |
|---|---|---|
| `003BEA03EEDD_T04__Consensus_Distribue_Resonance_semantique.md` | T04 | I_FONDAMENTAUX |
| `56C8CDE2F94D_T01__Reduction_Incertitude_Audit_coherence.md` | T01 | I_FONDAMENTAUX |
| `2C6000D53716_T02__Gardien_de_fond__Conscience_Distribuee_Validation_reciprocite.md` | T02 | I_FONDAMENTAUX |

---

## Q8 — Quelles règles doivent être respectées ?

1. Source unique : `arbres_34.canon.json` — rien d'autre
2. Extraction tree_id : regex `_T(\d+)__` sur title uniquement
3. Famille : lookup `id → family` dans arbres_34.canon.json
4. Zéro heuristique, zéro LLM-guess, zéro invention
5. Tags existants : APPEND ONLY — jamais supprimer
6. Docs sans `_Tnn__` : `PENDING_ADDITIONAL_SIGNAL` — pas d'écriture
7. Toute écriture : KX108 gate + WRITABLE_MEMORY_PROTOCOL obligatoires
8. `boundary_all_false = true` jusqu'à ouverture du gate

---

## Q9 — Quels blockers sont actifs ?

| Blocker | Severity | Résolution |
|---|---|---|
| WRITABLE_MEMORY_PROTOCOL non activé | HARD_BLOCK | Opérateur active après dry-run review |
| KX108 gate fermé | HARD_BLOCK | GATE_01 + GATE_02 + GATE_03 séquentiels |
| Table token_IR → tree_id absente | HARD_BLOCK (PATH_B) | Opérateur fournit si pertinent |
| Table concept_reverse_os → tree_id absente | HARD_BLOCK (PATH_C) | Opérateur fournit si pertinent |
| reverse_os.registry.json vide | HARD_BLOCK (PATH_C/D) | Opérateur peuple si pertinent |
| 2691 docs sans _Tnn__ | SOFT_BLOCK | Signal supplémentaire requis |

---

## Q10 — Quel est le spec de la CANONICAL_MEMORY_TAGGING_UNIT ?

Voir `CANONICAL_MEMORY_TAGGING_UNIT_SPEC.json` — champs clés :

- `memory_id` — BrodyMemoryDoc internal ID
- `source_title` — titre du doc
- `canonical_tree_id` — T{nn} ou null
- `canonical_tree_name` — nom de l'arbre ou null
- `canonical_family_id` — famille ou null
- `confidence_source_based` — 0.99 (TITLE_REGEX_MATCH) ou 0.0 (PENDING)
- `tagging_basis` — TITLE_REGEX_MATCH / PENDING_ADDITIONAL_SIGNAL / OPERATOR_EXPLICIT
- `boundary_status` — TAGGABLE_WITH_GATE / NOT_TAGGABLE_PENDING_SIGNAL / BLOCKED
- `new_tags_proposed` — [T04, I_FONDAMENTAUX] (append only)
- `existing_tags_preserved` — liste complète des tags existants

---

## Q11 — Quelle est la prochaine action ?

**BRODY_CANONICAL_TAGGING_DRY_RUN_READONLY**

Exécuter PATH_A en dry-run complet :
- Parcourir les 48 docs `_Tnn__`
- Produire `TAGGING_DRY_RUN_PLAN.jsonl` (48 CANONICAL_MEMORY_TAGGING_UNIT)
- Soumettre pour review opérateur / KX108 gate
- Zéro écriture Neo4j

---

## Q12 — Invariants finaux vérifiés

| Invariant | Valeur |
|---|---|
| neo4j_write_executed | false |
| graphiti_write_executed | false |
| memory_intake | false |
| runtime_binding_allowed | false |
| no_heuristic_tagging | true |
| no_llm_guessing | true |
| no_invention | true |
| boundary_all_false | true |
| group_a_staged_preserved | true |
| staged_files_still | 136 |

---

## Navigation

```
← BRODY_WORLD_TREE_GET_ONLY_TEST_READONLY_20260514_011350
→ BRODY_CANONICAL_TAGGING_DRY_RUN_READONLY (prochaine étape)
```
