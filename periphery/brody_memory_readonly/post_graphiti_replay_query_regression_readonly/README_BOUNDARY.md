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

## V1_1_SCALAR_SAFE_REPLAY

Fixes the failed replay caused by `toString(n[k])` on array properties.

The replay now queries only scalar fields expected from the memory-only apply layer:

- id
- name
- title
- source
- record_hash

Still readonly.
Still no Graphiti write.
Still no Neo4j write.
Still no memory decision.

## V1_2_SCALAR_SAFE_PARAM_FIX

Fixes the Neo4j Python driver conflict:

Session.run(cypher, query=query, limit=limit)

`query` is reserved as the first Session.run parameter.
The Cypher parameter is now `$q`, passed as `q=query`.

Still readonly.
Still no Graphiti write.
Still no Neo4j write.
Still no memory decision.
