# Graphiti Module

**Status:** FIRST_CLASS_X108_MODULE — READONLY / NO WRITE
**Source:** `periphery/graphiti/` (3 modules)
**Tests:** `tests/periphery/test_graphiti_*.py` + `tests/non_sovereignty/test_graphiti_*.py`

## Modules

| Module | Role | Write |
|--------|------|-------|
| `graphiti_readonly_bridge.py` | Read-only query interface to Graphiti | NONE |
| `graphiti_context_adapter.py` | Adapts Graphiti results to context packets | NONE |
| `graphiti_freeze_snapshot_reader.py` | Reads frozen Graphiti snapshots | NONE |

## Sovereignty Invariants

- `neo4j_write = False` — never writes to Neo4j
- `graphiti_write = False` — never writes to Graphiti
- `decision_authority = "KX108_ONLY"` — never decides
- `readonly = True` — all operations read-only
- `emits_act = False` — never emits ACT

## Relation to X108

Graphiti contextualizes. X108 decides. Graphiti provides graph-based context and relationship mapping — it never writes to the graph database and never makes governance decisions.

## Canonical Rules

- Graphiti contextualise mais ne décide pas
- Graphiti = contexte, contexte = signal, signal ≠ décision
- Neo4j write blocked absolutely
