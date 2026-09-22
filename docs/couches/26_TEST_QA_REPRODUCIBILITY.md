# 26 · Tests, QA, reproductibilité

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Ce qui valide le comportement et la reproductibilité.

## Où elle intervient dans le trajet d'une demande

- **Étape 5 · Preuves et gouvernance** : Tests, replay, Lean, ProofKit, receipts et checkpoints établissent ce qui est prouvé, avant tout passage au réel.

Voir le trajet complet : [guide général](../README.md).

## Où est son code aujourd'hui

**Points d'entrée connus :**

- [qa/cross-platform/](../../qa/cross-platform) · QA multi-plateforme RFC3161, TLC, Sigma

D'après le registre de fonctionnalités V3, **564 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `tests/` | 145 |
| `tests/api/` | 129 |
| `tests/periphery/` | 81 |
| `tests/gates/` | 38 |
| `tests/non_sovereignty/` | 35 |
| `sigma/tests/` | 22 |
| `tests/integration/` | 19 |
| `scripts/` | 17 |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 14 |
| `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/` | 10 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (19)

### Documents de référence — à lire en premier

- [Benchmarks Module](../benchmarks/README.md) · `docs/benchmarks/README.md`
  <br>Benchmark case schema and evaluation. Defines test cases for evaluating agent performance. Benchmark results are advisory context only — they inform X108 but never substitute…
- [Obsidia Fast Path A/B Benchmark Protocol V1](../performance/OBSIDIA_FAST_PATH_AB_BENCHMARK_PROTOCOL_V1.md) · `docs/performance/OBSIDIA_FAST_PATH_AB_BENCHMARK_PROTOCOL_V1.md`
  <br>Document type: Benchmark Protocol
- [Obsidia Request Cost Ledger Protocol V0](../performance/OBSIDIA_REQUEST_COST_LEDGER_PROTOCOL_V0.md) · `docs/performance/OBSIDIA_REQUEST_COST_LEDGER_PROTOCOL_V0.md`
  <br>Document type: Cost Measurement Protocol
- [CI Pipeline — X108 Periphery V1](../ci/CI_PIPELINE_X108_PERIPHERY_V1.md) · `docs/ci/CI_PIPELINE_X108_PERIPHERY_V1.md` *(référence probable)*
  <br>CIPIPELINECREATEDPASS — 6 gates, all automated.
- [Obsidia Domain Connector Burst Cost Metrics V0](../performance/OBSIDIA_DOMAIN_CONNECTOR_BURST_COST_METRICS_V0.md) · `docs/performance/OBSIDIA_DOMAIN_CONNECTOR_BURST_COST_METRICS_V0.md` *(référence probable)*
  <br>Document type: live measurement correction
- [Obsidia Fast Path Metric Crosswalk V1](../performance/OBSIDIA_FAST_PATH_METRIC_CROSSWALK_V1.md) · `docs/performance/OBSIDIA_FAST_PATH_METRIC_CROSSWALK_V1.md` *(référence probable)*
  <br>Ce document établit la correspondance entre les micro-métriques brutes du Fast Path Runtime
- [Obsidia Fast Path Runtime — Technical Note V0](../performance/OBSIDIA_FAST_PATH_RUNTIME_TECHNICAL_NOTE_V0.md) · `docs/performance/OBSIDIA_FAST_PATH_RUNTIME_TECHNICAL_NOTE_V0.md` *(référence probable)*
  <br>Document type: Technical Note
- [Obsidia Request Cost Ledger Real Routes Wiring V0](../performance/OBSIDIA_REQUEST_COST_LEDGER_REAL_ROUTES_WIRING_V0.md) · `docs/performance/OBSIDIA_REQUEST_COST_LEDGER_REAL_ROUTES_WIRING_V0.md` *(référence probable)*
  <br>Document type: wiring note
- [Obsidure Canon-Only Lean Closure Cost Metrics V0](../performance/OBSIDURE_CANON_ONLY_LEAN_CLOSURE_COST_METRICS_V0.md) · `docs/performance/OBSIDURE_CANON_ONLY_LEAN_CLOSURE_COST_METRICS_V0.md` *(référence probable)*
  <br>Document type: runbook
- [Obsidure Complete Lean Surface Cost Metrics V0](../performance/OBSIDURE_COMPLETE_LEAN_SURFACE_COST_METRICS_V0.md) · `docs/performance/OBSIDURE_COMPLETE_LEAN_SURFACE_COST_METRICS_V0.md` *(référence probable)*
  <br>Document type: full Lean surface measurement runbook
- [Obsidure Real Case Cost Metrics V0](../performance/OBSIDURE_REAL_CASE_COST_METRICS_V0.md) · `docs/performance/OBSIDURE_REAL_CASE_COST_METRICS_V0.md` *(référence probable)*
  <br>Document type: real-case measurement runbook

<details><summary><b>Rapports, audits et preuves d'exécution</b> (8)</summary>

**`docs/`**

- [PY_COMPILE_REPORT.md](../PY_COMPILE_REPORT.md) — Python Compile Report — V3+V4 Patch
- [TEST_RESULTS_FINAL.md](../TEST_RESULTS_FINAL.md) — Test Results — Final
- [TEST_RESULTS_V3_V4.md](../TEST_RESULTS_V3_V4.md) — Test Results — V3+V4 Patch

**`docs/freeze/`** · *dossier lu par du code : ne pas déplacer*

- [ZERO_FAIL_FULL_TEST_MATRIX_CLOSE_REPORT.md](../freeze/ZERO_FAIL_FULL_TEST_MATRIX_CLOSE_REPORT.md) — ZERO FAIL FULL TEST MATRIX CLOSE REPORT

**`docs/freeze/FULL_TEST_MATRIX_RECONCILIATION/`** · *dossier lu par du code : ne pas déplacer*

- [FULL_TEST_MATRIX_CLOSE_REPORT.md](../freeze/FULL_TEST_MATRIX_RECONCILIATION/FULL_TEST_MATRIX_CLOSE_REPORT.md) — FULL TEST MATRIX CLOSE REPORT
- [TEST_COUNT_RECONCILIATION_REPORT.md](../freeze/FULL_TEST_MATRIX_RECONCILIATION/TEST_COUNT_RECONCILIATION_REPORT.md) — TEST COUNT RECONCILIATION REPORT

**`docs/performance/`** · *dossier lu par du code : ne pas déplacer*

- [OBSIDIA_LIVE_ROUTE_REAL_CASE_COST_METRICS_V0.md](../performance/OBSIDIA_LIVE_ROUTE_REAL_CASE_COST_METRICS_V0.md) — Obsidia Live Route Real Case Cost Metrics V0
- [OBSIDIA_LIVE_STACK_COST_METRICS_V0.md](../performance/OBSIDIA_LIVE_STACK_COST_METRICS_V0.md) — Obsidia Live Stack Cost Metrics V0

</details>

## Fichiers liés au code

17 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
