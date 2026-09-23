# Memory Candidate Ledger V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Append-only ledger for memory candidates.
**Module:** `periphery/memory/memory_candidate_ledger.py`
**Runtime:** APPEND-ONLY — no promotion, no mutation

## Role

The Memory Candidate Ledger stores memory candidates in an append-only structure. Candidates are captured with content hash, source type, and status — but the ledger never promotes, never mutates, and never decides.

## Inputs

- `MemoryCandidate` objects from `build_memory_candidate_v2()`

## Outputs

- Appends to `memory_candidates.jsonl` in append-only mode
- Returns confirmation with candidate_id

## Candidate Fields

| Field | Description |
|-------|-------------|
| candidate_id | Unique identifier |
| source_id | Source action/query |
| source_type | From MemorySourceType |
| content_hash | SHA-256 of content |
| content_summary | Brief summary |
| status | From MemoryCandidateStatus |
| memory_write_allowed | Always False |
| auto_promotion_allowed | Always False |
| risk_flags | Detected risks |

## Forbidden Actions

| Action | Status |
|--------|--------|
| Auto-promote candidate | BLOCKED — auto_promotion_allowed=False |
| Write to memory | BLOCKED — memory_write_allowed=False |
| Modify candidate after append | BLOCKED — append-only |
| Decide | BLOCKED — KX108_ONLY |

## Tests

- `tests/non_sovereignty/test_memory_candidate_ledger_no_promotion.py`
- `tests/non_sovereignty/test_memory_promotion_not_automatic.py`

## Status

**APPEND-ONLY** — Captures candidates. Never promotes. Never decides.
