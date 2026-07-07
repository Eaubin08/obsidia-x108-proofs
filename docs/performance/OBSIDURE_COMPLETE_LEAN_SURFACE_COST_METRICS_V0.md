# Obsidure Complete Lean Surface Cost Metrics V0

## Status

Document type: full Lean surface measurement runbook
Status: V0
Scope: manifest + git tracked + git untracked + filtered repo scan
Decision authority: KX108_ONLY

---

## 1. Objective

The previous all-Lean runner focused on `proofs/lean`.

This runner expands the scope to include the original base Lean surface as well.

It discovers Lean files from:

- `proofs/LEAN_PROOF_SURFACE_MANIFEST.json`
- git tracked `*.lean`
- git untracked `*.lean`
- `proofs/lean/**/*.lean`
- `proofs/**/*.lean`
- `src/**/*.lean`
- `Obsidia/**/*.lean`
- filtered repo scan

---

## 2. Groups

| Group | Meaning |
|---|---|
| PERIPHERAL_15 | canonical peripheral Lean surface |
| LEGACY_PERIPHERAL_27 | legacy peripheral Lean surface |
| LOWERCASE_PERIPHERAL_OR_V3 | lowercase or later provisional peripheral surface |
| BASE57_ORIGINAL_OR_CORE | original base/core/kernel/canonical Lean surface |
| OTHER_LEAN | Lean files outside known groups |

---

## 3. Method

For each discovered Lean file:

    lake env lean <file>

A cost event is appended to:

    .local_reports/REQUEST_COST_EVENTS/cost_events.jsonl

Each event uses:

    family = OBSIDURE_LEAN
    route = COMPLETE_LEAN::<path>
    decision_authority = KX108_ONLY
    emits_act = false
    memory_write = false

---

## 4. Output

The runner writes:

    .local_reports/OBSIDURE_COMPLETE_LEAN_SURFACE_COST_METRICS_<timestamp>/summary.json
    .local_reports/OBSIDURE_COMPLETE_LEAN_SURFACE_COST_METRICS_<timestamp>/summary.md

The summary includes:

- total files
- PASS / FAIL / TIMEOUT
- p50 / p95 latency
- slowest files
- failure previews
- grouping by Lean surface
- grouping by discovery source
- base57/core count

---

## 5. Boundary

This runner only checks Lean files.

It does not apply proposals.

It does not modify proof files.

It does not emit ACT.

It does not write memory.

X108 remains the decision authority.

## Hard exclusions

The complete Lean surface metrics runner must not include archival or ephemeral surfaces.

Excluded from discovery:

- `_BACKUP_ORIGINALS_*`
- `_EPHEMERAL_CODE_SANDBOX_*`
- `ci_recheck_optional_publication/*`
- `.lake/*`
- `.git/*`
- `__pycache__/*`

This keeps the metric surface focused on current repository Lean material, not backup copies.
