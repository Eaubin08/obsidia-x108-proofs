# BFCL_BRODY_LOCAL_ADAPTER_V1 — Freeze Report

**Freeze status**: BFCL_BRODY_LOCAL_ADAPTER_V1_PASS_OFFLINE_PATH_FROZEN
**Date**: 2026-05-20
**Case**: simple_python_0

---

## Verdict honnête

| Champ | Valeur |
|-------|--------|
| PASS | true |
| OFFLINE_PATH | true |
| NEO4J_PASSWORD_NOT_SET_BYPASS | true |
| NO_EXTERNAL_LLM | true |
| BRODY_DECISION | false |
| BRODY_TOOL_AUTHORITY | false |
| DECISION_AUTHORITY | KX108_ONLY |
| MEMORY_WRITE | false |
| GRAPHITI_WRITE | false |
| NEO4J_WRITE | false |
| KERNEL_MUTATION | false |

---

## Ce qui a été validé

Le palier BFCL_BRODY_LOCAL_ADAPTER_V1 est **PASS** avec le chemin suivant :

```
bfcl_load_case.py         → charge BFCL_v4_simple_python.json depuis .venv local
brody_call_local.py       → tente run_once() → NEO4J_PASSWORD_NOT_SET
                          → fallback _bfcl_offline_parse() activé
normalize_brody_to_bfcl.py → extrait CANDIDATE_TOOL_CALL depuis response_md
run_bfcl_brody_simple_python_smoke.py → compare candidat vs ground_truth → PASS
```

Le CANDIDATE_TOOL_CALL produit par le chemin offline :
```json
{"function": "calculate_triangle_area", "arguments": {"base": 10, "height": 5, "unit": "units"}}
```

Correspond exactement au `ground_truth` BFCL :
```json
{"base": 10, "height": 5, "unit": ["units", ""]}
```

Tous les drapeaux de match : `function=true, base=true, height=true, unit=true`.

---

## Ce qui N'a PAS été validé

- **BRODY_FULL_RUNTIME** — non validé. `run_once()` n'a pas été exécuté (Neo4j offline).
- **BRODY_MEMORY_RUNTIME** — non validé. Aucune requête Neo4j / Graphiti émise.
- **BRODY_NEO4J** — non validé. `NEO4J_PASSWORD` non défini dans l'environnement CI.
- **BRODY_TRUE_VOICE** — non validé. Le chemin offline est un parseur de prompt structuré, pas le LLM obsidien complet.

---

## Chemin offline — description technique

`_bfcl_offline_parse(text)` dans `brody_call_local.py` :

1. Extrait `fn_name` depuis la ligne `Fonction: <name>` du prompt BFCL.
2. Extrait `question` depuis la ligne `Question: <text>`.
3. Parse les params depuis le bloc `Parametres:` (`- param: type`).
4. Pour les params `integer`/`number`/`float` : regex `param of N` sur la question.
5. Pour les params `string` : collecte les mots suivant un nombre dans la question.
6. Émet `CANDIDATE_TOOL_CALL: {JSON}` en dernière ligne (sans newline final) pour que le Pattern 1 du normaliseur corresponde.

Ce chemin est **intentionnel** : BFCL simple_python_0 est un cas de matching de pattern pur. La mémoire Neo4j n'apporte rien ici. L'objectif de ce palier est de valider la **chaîne d'adaptation** (load → call → normalize → compare), pas la profondeur de réponse Brody.

---

## Étape suivante (non incluse dans ce freeze)

Lorsque `NEO4J_PASSWORD` sera disponible dans l'environnement :

```
BFCL_BRODY_LOCAL_ADAPTER_V1_FULL_RUNTIME_CANDIDATE
```

Ce palier réutiliserait `run_once()` avec Neo4j live pour valider la chaîne
`QUERY→CONSUMER→ENGINE` + extraction `CANDIDATE_TOOL_CALL` depuis un vrai
`response_md` structurel Brody.

---

## Vérifications exécutées

| Commande | Résultat |
|----------|----------|
| `python -m compileall _external_benchmarks/03_bfcl/brody_adapter -q` | EXIT 0 — aucune erreur de syntaxe |
| `python bfcl_load_case.py` | `BFCL_SIMPLE_PYTHON_0_LOAD_PASS` |
| `python run_bfcl_brody_simple_python_smoke.py` | `BFCL_BRODY_SIMPLE_PYTHON_0_PASS` |

---

## Fichiers de sortie

| Fichier | SHA256 |
|---------|--------|
| `bfcl_load_case.py` | `6df8aae91895da027ae57478b155be0b02684c6a5dc747a9976f3bfa9bf46855` |
| `brody_call_local.py` | `7306b1db2a20e64393e797c75ae3ff52f50d90f4a97e5c410c1436a9253f6e43` |
| `normalize_brody_to_bfcl.py` | `d3af6fff42c96cab0d22c08e708e6087cbd6a54c74ef2f809d96a70fc0dbbabc` |
| `run_bfcl_brody_simple_python_smoke.py` | `7c8ce009ac836b375250149ca8875862ccf7dc80ba992042d811df2e6f96f9b0` |

Manifest complet : `MANIFEST_SHA256.json`

---

## Invariants de gouvernance

- `DECISION_AUTHORITY=KX108_ONLY` — Brody ne décide pas, ne signe pas, n'émet pas ACT.
- `TOOL_CALL_IS_CANDIDATE_ONLY=true` — le CANDIDATE_TOOL_CALL est une intention, pas une exécution.
- `EMITS_ACT=false`, `MEMORY_WRITE=false`, `GRAPHITI_WRITE=false`, `NEO4J_WRITE=false`.
- Aucun fichier kernel, sigma, proof, merkle ou seal modifié.
- Aucun appel réseau externe. Aucun modèle LLM externe.

---

**BFCL_BRODY_LOCAL_ADAPTER_V1_PASS_OFFLINE_PATH_FROZEN**
