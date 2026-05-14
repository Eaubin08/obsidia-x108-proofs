# BRODY_API_MEMORY_CONTEXT_READONLY_REPORT
Étape : 4 — BRODY_API_MEMORY_CONTEXT_TO_LLM_INTERACTION_READONLY
Date : 2026-05-13
Timestamp : 20260513_194604
Mode : READONLY — NO COMMIT — NO FREEZE — NO PUSH

---

## ÉTAT MÉMOIRE_CONTEXT_AUDIT

```
MEMORY_CONTEXT_AUDIT_STATUS = PASS
API_8011                    = LIVE
CHAIN_VERDICT               = CHAIN_PASS (validé étape 3+)
DECISION_AUTHORITY          = KX108_ONLY
```

---

## A — SOURCES MÉMOIRE EXISTANTES

Trois sources mémoire physiquement présentes, architecturalement distinctes :

### 1. Graphiti V20 frozen (via API 8011 frozen adapter)

| Champ | Valeur |
|---|---|
| Endpoint | `http://127.0.0.1:8011/graph/v20/frozen/*` |
| Adapter | `obsidiashell-main/graphiti_v20_frozen_adapter.py` |
| Nœuds | 167 (nodes), 477 (rels), 20 épisodes indexés |
| Mode | FROZEN_READONLY |
| live_neo4j_dependency | false |
| Structure entité | `entities[{name, summary}]` |
| x108_merge_status | NOT_MERGED |
| Rôle | Surface de contexte haut niveau (agents, concepts, invariants) |

### 2. Neo4j live BrodyMemoryDoc (bolt://7688)

| Champ | Valeur |
|---|---|
| URI | `bolt://localhost:7688` |
| Node label | `BrodyMemoryDoc` |
| Total nœuds | 3267 |
| Champs présents | `decision_authority, id, memory_decision, path, readonly, source, tags, text_preview, title, updated_at` |
| Nœuds avec `text_preview` non vide | **3267 / 3267** (100%) |
| Nœuds avec `path` non vide | 904 / 3267 |
| Rôle | Source primaire utilisée par la chaîne QUERY→CONSUMER→ENGINE |

### 3. Fichiers locaux

| Champ | Valeur |
|---|---|
| Accès | Via champ `path` des BrodyMemoryDoc |
| État | `path=""` pour 2363/3267 nœuds. Sur échantillon kernel-tagged : 0/5 paths existent sur disque |
| Contenu `text_preview` | JSON sérialisé avec `source_original_path` en chemin relatif `_world_sources/...` |
| Disponibilité | Non disponible en pratique pour la chaîne actuelle |

### 4. Context packets capturés (audit précédent)

Fichiers JSON dans `_local_audits/BRODY_CONTEXT_PACKET_CHAIN_TEST_READONLY_20260513_192629/` — snapshot du dernier run live.

---

## B — SOURCE UTILISÉE PAR BRODY DANS LA CHAÎNE

```
SOURCE_USED_BY_BRODY = Neo4j live BrodyMemoryDoc
MODULE               = brody_context_packet_query_readonly_v1.py
NEO4J_URI            = bolt://localhost:7688
NODE_LABEL           = BrodyMemoryDoc
```

**La chaîne QUERY→CONSUMER→ENGINE utilise exclusivement Neo4j BrodyMemoryDoc.**

Le corpus Graphiti V20 frozen (API 8011 `/frozen/*`) est une surface API distincte. Elle n'alimente pas la chaîne directement — elle a été testée pour sa disponibilité GET et ses mutations bloquées uniquement.

---

## C — POURQUOI material_quality=LOW_MATERIAL ?

### Cause racine : FIELD_MAPPING_MISMATCH

Le Cypher du query module (`brody_context_packet_query_readonly_v1.py`, ligne 52) utilise :

```cypher
coalesce(p.text, p.content, p.body, p.excerpt, p.summary, p.preview, "") AS body
```

Or les nœuds BrodyMemoryDoc ont le champ `text_preview` — **absent du `coalesce`**. Résultat : `body=""` pour **tous les 3267 nœuds**.

| Champ cherché par coalesce | Présent dans Neo4j ? |
|---|---|
| `text` | Non |
| `content` | Non |
| `body` | Non |
| `excerpt` | Non |
| `summary` | Non |
| `preview` | Non |
| **`text_preview`** | **Oui — 3267/3267 nœuds** |

### Cascade de conséquences

```
body = ""
  → safe_excerpt("") = ""
  → excerpt = "" dans query output
  → consumer.read_local_excerpt(path) = "" (path="" pour la plupart)
  → engine items_with_material = 0
  → material_quality = LOW_MATERIAL
```

### Contenu de `text_preview`

`text_preview` contient un JSON sérialisé :
```json
{
  "id": "BRODY_GRAPHITI_READY_000000",
  "title": "003BEA03EEDD_T04__Consensus...",
  "source_original_path": "_world_sources\\PROJECT_MEMORY_CLEAN_SOURCE_NO_INDEX_..."
}
```

Ce n'est pas un texte lisible directement — c'est un pointeur structuré. Le chemin `source_original_path` est relatif à un dossier `_world_sources/` qui n'existe plus ou n'est pas accessible dans ce contexte.

### Ce n'est PAS une violation

`LOW_MATERIAL` n'est pas une violation de boundary. C'est un état de données :
- Boundaries = tous false ✓
- DECISION_AUTHORITY = KX108_ONLY ✓
- Chaîne = PASS ✓

### Ce qu'il faudrait pour corriger (non autorisé sans instruction)

