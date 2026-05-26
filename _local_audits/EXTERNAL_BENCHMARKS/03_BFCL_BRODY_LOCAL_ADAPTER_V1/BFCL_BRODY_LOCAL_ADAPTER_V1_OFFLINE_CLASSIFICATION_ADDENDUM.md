# BFCL_BRODY_LOCAL_ADAPTER_V1 — Classification Addendum

**Date**: 2026-05-20
**Statut freeze**: BFCL_BRODY_LOCAL_ADAPTER_V1_PASS_OFFLINE_PATH_FROZEN

---

## Classification honnête

```json
{
  "bfcl_brody_local_adapter_v1": {
    "status": "PASS_OFFLINE_PATH_FROZEN",
    "case": "simple_python_0",
    "validated_chain": "load -> prompt -> offline_parse -> normalize -> compare",
    "neo4j_runtime": false,
    "brody_run_once": false,
    "true_voice_runtime": false,
    "source_role": "EXTERNAL_BENCHMARK_OFFLINE_ADAPTER",
    "next": "BFCL_BRODY_LOCAL_ADAPTER_V1_FULL_RUNTIME_CANDIDATE when NEO4J_PASSWORD is available"
  }
}
```

---

## Autorité de la source

| Domaine | Autorité |
|---------|----------|
| BFCL offline adapter harness | HIGH |
| Brody runtime | LOW — non validé par ce freeze |
| True voice runtime | NONE — non concerné |

---

## Ce que ce freeze PROUVE

- Le harness BFCL local existe et est syntaxiquement correct (`compileall EXIT 0`).
- La donnée `BFCL_v4_simple_python.json` est chargée et le cas `simple_python_0` est résolu (`BFCL_SIMPLE_PYTHON_0_LOAD_PASS`).
- Le fallback `_bfcl_offline_parse()` extrait correctement l'appel outil candidat depuis un prompt BFCL structuré.
- La chaîne de normalisation et de comparaison passe (`function=true, base=true, height=true, unit=true`).

## Ce que ce freeze NE PROUVE PAS

- `BRODY_FULL_RUNTIME` — `run_once()` n'a pas été exécuté.
- `BRODY_MEMORY_RUNTIME` — aucune requête Neo4j / Graphiti émise.
- `BRODY_NEO4J` — `NEO4J_PASSWORD` non défini dans l'environnement.
- `BRODY_TRUE_VOICE` — le chemin offline est un parseur de prompt, pas le LLM obsidien.
- Mémoire Brody, Graphiti live, terminal structural dialogue, project memory, session memory.

---

## Règle d'utilisation

Ce freeze peut être cité comme **preuve périphérique** (EXTERNAL_BENCHMARK_OFFLINE_ADAPTER) dans un rapport de stabilisation. Il ne peut **jamais** être cité comme preuve que Brody runtime est branché, fonctionnel, ou validé.

---

## Chantier principal (non dérivé par ce freeze)

Le chantier Brody reste indépendant de BFCL :

**Fondations à stabiliser :**
1. **PROJECT MEMORY** — sources PRE_UI / V1.4.12C, local response engine, hydration
2. **SESSION MEMORY / FOLLOW-UP** — terminal_structural_dialogue V1.1B, session_memory_ledger V2
3. **TRUE RESPONSE STRUCTURE** — auto_triage memory intake V1, brancher `/api/brody/chat`

**BFCL est une voie externe de benchmark. Il ne remplace pas le runtime Brody.**

---

## Prochain palier BFCL (optionnel)

`BFCL_BRODY_LOCAL_ADAPTER_V1_FULL_RUNTIME_CANDIDATE`

**Condition préalable** : `NEO4J_PASSWORD` disponible dans l'environnement.

**Objectif** :
- Désactiver le fallback offline dans `brody_call_local.py`.
- Appeler réellement `terminal_structural_dialogue.run_once()`.
- Vérifier que Brody répond via mémoire réelle.
- Normaliser la sortie en function call candidate.
- Comparer au ground_truth BFCL et documenter PASS / PARTIAL / FAIL.

**Ne pas lancer tant que Neo4j n'est pas disponible.**

---

**BFCL_BRODY_LOCAL_ADAPTER_V1_PASS_OFFLINE_PATH_FROZEN**
