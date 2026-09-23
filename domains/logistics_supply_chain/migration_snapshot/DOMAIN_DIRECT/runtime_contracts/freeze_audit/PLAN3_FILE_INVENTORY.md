# PLAN3_FILE_INVENTORY
# runtime_contracts/freeze_audit/
# Plan3 Freeze Audit — Inventaire complet runtime_contracts/
# Date: 2026-06-02
# Status: FREEZE_AUDIT_ONLY

---

## Résumé global

```
Total fichiers runtime_contracts/ : 109
Total dossiers                    : 46
Fichiers .py                      : 0
Packages présents                 : NON
Runtime actif                     : NON — DOCS_ONLY
Benchmark exécuté                 : NON
Données étudiants                 : NON
Commits                           : NON
```

---

## Inventaire par dossier

| Folder | File count | Role | Runtime active? |
|--------|----------:|------|----------------|
| `runtime_contracts/` (root) | 1 | README entrypoint | false |
| `runtime_contracts/boundaries/` | 13 | Boundary specs | false |
| `runtime_contracts/contracts/` | 7 | Contract definitions | false |
| `runtime_contracts/dry_run/` | 4 | Dry-run infra specs | false |
| `runtime_contracts/schemas/` | 7 | JSON schemas | false |
| `runtime_contracts/reports/` | 7 | P0 + P1 reports | false |
| `runtime_contracts/anti_bypass_tests_spec/` | 8 | P4 anti-bypass spec | false |
| `runtime_contracts/external_signals_dry_run/` | 8 | P2 external signals | false |
| `runtime_contracts/x108_gateway_dry_run_harness/` | 10 | P3 X108 gateway | false |
| `runtime_contracts/os3_evidence_dry_run/` | 11 | P5 OS3 evidence | false |
| `runtime_contracts/readonly_wrappers_spec/` | 14 | P6 readonly wrappers | false |
| `runtime_contracts/education_benchmark_dry_run/` | 19 | P7 education benchmark | false |
| **TOTAL** | **109** | | **false (all)** |

---

## Inventaire par phase

| Phase | Dossier principal | Fichiers | Verdict |
|-------|-----------------|---------|---------|
| P0 | `reports/` (P0_*), `contracts/`, `boundaries/`, `schemas/`, `dry_run/` | 32 | PLAN3_P0_RUNTIME_CONTRACT_SKELETON_READY |
| P1 | `reports/` (P1_*), `schemas/` | 11 | PLAN3_P1_PACKET_SCHEMA_AND_BOUNDARIES_READY |
| P2 | `external_signals_dry_run/` | 8 | PLAN3_P2_EXTERNAL_SIGNALS_DRY_RUN_SPEC_READY |
| P2C | `external_signals_dry_run/reports/` | (inclus P2) | PLAN3_P2_CORRECTION_READY_FOR_P3 |
| P3 | `x108_gateway_dry_run_harness/` | 10 | PLAN3_P3_X108_GATEWAY_DRY_RUN_HARNESS_SPEC_READY |
| P4 | `anti_bypass_tests_spec/` | 8 | PLAN3_P4_ANTI_BYPASS_TESTS_SPEC_READY |
| P5 | `os3_evidence_dry_run/` | 11 | PLAN3_P5_OS3_EVIDENCE_DRY_RUN_SPEC_READY |
| P6 | `readonly_wrappers_spec/` | 14 | PLAN3_P6_READONLY_WRAPPERS_SPEC_READY |
| P7 | `education_benchmark_dry_run/` | 19 | PLAN3_P7_EDUCATION_BENCHMARK_DRY_RUN_SPEC_READY + PLAN3_P7_RECONCILIATION_READY |

---

## Inventaire par type de fichier

| Type | Count | Dossiers |
|------|------:|---------|
| Reports (PLAN3_P*_*.md) | 34 | reports/, */reports/ |
| Specs (*_SPEC.md, *_DRY_RUN*.md) | 22 | */specs/, dry_run/ |
| Contracts (*.contract.md) | 7 | contracts/ |
| Schemas (*.schema.json) | 7 | schemas/ |
| Boundaries (*_ONLY.md, *_PRIORITY.md, *_REQUIRED.md) | 13 | boundaries/ |
| Examples (EXAMPLE_*.md) | 10 | */examples/ |
| Failure modes (*FAILURE_MODES*.md) | 8 | */failure_modes/ |
| Mappings (*_MAP.md) | 8 | */mapping/ |
| Matrices (*_MATRIX.md) | 2 | anti_bypass_tests_spec/matrices/ |
| Scenarios (*_CATALOG.md, *_SCENARIOS*.md) | 3 | */scenarios/ |
| Metrics (*_METRICS*.md) | 1 | education_benchmark_dry_run/metrics/ |
| README / entrypoints | 1 | root |
| **TOTAL** | **109** | |

---

## Détail P0 — Contrats + Boundaries + Schemas + Dry-run

| Fichier | Type | Phase |
|---------|------|-------|
| README.md | entrypoint | P0 |
| contracts/BoundaryContract.contract.md | contract | P0 |
| contracts/ContextPacket.contract.md | contract | P0 |
| contracts/DecisionTicket.contract.md | contract | P0 |
| contracts/IntentEnvelope.contract.md | contract | P0 |
| contracts/OS3EvidenceTicket.contract.md | contract | P0 |
| contracts/PeripheralSignalPacket.contract.md | contract | P0 |
| contracts/RuntimeAdmissionContract.contract.md | contract | P0 |
| boundaries/ (13 fichiers) | boundary | P0/P1 |
| schemas/ (7 fichiers JSON) | schema | P1 |
| dry_run/ (4 fichiers) | dry_run_infra | P0 |
| reports/PLAN3_P0_* (3 fichiers) | report | P0 |
| reports/PLAN3_P1_* (4 fichiers) | report | P1 |

---

## Détail P7 Education Benchmark (19 fichiers)

| Fichier | Type | Statut |
|---------|------|--------|
| specs/EDUCATION_BENCHMARK_DRY_RUN_SPEC.md | spec | SPEC_ONLY |
| metrics/EDUCATION_METRICS_CANDIDATE_SPEC.md | metrics | CANDIDATE_ONLY |
| scenarios/EDUCATION_BENCHMARK_SCENARIO_CATALOG.md | scenario | 20 scénarios |
| scenarios/EDUCATION_SCENARIOS_DRY_RUN.md | scenario | 7 initiaux |
| examples/EDUCATION_BENCHMARK_EXAMPLES.md | example | DOC_ONLY |
| failure_modes/EDUCATION_BENCHMARK_FAILURE_MODES.md | failure_mode | 20 modes |
| failure_modes/FAILURE_MODES_SPEC.md | failure_mode | 10 initiaux |
| pipeline/EDUCATION_BENCHMARK_PIPELINE_SPEC.md | spec | PIPELINE_SPEC_ONLY |
| anti_bypass/ANTI_BYPASS_EDUCATION_SPEC.md | spec | ANTI_BYPASS_SPEC_ONLY |
| os3/OS3_EVIDENCE_EDUCATION_BINDING_SPEC.md | spec | THEORETICAL_ONLY |
| boundary/EDUCATION_BOUNDARY_SPEC.md | boundary | BOUNDARY_SPEC_ONLY |
| reports/PLAN3_P7_* (5 fichiers) | report | CANONICAL |
| reports/REPORT_1/2/3_*.md (3 fichiers) | report | INITIAL (conservés) |
