# BRODY_PHASE12B_MEMORY_MATERIAL_BINDING_REPORT_20260527

Status: PASS_READY_FOR_REVIEW

## Scope

Patch Brody memory_response_chain so Graphiti V20 frozen HTTP material is used when Neo4j/BrodyMemoryDoc returns zero results.

## Problem

Phase 12A-ter proved:

- graphiti_rows_with_results=6
- brody_rows_no_material=12
- brody_rows_selected_zero=12
- material_gap=True

Meaning:

Graphiti had readonly material, but Brody memory_response_chain returned NO_MEMORY_RESULTS.

## Patched

- apps/obsidia_api/brody_memory_response_chain_adapter.py

## Added

When Neo4j is live but query_neo4j returns zero results:

1. Try Graphiti V20 frozen HTTP context/search endpoints.
2. Normalize returned items into local_response_engine-compatible items.
3. Preserve readonly/KX108 boundaries.
4. Run local_response_engine if available.
5. Return selected_items and material_quality instead of NO_MEMORY_RESULTS.

## Boundary

Preserved:

- readonly=true
- memory_write=false
- graphiti_write=false
- neo4j_write=false
- emits_act=false
- emits_verdict=false
- kernel_mutation=false
- decision_authority=KX108_ONLY

## Validations

- BOM=false
- py_compile passed
- targeted pytest passed
- live material check passed for Kernel / mémoire / 34 arbres

## Decision

Phase 12B repairs memory material binding without changing X108 authority.
