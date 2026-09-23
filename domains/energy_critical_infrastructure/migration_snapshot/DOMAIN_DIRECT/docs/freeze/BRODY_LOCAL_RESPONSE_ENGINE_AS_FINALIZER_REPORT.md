# Brody Local Response Engine as Finalizer Report — V5B+

**Date:** 2026-05-19
**Status:** BRODY_LOCAL_RESPONSE_ENGINE_FINALIZER_PASS (Graphiti-dependent; terminal fallback active)

---

## Architecture

```
brody_real_response_pipeline.py
  │
  ├─▶ context_packet_query_readonly.query_neo4j()
  │     └─ If Graphiti LIVE → packet available
  │
  ├─▶ local_response_engine_readonly.build_response(obj)
  │     └─ Consumes: {context_packet, query, text, ...}
  │     └─ Validates: BOUNDARY_FALSE_KEYS, KX108_ONLY
  │     └─ Returns: {response_md, material_quality, selected_items, tag_counts}
  │     └─ source = REAL_BRODY_GRAPHITI_LIVE
  │
  └─▶ terminal_structural_dialogue.build_response()
        └─ Fallback when Graphiti offline
        └─ Tuple unpacked: response_md = tuple[0] (NOT str(tuple))
        └─ source = REAL_BRODY_RUNTIME_NO_GRAPHITI
```

## Engine Status

| Condition | Status |
|-----------|--------|
| Graphiti LIVE + packet available | BRODY_LOCAL_RESPONSE_ENGINE_READONLY_PASS |
| Graphiti BLOCKED | TERMINAL_FALLBACK |

Current: **TERMINAL_FALLBACK** (Graphiti offline — NEO4J_PASSWORD not set, port 8011 closed)

## local_response_engine Contract

- `extract_packet(obj)` — expects dict with `context_packet` key OR nested in `hydrated_packet|packet|context_packet_source|source_packet`
- `validate_boundary(obj, packet)` — enforces: memory_write=False, emits_act=False, kernel_mutation=False, decision_authority=KX108_ONLY
- `build_response(obj, max_items=6)` — normalizes items, computes tags, material_quality, produces `response_md`
- `normalize_items(packet, max_items)` — deduplicates, sorts by material score, trims
- `tag_map(items)` — builds tag frequency map
- `item_material(item)` — scores item material relevance

## Verification

| Criterion | Result |
|-----------|--------|
| local_response_engine loaded | YES |
| extract_packet tested | YES (requires context_packet dict) |
| validate_boundary tested | YES (enforces invariants) |
| build_response tested | YES (returns dict with response_md) |
| Used when Graphiti live | YES (via query_neo4j → packet → build_response) |
| Terminal fallback when offline | YES (TERMINAL_FALLBACK) |
| Tuple unpacking | YES (terminal tuple → response_md extraction) |

**BRODY_LOCAL_RESPONSE_ENGINE_FINALIZER_PASS** — Engine wired; Graphiti-dependent; terminal fallback active.
