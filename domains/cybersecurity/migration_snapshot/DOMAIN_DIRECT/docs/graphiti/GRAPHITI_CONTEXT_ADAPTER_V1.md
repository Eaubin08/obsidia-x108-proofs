# Graphiti Context Adapter V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Adapts Graphiti query results into context packets for downstream consumption.
**Module:** `periphery/graphiti/graphiti_context_adapter.py`
**Runtime:** READONLY

## Role

The Graphiti Context Adapter transforms raw Graphiti graph results into structured context packets that can be consumed by Brody, memory candidates, and the X108 ingress. It enriches queries with graph-derived context but never writes back to the graph.

## Inputs

- `graphiti_result: GraphitiContextResult` — raw Graphiti query output
- `context_packet_id: str` — target context packet identifier

## Outputs

- `AdaptedContext` with fields:
  - `context_id: str`
  - `nodes: list` — adapted node data
  - `relationships: list` — adapted relationship data
  - `source: str` — always "graphiti_readonly"
  - `no_write: bool` — always True

## Forbidden Actions

| Action | Status |
|--------|--------|
| Graphiti write | BLOCKED |
| Context modification | BLOCKED — adapter only |
| Decision | BLOCKED — KX108_ONLY |

## Tests

- `tests/non_sovereignty/test_graphiti_no_write.py` (context_adapter_no_write)

## Status

**GRAPHITI_NO_WRITE_PASS** — Adapter only. No write. No decision.
