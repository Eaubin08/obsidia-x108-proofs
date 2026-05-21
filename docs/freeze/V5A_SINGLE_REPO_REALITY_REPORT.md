# V5A Single Repo Reality Report

**Date:** 2026-05-19
**Phase:** 0 — Reality Check
**Status:** SINGLE_REPO_SOURCE_OF_TRUTH_CONFIRMED

---

## Verdict

**SINGLE_REPO_SOURCE_OF_TRUTH_PASS** — `obsidia-x108-proofs` is fully self-sufficient. No functional dependency on `Demo-obsidia-x108-proof`.

---

## Repository Inventory

### obsidia-x108-proofs (SOURCE OF TRUTH)

| Area | Count | Status |
|------|-------|--------|
| `periphery/` modules | 216 .py files, 14 subdirectories | COMPLETE |
| `tests/periphery/` | 76 test files | COMPLETE |
| `tests/non_sovereignty/` | 24 test files | COMPLETE |
| `tests/integration/` | 14 test files | COMPLETE |
| `docs/` | 85+ files, 20+ subdirectories | PARTIAL (see gaps) |
| `scripts/` | ~20 PS1 scripts | PARTIAL (3 reference Demo) |
| `sigma/` | 4 files | PROTECTED |
| `proofs/lean/` | formal proofs | PROTECTED |
| `formal/tla/` | TLA+ specs | PROTECTED |
| `merkle_seal.json` | 1 file | PROTECTED |

### Demo-obsidia-x108-proof (ARCHIVE)

| Path | Size | Status |
|------|------|--------|
| `connectors/action_lifecycle_full_stack_flow.py` | 3,043 B | OBSOLETE (broken imports) |
| `connectors/feedback_memory_candidate_flow.py` | 1,283 B | OBSOLETE (stale paths) |
| `connectors/world_action_dry_run_flow.py` | 2,148 B | OBSOLETE (broken imports) |

**Total: 3 files, 6.5 KB** — all superseded by periphery modules and tests.

---

## Import Dependency Analysis

### Python imports from Demo → x108-proofs: NONE

All periphery modules import only from `periphery.*` (self-contained). Zero imports reference `Demo-obsidia-x108-proof`.

### Broken imports in Demo connectors

| Connector | Broken Import | Correct Path |
|-----------|--------------|--------------|
| `action_lifecycle_full_stack_flow.py` | `periphery.agents.control_plane` | `periphery.common` (ActionCandidate) |
| `action_lifecycle_full_stack_flow.py` | `OS3ProofTicket` | `OS3ReplayManifest` (class renamed) |
| `world_action_dry_run_flow.py` | `WorldCallClass.READ_ONLY` | Likely stale enum value |

The 3 Demo connectors cannot execute as-is — they reference module paths and class names that don't exist in the current codebase. They are **OBSOLETE** and need complete rewrite.

### PS1 scripts referencing Demo

| Script | Demo Reference |
|--------|---------------|
| `TEST_ACTION_LIFECYCLE_FULL_STACK.ps1` | Calls `Demo-obsidia-x108-proof/connectors/action_lifecycle_full_stack_flow.py` |
| `TEST_FEEDBACK_MEMORY_CANDIDATE.ps1` | Calls `Demo-obsidia-x108-proof/connectors/feedback_memory_candidate_flow.py` |
| `TEST_WORLD_ACTION_DRY_RUN.ps1` | Calls `Demo-obsidia-x108-proof/connectors/world_action_dry_run_flow.py` |

---

## Test Independence Verification

`python -m pytest tests/ -q` → 397 passed, 0 failed — zero Demo dependency.

All tests import from `periphery.*` only. The `tests/` directory is fully self-contained.

---

## Conclusion

`obsidia-x108-proofs` is the single source of truth. `Demo-obsidia-x108-proof` contains 3 obsolete connector scripts with broken imports and is safe to archive. The 3 PS1 scripts referencing Demo must be updated to point to internal flows (Phase 1).