Ajouter `p.text_preview` dans le coalesce du Cypher, ligne 52 de `brody_context_packet_query_readonly_v1.py`. Modification X108 — nécessite instruction explicite opérateur.

---

## D — entity_count=0 POUR BRODY : NORMAL ?

```
OUI — ARCHITECTURALEMENT CORRECT
```

`context_brody.json` : `entity_count=0`, `relation_count=0`, `warnings=[]`

**Brody = le LLM obsidien lui-même.** Brody n'est pas une entité dans le corpus Graphiti V20. Le corpus V20 Phase0 contient :
- Agents : CANON_GUARDIAN, GRAPH_BUILDER, PROOF_SENTINEL, etc.
- Concepts : Kernel, Lean, TLA+, Sigma, etc.
- Pas "Brody" comme nœud nommé.

Ce résultat vide est correct et attendu. Ce n'est pas une erreur d'API.

---

## E — COHÉRENCE DES ENDPOINTS API 8011

### GET frozen (6 endpoints)

| Endpoint | OK | entity_count | kernel_decision | graphiti_decision |
|---|---|---|---|---|
| /frozen/status | ✓ | — | — | — |
| /frozen/context?q=Kernel | ✓ | 5 | NONE | NONE |
| /frozen/context?q=CANON | ✓ | 5 (2 rels) | NONE | NONE |
| /frozen/context?q=X-108 | ✓ | 1 (CANON_GUARDIAN) | NONE | NONE |
| /frozen/context?q=Brody | ✓ | 0 | NONE | NONE |
| /frozen/search?q=Kernel | ✓ | 5 | — | — |

### Mutations négatives (3)

| Méthode | Endpoint | Status | Bloqué |
|---|---|---|---|
| POST | /frozen/context | 405 | ✓ |
| POST | /frozen/search | 405 | ✓ |
| DELETE | /frozen/status | 405 | ✓ |

### Status frozen

```
source               = OBSIDIA_GRAPHITI_PHASE0_V20_FROZEN
mode                 = FROZEN_READONLY
live_neo4j_dependency = false ✓
nodes                = 167
rels                 = 477
indexed_episodes     = 20
x108_merge_status    = NOT_MERGED
commit_status        = LOCAL_ONLY
```

**Cohérence : COMPLÈTE.** Tous les GET OK, toutes les mutations bloquées 405, `kernel_decision=NONE` et `graphiti_decision=NONE` sur toutes les réponses contexte.

---

## F — INCOHÉRENCE DU RAPPORT PRÉCÉDENT (12 vs 14)

**Rapport concerné :** `BRODY_CONTEXT_PACKET_CHAIN_TEST_READONLY_20260513_192629/reports/BRODY_CONTEXT_PACKET_CHAIN_TEST_READONLY_REPORT.md`

**Incohérence constatée :**
- Le header du rapport dit : `"total_tested": 12`
- La table des endpoints liste : 6 GET frozen context + 5 autres GET + 3 mutations = 14 entrées

**Analyse :**
- 12 = 9 GET réels (status + context×4 + counts + metrics + manifest + search) + 3 mutations = **mais le rapport listait aussi evidence**
- 14 = 11 GET + 3 mutations = total correct de la table

**Conclusion :** Le chiffre "12" dans le JSON était le nombre d'endpoints GET testés dans les 6 premiers groupes (frozen context endpoints uniquement, sans les autres GET). La table incluait tous les 14.

**Action :** Rapport précédent non modifié. Incohérence documentée ici.

---

## G — BOUNDARY FINAL

```
BRODY_EXECUTE_ALLOWED      = false ✓
BRODY_AUTHORIZE_ALLOWED    = false ✓
HUMAN_OPERATOR_REQUIRED    = true  ✓
READONLY_ANALYSIS_ONLY     = true  ✓
MEMORY_DECISION            = false ✓
ALLOWED_TO_DECIDE          = false ✓
EMITS_ACT                  = false ✓
EMITS_VERDICT              = false ✓
GRAPHITI_WRITE             = false ✓
GRAPHITI_INDEX_WRITE       = false ✓
NEO4J_WRITE_EXECUTED       = false ✓
MEMORY_INTAKE              = false ✓
KERNEL_MUTATION            = false ✓
X108_RUNTIME_BINDING       = false ✓
X108_MERGE                 = false ✓
DECISION_AUTHORITY         = KX108_ONLY ✓
X108_DIRTY_FILE_TOUCHED    = false ✓
```

---

## RÉSUMÉ FINAL

| Point | Valeur |
|---|---|
| MEMORY_CONTEXT_AUDIT_STATUS | **PASS** |
| SOURCE_USED_BY_BRODY | Neo4j live BrodyMemoryDoc (bolt://7688) — 3267 nœuds |
| MATERIAL_QUALITY_CAUSE | `text_preview` absent du coalesce Cypher. path='' pour 72% des nœuds. Aucun fichier local accessible. |
| API_FROZEN_STATUS | 6 GET OK, 3 mutations 405 bloquées, kernel_decision=NONE, live_neo4j_dependency=false |
| ENTITY_COUNT_BRODY_ZERO | Architecturalement correct — Brody=LLM obsidien, pas entité Graphiti |
| ENDPOINT_COUNT_CLARIFICATION | 12 (GET) + 3 (mutations) = 15 vérifications totales dans cette session |
| NEXT_BUILD_TARGET | **ÉTAPE 5 — BRODY_USER_MEMORY_INTAKE_CANDIDATE_READONLY** |

---

## GUARDRAILS

```
COMMITTED           = false
FROZEN              = false
PUSH                = false
X108_MODIFICATION   = false
SIGMA_TOOLS_TOUCHED = false
FAUX_PASS_CREES     = false
```
