# BRODY POST GRAPHITI REPLAY QUERY REGRESSION READONLY V1

## Purpose

Prove that the 29 manually applied Graphiti memory-only records are not only present by ID, but also retrievable through readonly memory queries.

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

## Regression

Expected:

- 29 applied IDs found by exact replay
- 0 missing IDs
- query BRODY_GRAPHITI_MEMORY_ONLY retrieves the applied records

## Next

BRODY_MEMORY_PIPELINE_FREEZE_V2
