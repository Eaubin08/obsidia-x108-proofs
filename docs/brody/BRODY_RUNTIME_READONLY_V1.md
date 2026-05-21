# Brody Runtime Read-Only V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Read-only query responder. Provides advisory context. Never decides.
**Module:** `periphery/brody/brody_runtime_readonly.py`
**Runtime:** READONLY / ADVISORY_ONLY

## Role

Brody Runtime is the main query interface. It accepts natural language queries, processes them through the language router, and returns advisory responses. Every response is constrained by the Brody Response Contract.

## Inputs

- `query: str` — the user's query
- `language: str` — language code (en, fr, etc.)
- `context_refs: list[str]` — references to relevant context packets
- `confidence: float` — confidence threshold (default 0.8)

## Outputs

- `BrodyResponse` with fields:
  - `response_id: str`
  - `query_id: str`
  - `content: str` — advisory response text
  - `decision_authority: str` — always "KX108_ONLY"
  - `advisory_only: bool` — always True
  - `context_refs: list[str]`

## Forbidden Actions

| Action | Status |
|--------|--------|
| Emit ACT | BLOCKED — emits_act=False |
| Emit VERDICT | BLOCKED — emits_verdict=False |
| Write memory | BLOCKED — memory_write=False |
| Decide | BLOCKED — decision_authority=KX108_ONLY |

## Tests

- `tests/periphery/test_brody_runtime_readonly.py`
- `tests/non_sovereignty/test_brody_no_decision.py`

## Status

**READONLY** — Advisory responses only. X108 decides. Brody responds.
