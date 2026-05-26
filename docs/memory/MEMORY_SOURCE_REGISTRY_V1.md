# Memory Source Registry V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Registers and validates memory source types.
**Module:** `periphery/memory/memory_source_types.py` + `memory_source_registry.py`
**Runtime:** READONLY

## Role

The Memory Source Registry defines the valid types of memory sources and validates that each memory candidate comes from an authorized source. It classifies sources but never decides on promotion.

## Source Types

| Type | Description |
|------|-------------|
| BRODY_RUNTIME | Context from Brody responses |
| GRAPHITI_GRAPH | Context from Graphiti queries |
| DOCUMENT_INGESTION | Ingested document content |
| CONTEXT_PACKET | Structured context packets |
| FEEDBACK_CAPTURE | User feedback capture |
| OPERATOR_SESSION | Session context |
| HUMAN_REVIEW | Human review input |
| UNKNOWN | Unclassified source |

## Candidate Statuses

| Status | Description |
|--------|-------------|
| CAPTURED | Initial capture |
| HASHED | Content hashed |
| CANDIDATE_ONLY | Candidate, not promoted |
| NEEDS_REVIEW | Requires human review |
| FROZEN | Frozen (immutable) |
| REJECTED | Rejected |
| PROMOTION_READY | Ready for manual promotion |
| PROMOTED_MANUAL_ONLY | Promoted (only via manual review) |

## Forbidden Actions

| Action | Status |
|--------|--------|
| Auto-promote | BLOCKED |
| Write to memory | BLOCKED — memory_write_allowed=False |
| Decide | BLOCKED — KX108_ONLY |

## Tests

- `tests/periphery/test_memory_source_registry.py`

## Status

**READONLY** — Registers sources. Never promotes. Never decides.
