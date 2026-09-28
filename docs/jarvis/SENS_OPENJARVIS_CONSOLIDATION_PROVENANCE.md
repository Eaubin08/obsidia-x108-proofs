# Jarvis Cognition Consolidation Provenance

This target worktree consolidates useful SENS cognition code and the bounded governed OpenJarvis integration delta without merging Git histories and without importing a second repository.

## Sources

- SENS source: `C:\Users\User\Desktop\obsidia-semantic-grammar-claude-v0`
- SENS branch/head: `exp/semantic-grammar-cognitive-lattice-v0 @ 85d55e35`
- OpenJarvis integration source: `C:\Users\User\Desktop\OBSIDIA_ACTIVE_BUILD\OpenJarvis-Obsidia`
- OpenJarvis branch/head: `feat/obsidia-governed-ui-v0 @ 915153b`

## Migrated SENS Capabilities

- semantic lattice primitives and PredicateUnit model
- ordered meaning flow and language-flow projections
- complement commitment and unresolved-governor fail-closed handling
- occurrence claims/projections/derivations
- event primitives, extraction, event index, temporal attachment
- observation/knowledge event target extraction
- explicit nominal event-reference resolution
- relation/status distinctions for content, scope, commitment, occurrence, epistemic, evidence, verification and authority
- supporting docs under `docs/semantic/`

## Migrated OpenJarvis Delta

Only the governed Obsidia/OpenJarvis delta from commit `915153b` is preserved under `apps/openjarvis_obsidia_bridge/`:

- governed action card UI
- OpenJarvis server-side Obsidia governance transport proxy
- model boundary tests and governed route tests

This is not a nested OpenJarvis repository. It intentionally excludes `.git`, dependencies, caches, lockfile migration, build outputs, and upstream OpenJarvis bulk source.

## Authority Invariants

- `KX108_ONLY` remains the decision authority.
- `memory_write=False` for migrated cognition surfaces.
- `emits_act=False` for migrated cognition surfaces.
- `kernel_mutation=False` for migrated cognition surfaces.
- SENS represents and distinguishes meaning; it does not authorize execution.
- OpenJarvis UI/transport surfaces proxy bounded requests; they do not decide or execute.
