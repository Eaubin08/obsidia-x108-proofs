# LOW_MATERIAL_PATCH_CANDIDATE_READONLY
**Timestamp :** 20260513_231002  
**Mode :** READONLY — NO_COMMIT — NO_FREEZE — NO_PUSH  
**Autorité :** KX108_ONLY

---

## Cause racine — LOW_MATERIAL

### Fichier cible

```
obsidia-x108-proofs/periphery/brody_memory_readonly/context_packet_query_readonly/brody_context_packet_query_readonly_v1.py
```

(Repo git distinct : `obsidia-x108-proofs/.git` — non tracké par `obsidia-engine-proof-core`)

### Diagnostic schéma Neo4j

Champs présents sur les nœuds `BrodyMemoryDoc` :

| Champ | Dans schema | text_preview non vide |
|---|---|---|
| `text` | **ABSENT** | — |
| `content` | **ABSENT** | — |
| `body` | **ABSENT** | — |
| `excerpt` | **ABSENT** | — |
| `summary` | **ABSENT** | — |
| `preview` | **ABSENT** | — |
| `text_preview` | **PRÉSENT** | **3 267 nœuds** |

Source : `brody_memory_doc_inspection.json` — `with_text_preview_non_empty: 3267`

### Conséquence

Le coalesce AVANT épuisait 6 champs tous absents → fallback toujours `""` → `body=""` pour les 3 267 nœuds → score body = 0 → LOW_MATERIAL sur toutes les requêtes.

---

## Patch minimal — 1 ligne

**AVANT (ligne 52) :**
```cypher
coalesce(p.text, p.content, p.body, p.excerpt, p.summary, p.preview, "") AS body
```

**APRÈS :**
```cypher
coalesce(p.text, p.content, p.body, p.excerpt, p.summary, p.preview, p.text_preview, "") AS body
```

Patch appliqué. Diff complet : `LOW_MATERIAL_PATCH.diff`

---

## Smoke AVANT / APRÈS — Analyse statique

| Métrique | AVANT | APRÈS |
|---|---|---|
| LOW_MATERIAL | true | false |
| items_with_material | 0 | UP_TO_3267 |
| body scoring actif | false | true |
| nodes exploitables | 0 | 3 267 |

**Méthode :** analyse statique du schéma Neo4j (aucune requête Neo4j live — READONLY_DRY_RUN)  
Détail : `LOW_MATERIAL_BEFORE_AFTER_SMOKE.json`

---

## Guardrails

| Check | Valeur |
|---|---|
| MEMORY_INTAKE | false |
| GRAPHITI_WRITE | false |
| NEO4J_WRITE | false |
| BRODY_EXECUTE_ALLOWED | false |
| BRODY_AUTHORIZE_ALLOWED | false |
| GROUP_A_STAGED_PRESERVED | true |
| STAGED_FILES_STILL | 136 |
| NO_GIT_ADD | true |
| NO_COMMIT | true |
| NO_FREEZE | true |
| NO_PUSH | true |

---

## Prochaines actions

```
NEXT_BRODY_MEMORY_ACTION=BRODY_SESSION_CLOSE_DECISION_APPLY_PRECURSOR_READONLY
NEXT_REAL_WORLD_ACTION=BRODY_WORLD_PROVIDER_MATRIX_READONLY
```

**VERDICT : LOW_MATERIAL_PATCH_CANDIDATE_READONLY_DONE**
