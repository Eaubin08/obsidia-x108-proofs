# Graphiti No-Write Policy V1

**Status:** ABSOLUTE INVARIANT
**Role:** Absolute prohibition on Neo4j writes and Graphiti graph mutations.
**Modules:** `graphiti_readonly_bridge.py`, `graphiti_context_adapter.py`, `graphiti_freeze_snapshot_reader.py`

## The Invariant

**Graphiti ne décide pas. Graphiti n'écrit pas.** The Graphiti knowledge graph is read-only within the X-108 governance perimeter. No module, agent, or process can write to Neo4j or mutate Graphiti data.

## Enforcement

- `neo4j_write = False` in every query result
- `graphiti_write = False` in every query result
- `assert_graphiti_no_write()` validation function
- `readonly = True` in bridge configuration
- `decision_authority = "KX108_ONLY"` in every result

## Why

Graphiti provides context. Context is signal. Signal is not decision. Writing to the knowledge graph would:
- Bypass the X108 authority gate
- Allow ungoverned memory modification
- Create unverifiable graph state changes

## What Graphiti CAN Do

- Query nodes and relationships
- Traverse the knowledge graph
- Provide context enrichment
- Return entity data
- Read frozen snapshots

## What Graphiti CANNOT Do

- Write to Neo4j
- Mutate graph data
- Create/delete nodes
- Create/delete relationships
- Modify episode data
- Emit ACT
- Issue decisions

## Tests

- `tests/non_sovereignty/test_graphiti_no_write.py` (5 assertions)
- `tests/periphery/test_graphiti_readonly_bridge.py`
- `tests/non_sovereignty/test_graphiti_bridge_readonly_only.py`

## Status

**GRAPHITI_NO_WRITE_PASS** — Absolute invariant. Never broken.
