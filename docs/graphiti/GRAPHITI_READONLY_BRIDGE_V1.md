# Graphiti Read-Only Bridge V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Read-only query bridge to Graphiti knowledge graph.
**Module:** `periphery/graphiti/graphiti_readonly_bridge.py`
**Runtime:** READONLY — NO WRITE

## Role

The Graphiti Read-Only Bridge provides a query interface to the Graphiti knowledge graph for context enrichment. It reads graph relationships, entity data, and episode history — but never writes to Neo4j or Graphiti.

## Inputs

- `query_id: str` — unique query identifier
- `query: str` — natural language or structured query
- `max_nodes: int` — maximum nodes to return (default 20)

## Outputs

- `GraphitiContextResult` with fields:
  - `query_id: str`
  - `nodes: list` — matched graph nodes
  - `relationships: list` — matched edges
  - `neo4j_write: bool` — always False
  - `graphiti_write: bool` — always False
  - `decision_authority: str` — always "KX108_ONLY"

## Forbidden Actions

| Action | Status |
|--------|--------|
| Neo4j write | BLOCKED — neo4j_write=False |
| Graphiti write | BLOCKED — graphiti_write=False |
| Graph mutation | BLOCKED — readonly=True |
| Decision authority | BLOCKED — KX108_ONLY |

## Additional Protection

`assert_graphiti_no_write()` validates that no write operations are present in the result.

## Tests

- `tests/periphery/test_graphiti_readonly_bridge.py`
- `tests/non_sovereignty/test_graphiti_no_write.py` (5 assertions)

## Status

**GRAPHITI_READONLY_BRIDGE_PASS** — Read-only. No write. Ever.
