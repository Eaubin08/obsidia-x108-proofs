# P33D — OS_TRAD Evidence Reconciliation Report

**Branche :** p10-real-engine-controlled-bridge  
**Date :** 2026-06-03  
**Commit de référence P33 :** fe38ee1 — feat(p33): add os trad deep concept layer index and semantic enrichment  
**Verdict :** P33D_OS_TRAD_EVIDENCE_RECONCILED

---

## Contexte

P33 a introduit `runtime_wiring/source_runtime/os_trad_reverse_index.py`, un index conceptuel
classifiant les entrées du registre OS_TRAD_REVERSE_OS en couches sémantiques. Cet index était
basé principalement sur une analyse de chemins (path-only / P33 zip scan).

P33B et P33C ont ensuite réalisé des audits plus stricts :

| Audit | Méthode | Portée | Autorité |
|---|---|---|---|
| P33B | Deep evidence (contenu + chemin) | 546 fichiers sûrs | Secondaire |
| P33C | Content-only (termes dans le corps du fichier) | 546 fichiers sûrs | **Primaire** |

P33D corrige le runtime pour refléter fidèlement les preuves P33C et ajoute les champs
d'évidence manquants à chaque couche.

---

## Tableau comparatif P33B vs P33C

| Concept runtime | P33 (initial) | P33B (deep) | P33C (content-only) | P33D (corrigé) |
|---|---|---|---|---|
| UNIVERSAL_LANGUAGE_LAYER | found=True, 7 fichiers, HIGH | FOUND_STRONG, 546/5 | FOUND_STRONG, 5 fichiers | PARTIAL_STRONG, 5 fichiers |
| REVERSE_LANGUAGE_LAYER | found=True, 1 fichier, LOW | FOUND_STRONG (path+content) | FOUND_MEDIUM, 1 fichier | MEDIUM_SIGNAL, 1 fichier |
| IR_LAYER | found=True, 1 fichier, LOW | FOUND_MEDIUM | FOUND_MEDIUM, 1 fichier | MEDIUM_SIGNAL, 1 fichier |
| REVERSE_WINDOWS_LAYER | **found=True**, 1 fichier, LOW | FOUND_MEDIUM (1 occ.) | **NOT_FOUND** | **NOT_FOUND, found=False** |
| LAWS_PROTOCOLS_LAYER | found=True, 202 fichiers, HIGH | FOUND_STRONG | LOIS=22 + PROTO=97 | CORE_STRONG, 119 |
| AGENTS_TREES_LAYER | found=True, 397 fichiers, HIGH | FOUND_STRONG | FOUND_STRONG | CORE_STRONG, 397 |
| LCTU (path_pattern) | présent dans path_patterns | — | **NOT_FOUND** | **retiré** |
| ALPHABET | signal dans UNIVERSAL | signal | FOUND_MEDIUM, 1 | signal, pas système |

---

## Concepts solides — CORE_STRONG

### LAWS_PROTOCOLS_LAYER

- **P33C :** LOIS = 22 fichiers, 34 matches ; PROTOCOLES = 97 fichiers, 170 matches
- **Fichiers clés :** Constitution O1–O8, agent_boundary.md, non_decision_formulas.md
- **Dirs dédiés :** `02_CONSTITUTION_LOIS_OBSIDIENNES`, `11_AGENTS_RUNTIME_CONTRACTS`, `15_GUARDS_NON_DECISION`
- **Verdict :** CORE_STRONG — couche la plus dense en termes contenu hors arbres/agents

### AGENTS_TREES_LAYER

- **P33C :** 397 fichiers, 34 répertoires d'arbres, registry 52 agents confirmé
- **Fichiers clés :** `agents_52.registry.json`, `shazam_spec.md`, `BDF.schema.json`
- **Verdict :** CORE_STRONG — couche dominante du pack

---

## Concept partiel — PARTIAL_STRONG

### UNIVERSAL_LANGUAGE_LAYER

- **P33C :** 5 fichiers avec termes `grammaire`, `syntaxe`, `lexique`, `vocabulaire`
- **Limite :** langage universel complet non établi. LCTU absent (NOT_FOUND P33C).
- **ALPHABET :** 1 fichier contenu — signal, pas système alphabet complet
- **Verdict :** PARTIAL_STRONG (pas CORE_STRONG, pas système de langage universel)

---

## Concepts à signal faible — MEDIUM_SIGNAL

### REVERSE_LANGUAGE_LAYER

- **P33C :** 1 fichier (`extracted_text_all.md`) avec termes `réciproque`, `miroir`, `inversion`
- **P33B :** strong path presence (répertoires 06/16) mais 1 seul fichier contenu fort
- **Verdict :** MEDIUM_SIGNAL — présence structurelle, pas de spec langage reverse dédiée

### IR_LAYER

