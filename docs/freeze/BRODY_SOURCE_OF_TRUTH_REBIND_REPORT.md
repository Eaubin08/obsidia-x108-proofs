# Brody Source-of-Truth Rebind Report

**Date:** 2026-05-19
**Status:** BRODY_SOURCE_OF_TRUTH_REBIND_PASS

---

## What Changed

`/api/brody/chat` was wired to the real `brody_memory_readonly/` modules instead of the placeholder composer.

### Before
```
/api/brody/chat → brody_backend_response_composer.py (hardcoded templates)
```

### After
```
/api/brody/chat → brody_source_of_truth_adapter.py
  → brody_terminal_structural_dialogue_readonly_v1.run_once()
  → (fallback) brody_terminal build_response()
  → (fallback) brody_local_response_engine_readonly_v1.build_response()
  → (last resort) structured advisory response
```

## Real Modules Used

| Module | Function | Status |
|--------|----------|--------|
| `terminal_structural_dialogue_readonly_v1` | `run_once()`, `build_response()`, `extract_memory_query()`, `is_action_risk()` | REAL_BRODY_TERMINAL_STRUCTURAL_DIALOGUE |
| `local_response_engine_readonly_v1` | `build_response()` | REAL_BRODY_LOCAL_RESPONSE_ENGINE |
| `context_packet_query_readonly_v1` | `query_neo4j()` (ready, not called — Neo4j offline) | OFFLINE |
| `content_hydration_readonly_v1` | `hydrate_packet()` (ready, not called — no packet) | READY |

## Response Sources

| Source | When |
|--------|------|
| `REAL_BRODY_TERMINAL_STRUCTURAL_DIALOGUE` | `run_once()` succeeds |
| `REAL_BRODY_RUNTIME_NO_GRAPHITI` | Terminal `build_response()` fallback (Neo4j offline) |
| `REAL_BRODY_LOCAL_RESPONSE_ENGINE` | Local response engine fallback |
| `BACKEND_STUB_LAST_RESORT` | All modules fail |

## Placeholder Status

- "BRODY_READONLY_RESPONSE" → **GONE** as primary response
- "Projection unavailable" → **GONE** as primary response
- Responses are now structured French/English from real Brody modules

## Protected Files

All protected paths untouched.
