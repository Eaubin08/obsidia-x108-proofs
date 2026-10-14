# Runtime Truth Repairs — Validation — 2026-10-08

Scope: Obsidure MathMemory, CLI runtime truth, Brody active memory truth.

Aucun fichier sous `proofs/` ou `proofs/lean/` n'a ete modifie par ce chantier.

## Branch chain

- `repair/obsidure-mathmemory-20261008`
- `repair/cli-runtime-truth-20261008`
- `repair/brody-native-memory-cleanup-20261008`

## Repairs

### Obsidure MathMemory

The optional `research_context` hook no longer breaks the indexed MathMemory path when absent.
Fallback remains the existing readonly provider surface.

### CLI runtime truth

Active runtime:
- API 8000
- Sigma F63 readonly routes
- Native Memory

Legacy / historical:
- Graphiti 8011
- Neo4j 7475/7688
- UI 5173

Kernel 3001 is observed conservatively as a socket surface; no fake GET health claim is made.

### Brody active memory truth

The active Brody memory projection no longer depends on the legacy
`graphiti_memory_readonly_activation` state.

Top-level memory truth is derived from the already active Native Memory project snapshot:
- `source_mode = OBSIDIA_NATIVE_MEMORY`
- `native_memory_ready`
- `memory_write = false`
- `decision_authority = KX108_ONLY`

## User-validated targeted regression

Executed locally on Windows from the branch chain:

- `tests/test_obsidure_math_memory_context_pack.py` → 2 passed
- `tests/test_obsidure_math_memory_provider.py` → 13 passed
- `tests/gates/test_obsidia_runtime_service_map_v1.py` → 30 passed
- `tests/test_brody_native_memory_active_truth_20261008.py` → 2 passed
- `tests/test_brody_top_level_p52_provider_aliases_removed_c2b_m4d3b_b3a1.py` → 3 passed
- `tests/test_brody_route_no_graphiti_guard_c2b_m4d1b_a.py` → 4 passed

Total targeted validation: **54 passed, 0 failed**.

Observed warning:
- Starlette TestClient deprecation warning regarding `httpx`; non-blocking for this repair scope.

## Verdict

```text
OBSIDURE_MATHMEMORY_REPAIR = GREEN
CLI_RUNTIME_TRUTH_REPAIR = GREEN
BRODY_NATIVE_MEMORY_TRUTH_REPAIR = GREEN
PROOFS_TREE_TOUCHED = NO
```

Next gate: broader regression before freezing this runtime-truth repair chain.
