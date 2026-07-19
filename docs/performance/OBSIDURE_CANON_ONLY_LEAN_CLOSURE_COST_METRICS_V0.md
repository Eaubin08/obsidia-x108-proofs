# Obsidure Canon-Only Lean Closure Cost Metrics V0

## Status

Document type: runbook
Scope: canonical Lean closure only
Decision authority: KX108_ONLY

---

## Objective

This runner replaces the previous broad archaeological scan.

The previous complete scan intentionally discovered too much:

- backups
- ephemeral sandboxes
- publication copies
- wip files
- lowercase duplicate files
- lakefile.lean as if it were a proof

This runner verifies only the active canonical Lean closure.

---

## Included

Module builds from `proofs/lean`:

- `lake build Obsidia`
- `lake build Obsidia.Refinement`
- `lake build Obsidia.Peripheral`
- `lake build Obsidia.LegacyPeripheral`
- `lake build Obsidia.GeneratedPeripheral` as optional if available

Canonical file checks include tracked and manifest Lean files, excluding archives and non-canonical duplicates.

---

## Excluded

- `_BACKUP_ORIGINALS_*`
- `_EPHEMERAL_CODE_SANDBOX_*`
- `ci_recheck_optional_publication/*`
- `proofs/lean/wip/*`
- `proofs/lean/peripheral/*`
- `proofs/lean/lakefile.lean`

---

## Boundary

Each check appends a cost event with:

- `family = OBSIDURE_LEAN`
- `decision_authority = KX108_ONLY`
- `emits_act = false`
- `memory_write = false`
- `boundary_ok = true`

This runner does not modify proof files.
