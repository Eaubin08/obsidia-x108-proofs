# Brody Language Routing V1

**Status:** FIRST_CLASS_X108_MODULE
**Role:** Routes queries through language detection and response generation.
**Module:** `periphery/brody/brody_language_router.py`
**Runtime:** READONLY

## Role

The Brody Language Router detects the language of incoming queries and routes them to the appropriate response pipeline. It preserves language boundaries and ensures responses match the query language.

## Inputs

- `query: str` — user query
- `language_hint: str | None` — explicit language hint
- `context_lang: str | None` — language from context packet

## Outputs

- `LanguageRoute` with fields:
  - `detected_lang: str` — ISO language code
  - `confidence: float`
  - `route: str` — pipeline route
  - `readonly: bool` — always True
  - `can_emit_act: bool` — always False

## Forbidden Actions

| Action | Status |
|--------|--------|
| Emit ACT | BLOCKED |
| Emit verdict | BLOCKED |
| Write to memory | BLOCKED |
| Modify context packet | BLOCKED |

## Relation to Brody Response Contract

Every language-routed response must pass the Brody Response Contract validation. Language routing does not grant authority — it only routes context.

## Tests

- `tests/periphery/test_language_router_boundary_preserved.py`

## Status

**READONLY** — Routes context. Never decides. Never writes.
