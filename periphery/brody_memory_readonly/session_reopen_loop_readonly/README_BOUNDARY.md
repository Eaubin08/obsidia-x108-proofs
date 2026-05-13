# BRODY SESSION REOPEN LOOP READONLY V1

## Purpose

Prove that a future Brody session can reopen from the frozen/closed memory pipeline and recover a usable readonly context packet.

## Inputs

- Brody Memory Pipeline V2 close report
- Brody Memory Readonly Micro Smoke
- Guarded manual Graphiti memory-only apply execution pointer

## Expected

- 29 memory-only applied IDs found by exact replay
- 0 missing IDs
- `BRODY_GRAPHITI_MEMORY_ONLY` retrieves the 29 applied records
- Reopen context packet generated
- Prompt context generated
- No write

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

BUILD_BRODY_MEMORY_SCHEDULER_READONLY_V1
