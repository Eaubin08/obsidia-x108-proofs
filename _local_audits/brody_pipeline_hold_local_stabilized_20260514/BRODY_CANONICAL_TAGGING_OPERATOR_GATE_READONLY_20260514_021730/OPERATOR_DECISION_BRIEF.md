# OPERATOR DECISION BRIEF
## Mission: BRODY_CANONICAL_TAGGING_OPERATOR_GATE_READONLY
## Timestamp: 20260514_021730
## Destinataire: Opérateur / KX108
## Decision authority: KX108_ONLY

---

> **Aucune écriture n'est exécutée dans cette mission.**

---

## Ce qui va être écrit si vous autorisez

**96 tags** ajoutés sur **48 BrodyMemoryDoc** dans Neo4j (bolt://127.0.0.1:7688).

Chaque document reçoit **2 tags** :
1. Son identifiant canonique d'arbre : `T01` .. `T12`
2. Son identifiant canonique de famille : `I_FONDAMENTAUX`, `II_COGNITIFS`, ou `III_CONNAISSANCE`

### Distribution exacte

| Famille | Trees | Docs |
|---|---|---|
| I_FONDAMENTAUX | T01, T02, T03, T04, T05 | 20 docs (4 par arbre) |
| II_COGNITIFS | T06, T07, T08, T09, T10 | 20 docs (4 par arbre) |
| III_CONNAISSANCE | T11, T12 | 8 docs (4 par arbre) |

### Stratégie : APPEND_ONLY

Les tags sont **ajoutés** aux tags existants. Aucun tag existant n'est supprimé.

```cypher
-- Exemple pour un node T04 / I_FONDAMENTAUX :
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000000'})
WHERE n.title =~ '.*_T04__.*'
WITH n,
  CASE WHEN 'T04' IN n.tags THEN n.tags ELSE n.tags + ['T04'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;
```

---

## Ce qui ne sera pas touché

| Élément | Statut |
|---|---|
| Tags existants sur les 48 docs | Préservés intégralement (append-only) |
| `title`, `source`, `text_preview` des nodes | Non modifiés |
| 9 nodes exclus (META_DOCUMENT + TEXT_PREVIEW_REFERENCE) | Non touchés |
| T13-T34 (22 arbres) | Non touchés — PENDING_ADDITIONAL_SIGNAL |
| Familles IV-VIII | Non touchées — PENDING_ADDITIONAL_SIGNAL |
| 2691 docs `34_arbres` sans `_Tnn__` dans le titre | Non touchés |
| BrodyImportedMemory (batch 003636) | Non touchés — batch différent |
| Graphiti V20 frozen | Non touché |
| Neo4j : aucun CREATE, DELETE, MERGE, DETACH DELETE | Non exécutés |
| Git staging / commits / push | Non exécutés |

---

## Pourquoi c'est safe

1. **Source canonique unique** : arbres_34.canon.json + arbres_34.registry.json — zéro invention, zéro heuristique
2. **Match structurel direct** : regex `_T(\d+)__` sur le champ `title` uniquement — pas d'inférence sémantique
3. **48 nodes individuellement identifiés** par `node_id` — pas de MATCH wildcard
4. **Validation 13 règles × 48 entrées** : PASS 100% (BRODY_CANONICAL_TAGGING_REVIEW_GATE_READONLY)
5. **Rollback ciblé disponible** : 48 requêtes qui retirent uniquement les tags ajoutés par ce batch
6. **10 checks post-write obligatoires** : count, distribution, intégrité des exclus, T13-T34 inchangés
7. **Chaque requête vérifie le title pattern** avant SET — double protection contre erreur de ciblage

---

## Ce qui reste bloqué après cette écriture

| Élément | Raison du blocage |
|---|---|
| T13-T34 (22 arbres) | 0 doc avec `_Tnn__` dans le titre pour ces arbres |
| Familles IV-VIII | Aucun doc explicitement associé |
| 2691 docs 34_arbres restants | Signal supplémentaire requis (opérateur fournit mapping) |
| BrodyImportedMemory tree tagging | Batch séparé, gate séparé |
| Graphiti / Memory intake | Protocoles séparés non ouverts |

---

## Rollback disponible

Si un check post-write échoue, le rollback retire **uniquement les tags ajoutés par ce batch** :

```cypher
-- Exemple rollback pour GRAPHITI_V2_000000 :
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000000'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ['T04', 'I_FONDAMENTAUX']]
RETURN n.id, n.tags AS tags_after_rollback;
```

48 requêtes rollback prêtes dans `ROLLBACK_CANONICAL_TAGGING_PLAN.cypher`. Tags préexistants jamais affectés.

---

## Validation post-write prévue (10 checks obligatoires)

| Check | Condition attendue |
|---|---|
| PWV_01 | 48 nodes ont un Tnn tag |
| PWV_02 | Tous les approuvés ont leur Tnn |
| PWV_03 | Tous les approuvés ont leur family_id |
| PWV_04 | Tags existants préservés |
| PWV_05 | 9 exclus non touchés |
| PWV_06 | T13-T34 toujours à 0 |
| PWV_07 | Pas de tag dupliqué |
| PWV_08 | title/source/text_preview inchangés |
| PWV_09 | Count BrodyMemoryDoc = 3267 |
| PWV_10 | Distribution T01-T12: 4 docs chacun |

**Tout échec → rollback immédiat.**

---

## Pour autoriser l'écriture

Déclarez explicitement :

> **"J'autorise l'écriture canonique des 96 tags sur les 48 nodes validés."**

Cette déclaration déclenche la mission `BRODY_CANONICAL_TAGGING_CONTROLLED_WRITE_V1`.

Sans cette déclaration, **aucune écriture ne sera jamais exécutée**.

---

## État actuel

```
OPERATOR_APPROVAL=false
KX108_GATE_PASS=false
REAL_WRITE_ALLOWED=false
FINAL_VERDICT=NO_GO_PENDING_OPERATOR_AND_KX108_GATE
```
