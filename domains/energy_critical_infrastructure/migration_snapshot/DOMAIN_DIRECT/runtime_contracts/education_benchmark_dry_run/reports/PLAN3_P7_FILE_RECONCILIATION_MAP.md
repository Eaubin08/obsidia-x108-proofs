# PLAN3_P7_FILE_RECONCILIATION_MAP
# runtime_contracts/education_benchmark_dry_run/reports/
# Plan 3 P7 Reconciliation Patch — Canonical file mapping
# Date: 2026-06-02
# Status: RECONCILIATION_MAP

---

## Contexte

P7 initial a produit 12 fichiers avec des noms internes (non canoniques).
Ce patch crée les fichiers canoniques qui référencent les fichiers existants.
Aucun fichier existant n'est supprimé ni écrasé.

---

## Canonical file map

| Expected canonical file | Existing file (P7 initial) | Status | Action |
|---|---|---|---|
| `scenarios/EDUCATION_BENCHMARK_SCENARIO_CATALOG.md` | `scenarios/EDUCATION_SCENARIOS_DRY_RUN.md` | MISSING_CANONICAL | CREATED by patch |
| `failure_modes/EDUCATION_BENCHMARK_FAILURE_MODES.md` | `failure_modes/FAILURE_MODES_SPEC.md` | MISSING_CANONICAL | CREATED by patch |
| `reports/PLAN3_P7_EDUCATION_BENCHMARK_DRY_RUN_SPEC_REPORT.md` | `reports/REPORT_1_ARCHITECTURE.md` | MISSING_CANONICAL | CREATED by patch |
| `reports/PLAN3_P7_SCOPE_VERIFICATION.md` | `reports/REPORT_2_SCOPE_CHECK.md` | MISSING_CANONICAL | CREATED by patch |
| `reports/PLAN3_P7_NEXT_STEPS.md` | `reports/REPORT_3_NEXT_STEPS.md` | MISSING_CANONICAL | CREATED by patch |
| `reports/PLAN3_P7_FILE_RECONCILIATION_MAP.md` | _(absent)_ | MISSING | CREATED (ce fichier) |
| `reports/PLAN3_P7_RECONCILIATION_PATCH_REPORT.md` | _(absent)_ | MISSING | CREATED by patch |

---

## Fichiers P7 initiaux conservés (non supprimés, non renommés)

| Fichier | Statut |
|---------|--------|
| `specs/EDUCATION_BENCHMARK_DRY_RUN_SPEC.md` | KEPT — nom correct |
| `metrics/EDUCATION_METRICS_CANDIDATE_SPEC.md` | KEPT — nom correct |
| `examples/EDUCATION_BENCHMARK_EXAMPLES.md` | KEPT — nom correct |
| `scenarios/EDUCATION_SCENARIOS_DRY_RUN.md` | KEPT — référencé par canonical |
| `failure_modes/FAILURE_MODES_SPEC.md` | KEPT — référencé par canonical |
| `reports/REPORT_1_ARCHITECTURE.md` | KEPT — référencé par canonical |
| `reports/REPORT_2_SCOPE_CHECK.md` | KEPT — référencé par canonical |
| `reports/REPORT_3_NEXT_STEPS.md` | KEPT — référencé par canonical |
| `pipeline/EDUCATION_BENCHMARK_PIPELINE_SPEC.md` | KEPT — dossier non canonique mais valide |
| `anti_bypass/ANTI_BYPASS_EDUCATION_SPEC.md` | KEPT — dossier non canonique mais valide |
| `os3/OS3_EVIDENCE_EDUCATION_BINDING_SPEC.md` | KEPT — dossier non canonique mais valide |
| `boundary/EDUCATION_BOUNDARY_SPEC.md` | KEPT — dossier non canonique mais valide |

---

## Écarts de contenu

| Dimension | Attendu | P7 initial | Patch action |
|-----------|---------|-----------|--------------|
| Scénarios | ≥ 20 | 7 | Catalog complété à 20 |
| Failure modes | ≥ 20 | 10 | Catalog complété à 20 |
| Rapports canoniques PLAN3_P7_* | 3 | 0 | Créés (4 avec réconciliation) |

---

## Backup guard

```
Fichiers existants modifiés : 0
Backups requis : 0
Backup guard violation : NO
```
