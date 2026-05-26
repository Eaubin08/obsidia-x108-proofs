# DO NOT TOUCH Report — V3+V4 Patch

**Date:** 2026-05-19

The following files were verified untouched during the entire V3+V4 patch. Any modification to these files requires explicit user approval and a formal verification plan.

## Kernel (FROZEN)

| File | Status |
|---|---|
| `sigma/guard.py` | FROZEN — X-108 gate logic |
| `sigma/contracts.py` | FROZEN — domain contracts |
| `sigma/protocols.py` | FROZEN — Sigma protocols |
| `sigma/aggregation.py` | FROZEN — aggregation logic |

## Formal Proofs (FROZEN)

| Path | Status |
|---|---|
| `proofs/lean/` | FROZEN — all Lean4 proof files |
| `formal/tla/` | FROZEN — all TLA+ specs |

## Cryptographic Anchors (FROZEN)

| File | Status |
|---|---|
| `merkle_seal.json` | FROZEN — Merkle root seal |
| `rfc3161*.tsr` | FROZEN — RFC3161 timestamps |

## Rule

**No periphery module may call, modify, or bypass any of the above.** If any test or module requires importing from `sigma/`, it must be read-only (import the dataclass types, not the decision functions). The kernel X-108 is the sole sovereign authority.
