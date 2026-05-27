# BRODY_PHASE12D_MEMORY_MATERIAL_BINDING_FREEZE_20260527

Status: FROZEN_PASS

## Scope

Freeze the validated Brody Memory Material Binding after Phase 12A-ter, 12B, and 12C.

## Problem found in 12A-ter

Phase 12A-ter proved:

- graphiti_rows_with_results=6
- brody_rows_no_material=12
- brody_rows_selected_zero=12
- material_gap=True

Meaning:

Graphiti V20 frozen HTTP had readonly material, but Brody memory_response_chain returned NO_MEMORY_RESULTS.

## Patch 12B

Patched:

- apps/obsidia_api/brody_memory_response_chain_adapter.py

Added behavior:

When Neo4j/BrodyMemoryDoc is live but query_neo4j returns zero results:

1. Try Graphiti V20 frozen HTTP context/search endpoints.
2. Normalize returned items into local_response_engine-compatible items.
3. Preserve readonly/KX108 boundaries.
4. Run local_response_engine if available.
5. Return selected_items and material_quality instead of NO_MEMORY_RESULTS.

## Validation 12B

- BOM=false
- py_compile passed
- targeted pytest passed: 6 passed
- live material check passed for:
  - Kernel
  - mémoire
  - 34 arbres

## Regression 12C

Validated cases:

- Kernel
- mémoire
- 34 arbres
- explique-moi ce que tu as maintenant comme mémoire, contrats, arbres et limites
- explique-moi comment OS Trad IR Reverse Graphiti mémoire contrats et 34 arbres aident Brody sans remplacer X108

All passed with:

- source=REAL_BRODY_GRAPHITI_LIVE
- graphiti_status=GRAPHITI_LIVE_READONLY_PASS
- chain_status != NO_MEMORY_RESULTS
- decision_authority=KX108_ONLY
- emits_act=false
- memory_write=false
- kernel_mutation=false

## Boundary frozen

Preserved:

- readonly=true
- memory_write=false
- graphiti_write=false
- neo4j_write=false
- emits_act=false
- emits_verdict=false
- kernel_mutation=false
- x108_mutation=false
- decision_authority=KX108_ONLY

## Decision

Brody Memory Material Binding is frozen as validated.

Current state:

Brody no longer only exposes native machination.

Brody can now receive actual readonly memory material from Graphiti V20 frozen HTTP when Neo4j/BrodyMemoryDoc returns zero direct results.

This does not change X108 authority.
