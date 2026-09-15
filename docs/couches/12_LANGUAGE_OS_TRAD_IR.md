# 12 · Langage : OS Trad et IR

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

La traduction de toute entrée (demande humaine, code, document, événement) en représentation unifiée (Unified Input IR) et le routage.

## Où elle intervient dans le trajet d'une demande

- **Étape 2 · Traduction et compréhension** : OS Trad et Unified Input IR la traduisent dans le langage d'Obsidia, avec son contexte, puis la routent.

Voir le trajet complet : [guide général](../README.md).

Cette couche joue un rôle clé dans **le trajet 1 (cognition)** : voir [TRAJETS.md](../TRAJETS.md), qui explique aussi pourquoi Obsidia fonctionne sans entraînement.

## Où est son code aujourd'hui

**Points d'entrée connus :**

- [periphery/language/](../../periphery/language) · langage

D'après le registre de fonctionnalités V3, **30 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `proofs/V18_3_1/` | 18 |
| `apps/obsidia-workbench/` | 5 |
| `apps/obsidia_api/` | 3 |
| `scripts/` | 2 |
| `periphery/language/` | 1 |
| `runtime_wiring/source_runtime/` | 1 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (15)

### Documents de référence — à lire en premier

- [Language Module](../language/README.md) · `docs/language/README.md`
  <br>Language detection and routing. Routes queries to appropriate response pipelines while preserving language boundaries. Never decides, never emits ACT. Language = context,…
- [Translation Layer — Obsidia X-108](../translation/README.md) · `docs/translation/README.md`
  <br>Natural Language
- [OS Reverse Projection — Workbench V1](../translation/OS_REVERSE_PROJECTION_WORKBENCH_V1.md) · `docs/translation/OS_REVERSE_PROJECTION_WORKBENCH_V1.md` *(référence probable)*
  <br>OS Reverse takes an IR Candidate and projects it back into natural language for the human user.
- [OS Trad → IR Pipeline — Workbench V1](../translation/OS_TRAD_TO_IR_WORKBENCH_V1.md) · `docs/translation/OS_TRAD_TO_IR_WORKBENCH_V1.md` *(référence probable)*
  <br>OS Trad takes natural language input and structures it into an Intermediate Representation (IR) for inspection.
- [Symbolic Alphabet Trace — Workbench V1](../translation/SYMBOLIC_ALPHABET_TRACE_V1.md) · `docs/translation/SYMBOLIC_ALPHABET_TRACE_V1.md` *(référence probable)*
  <br>The symbolic alphabet converts raw natural language tokens into inspectable semantic units.

<details><summary><b>Rapports, audits et preuves d'exécution</b> (10)</summary>

**`docs/`**

- [EDUCATION_BIAS_LANGUAGE_BACKLOG_REPORT.md](../EDUCATION_BIAS_LANGUAGE_BACKLOG_REPORT.md) — Education / Bias / Language / Ingestion — Implementation Report

**`docs/freeze/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_OS_TRAD_IR_REVERSE_DISCOVERY_REPORT.md](../freeze/BRODY_OS_TRAD_IR_REVERSE_DISCOVERY_REPORT.md) — BRODY_OS_TRAD_IR_REVERSE_DISCOVERY_REPORT

**`docs/real_engine/`** · *dossier lu par du code : ne pas déplacer*

- [P32_OS_TRAD_REVERSE_OS_RUNTIME_FAMILY_REPORT.md](../real_engine/P32_OS_TRAD_REVERSE_OS_RUNTIME_FAMILY_REPORT.md) — P32 — OS_TRAD_REVERSE_OS Runtime Family Report
- [P34_REVERSE_OS_INTERLANGUAGE_CANONIZATION_REPORT.md](../real_engine/P34_REVERSE_OS_INTERLANGUAGE_CANONIZATION_REPORT.md) — P34 — Reverse OS Interlanguage Canonization Report
- [P35_REVERSE_OS_INTERLANGUAGE_RUNTIME_EXTENSION_REPORT.md](../real_engine/P35_REVERSE_OS_INTERLANGUAGE_RUNTIME_EXTENSION_REPORT.md) — P35 — Reverse OS Interlanguage Runtime Extension Report

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [F18A_OS_TRAD_IR_REVERSE_PAYLOAD_8000_20260528_003836.json](../runtime/F18A_OS_TRAD_IR_REVERSE_PAYLOAD_8000_20260528_003836.json)
- [F18A_OS_TRAD_IR_REVERSE_PAYLOAD_8012_20260528_003836.json](../runtime/F18A_OS_TRAD_IR_REVERSE_PAYLOAD_8012_20260528_003836.json)
- [OBSIDIA_F18A_OS_TRAD_IR_REVERSE_LIVE_AUDIT_20260528_003836.json](../runtime/OBSIDIA_F18A_OS_TRAD_IR_REVERSE_LIVE_AUDIT_20260528_003836.json)
- [OBSIDIA_F18A_OS_TRAD_IR_REVERSE_LIVE_AUDIT_20260528_003836.txt](../runtime/OBSIDIA_F18A_OS_TRAD_IR_REVERSE_LIVE_AUDIT_20260528_003836.txt)
- [OBSIDIA_F18B_EXISTING_REVERSE_OS_IR_READONLY_WIRING_REPORT_20260528_030305.md](../runtime/OBSIDIA_F18B_EXISTING_REVERSE_OS_IR_READONLY_WIRING_REPORT_20260528_030305.md) — OBSIDIA F18B — EXISTING REVERSE OS / IR READONLY WIRING

</details>

## Fichiers liés au code

15 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
