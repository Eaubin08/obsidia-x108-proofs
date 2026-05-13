# BRODY MEMORY READONLY MICRO SMOKE V1

## Purpose

Prove that the Brody memory-only Graphiti records are readable after Freeze V2 close.

## Expected

- 29 memory-only applied IDs found by exact replay
- 0 missing IDs
- `BRODY_GRAPHITI_MEMORY_ONLY` query retrieves the 29 applied records
- readonly query path works

## Boundary

- Graphiti query read: true
- Graphiti write: false
- Neo4j write: false
- Memory intake: false
- Memory decision: false
- Emits ACT: false
- Emits verdict: false
- Kernel mutation: false
- X108 runtime binding: false
- X108 merge: false

## Next

BUILD_BRODY_SESSION_REOPEN_LOOP_READONLY_V1
