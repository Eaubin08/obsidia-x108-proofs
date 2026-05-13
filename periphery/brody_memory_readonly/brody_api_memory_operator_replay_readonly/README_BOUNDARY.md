# BRODY API MEMORY OPERATOR REPLAY READONLY V1

## Purpose

Test the real readonly loop:

1. Brody command gate classification.
2. Local API readonly GET calls.
3. Memory/context readonly endpoint.
4. Human operator receipt shape.
5. Negative command classification.
6. X108 authority preservation.

## Current state

- source_head: ea03647
- build_target: obsidia-x108-proofs
- api_base: http://127.0.0.1:8011
- verify_all.py: PASS
- control_loop_clean_close: PASS
- candidate_build_target: false

## What was actually executed

Executed by human/operator script:

- GET /graph/v20/frozen/status
- GET /graph/v20/frozen/counts
- GET /graph/v20/frozen/readiness
- GET /graph/v20/frozen/context?q=X-108&limit=5
- GET /graph/v20/frozen/search?q=Brody&limit=5
- git status --short
- python smoke validator
- python proofs/verify_all.py

## What Brody did not do

- Brody did not execute commands.
- Brody did not authorize commands.
- Brody did not perform POST.
- Brody did not write Graphiti.
- Brody did not write Neo4j.
- Brody did not ingest memory.
- Brody did not decide.
- Brody did not emit ACT.
- Brody did not emit verdict.
- Brody did not bind X108 runtime.
- Brody did not mutate kernel.
- Brody did not merge X108.

## Boundary

- BRODY_EXECUTE_ALLOWED=false
- BRODY_AUTHORIZE_ALLOWED=false
- HUMAN_OPERATOR_REQUIRED=true
- READONLY_ANALYSIS_ONLY=true
- COMMAND_EXECUTED_BY_BRODY=false
- MEMORY_DECISION=false
- ALLOWED_TO_DECIDE=false
- EMITS_ACT=false
- EMITS_VERDICT=false
- DECISION_AUTHORITY=KX108_ONLY
- KERNEL_MUTATION=false
- X108_RUNTIME_BINDING=false
- X108_MERGE=false
- GRAPHITI_WRITE=false
- GRAPHITI_INDEX_WRITE=false
- NEO4J_WRITE_EXECUTED=false
- MEMORY_INTAKE=false