- **P33C :** 1 fichier, terme `alphabet ir` / ` ir `
- **P33B :** répertoire `09_MCP_BRIDGE_OBSIDIA_IR` présent, mais spec IR non confirmée en contenu
- **Verdict :** MEDIUM_SIGNAL — concept référencé, pas de spec dédiée confirmée

### RECIPROQUE / OPERATEURS / ALPHABET

- 1 fichier chacun (P33C), 1–6 matches
- Signaux présents dans `extracted_text_all.md` uniquement
- Aucun fichier spec dédié
- Restent des signaux conceptuels, pas des systèmes complets

---

## Concepts absents — NOT_FOUND

### LCTU

- **P33C :** 0 fichiers, 0 matches
- **P33B :** 0 fichiers contenu
- **Action P33D :** retiré de `_LAYER_DEFINITIONS["UNIVERSAL_LANGUAGE_LAYER"]["path_patterns"]`
- **Note :** la description de UNIVERSAL_LANGUAGE_LAYER mentionne l'absence explicitement

### REVERSE_WINDOWS_LAYER

- **P33C :** 0 fichiers, 0 matches sur termes windowing/fenêtre/sliding
- **P33B :** 1 occurrence du mot `window` dans `extracted_text_all.md` — insuffisant
- **Action P33D :** `found=True → False`, `confidence=LOW → NONE`, `evidence_status="NOT_FOUND"`
- **Note :** les répertoires `16_VISUALISATION_REVERSE_OS` et `13_GRAPHES_NUAGE_POINTS` existent
  dans l'arborescence, mais aucun contenu de fichier ne confirme un concept windowing

---

## Corrections runtime apportées

### `runtime_wiring/source_runtime/os_trad_reverse_index.py`

**`_LAYER_DEFINITIONS` :**

| Champ | Avant | Après |
|---|---|---|
| UNIVERSAL_LANGUAGE_LAYER.description | "…, LCTU" | "…(LCTU absent P33C)" |
| UNIVERSAL_LANGUAGE_LAYER.path_patterns | contient "lctu" | "lctu" retiré |

**`_SCAN_RESULTS` — nouveaux champs ajoutés à toutes les couches :**

- `evidence_status` — niveau P33C : CORE_STRONG / PARTIAL_STRONG / MEDIUM_SIGNAL / NOT_FOUND
- `evidence_basis` — "P33C_CONTENT_ONLY" (autorité)
- `confidence_reason` — phrase explicative
- `source_files_count` — compte P33C content-only
- `strong_files_count` — fichiers fortement confirmés

**Corrections de valeurs :**

| Couche | Champ | Avant | Après |
|---|---|---|---|
| REVERSE_WINDOWS_LAYER | found | True | **False** |
| REVERSE_WINDOWS_LAYER | confidence | "LOW" | **"NONE"** |
| REVERSE_WINDOWS_LAYER | matching_files_count | 1 | **0** |
| Toutes | evidence_status | _(absent)_ | ajouté |
| Toutes | source_files_count | _(absent)_ | ajouté |
| Toutes | strong_files_count | _(absent)_ | ajouté |

**`build_os_trad_deep_concept_index()` chemin dynamique :**

Les 5 nouveaux champs P33D sont propagés depuis `_SCAN_RESULTS` (statique, autorité P33C) même
lors d'un appel dynamique avec entrées de registre.

---

## Limites restantes

1. **REVERSE_LANGUAGE_LAYER** : présence structurelle forte (dirs 06/16) mais contenu limité à
   1 fichier. Le statut MEDIUM_SIGNAL pourrait évoluer si des specs dédiées sont ajoutées au pack.

2. **IR_LAYER** : répertoire `09_MCP_BRIDGE_OBSIDIA_IR` présent mais non peuplé de specs IR
   dans le contenu audité. Statut MEDIUM_SIGNAL à réévaluer si des specs IR sont ajoutées.

3. **ALPHABET** : signal présent dans 1 fichier. N'est pas un système alphabet complet —
   restera un signal partiel de UNIVERSAL_LANGUAGE_LAYER.

4. **OPERATEURS / RECIPROQUE** : 1 fichier chacun. Signaux faibles non promus en couches
   dédiées — ils restent couverts par LAWS_PROTOCOLS ou UNIVERSAL_LANGUAGE selon le contexte.

5. **Source principale** : `01_SOURCES/extracted_text_all.md` (443 KB) est la source de la
   majorité des signaux faibles. Une analyse par section de ce fichier permettrait d'affiner
   les niveaux de signal.

---

## Fichiers modifiés

```
runtime_wiring/source_runtime/os_trad_reverse_index.py   — corrections P33D
tests/test_os_trad_reverse_deep_binding_p33.py           — +8 tests P33D evidence
docs/real_engine/P33D_OS_TRAD_EVIDENCE_RECONCILIATION_REPORT.md  — ce rapport
```

## Commit

```
fix(p33): reconcile os trad deep index with content-only evidence
```
