# SENS / OpenJarvis Residual Parity Audit

Target: `C:\Users\User\Desktop\obsidia-jarvis-advanced-integration-v0`
Base consolidation commit: `d99f115d`

## Sources Audited

- SENS: `C:\Users\User\Desktop\obsidia-semantic-grammar-claude-v0` @ `85d55e35`
- OpenJarvis-Obsidia: `C:\Users\User\Desktop\OBSIDIA_ACTIVE_BUILD\OpenJarvis-Obsidia` @ `915153b`

## Residual Classification Summary

### SENS

Required residuals found after `d99f115d`:

- REQUIRED_TEST: additional semantic-lattice, occurrence, event-reference, review-join, relation-status, dynamic invariant, and semantic projection tests.
- REQUIRED_EVIDENCE: deterministic semantic matrix and dynamic case generators used by the imported tests.

Migrated in the residual pass:

- `benchmarks/dynamic_cases.py`
- `benchmarks/dynamic_cases_v2.py`
- `tests/__init__.py`
- `tests/semantic_grammar_matrix.py`
- semantic residual tests covering belief/report event relations, conditional event occurrence, event coreference/indexing, event anaphora, target contextual invariants, occurrence derivation/migration/ancestry, meta-target selection, nominal references, relation status, review join/provenance, semantic governance/action projections, dynamic invariants, and grammar regressions.

Residual SENS files not migrated are classified as:

- OUT_OF_SCOPE: Track1/Track3 competition harnesses, model/provider triage, Qwen/Fireworks/Brody adapter tests, submission scaffolding, benchmark runners unrelated to the consolidated Jarvis/SENS semantic behavior.
- HISTORICAL_ONLY: challenge reports and old result summaries not needed for runtime, tests, docs, or provenance.
- UPSTREAM_ONLY: Dockerfiles, external model smoke scripts, adapter-specific utilities, and packaging surfaces from the original SENS project.
- BUILD_ARTIFACT/CACHE: generated outputs and local cache paths are intentionally excluded.

SENS_RESIDUAL_REQUIRED after this pass: NONE.

### OpenJarvis-Obsidia

The useful Obsidia delta from commit `915153b` was already preserved under `apps/openjarvis_obsidia_bridge/`:

- governed UI action card and API surface
- governance transport proxy
- server model-surface lock invariant
- governed stream route invariant
- tests proving `AUTHORITY = "NONE"` and `DECISION_AUTHORITY = "KX108_ONLY"`

The original upstream OpenJarvis repository contents remain classified as:

- UPSTREAM_ONLY: full upstream OpenJarvis application, server, frontend, rust crates, deployment files, assets, and broad tests.
- BUILD_ARTIFACT/CACHE: lock/build/cache/generated outputs are intentionally excluded.
- OUT_OF_SCOPE: non-Obsidia OpenJarvis functionality not required by Jarvis governed integration.

OPENJARVIS_RESIDUAL_REQUIRED after this pass: NONE.

## Deletion Readiness

These folders are redundant for the consolidated target content after this audit, but this report does not delete them:

- `C:\Users\User\Desktop\obsidia-semantic-grammar-claude-v0`
- `C:\Users\User\Desktop\OBSIDIA_ACTIVE_BUILD\OpenJarvis-Obsidia`

Do not delete them until the pushed branch is reviewed/accepted by the user.

## Invariants

- `KX108_ONLY` remains the decision authority.
- SENS cognition has no autonomous execution authority.
- OpenJarvis bridge authority remains `NONE`.
- No `.git`, cache, dependency directory, build artifact, nested repository, or full upstream OpenJarvis import was migrated.
