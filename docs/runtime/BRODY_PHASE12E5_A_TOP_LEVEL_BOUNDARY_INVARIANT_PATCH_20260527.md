# BRODY_PHASE12E5_A_TOP_LEVEL_BOUNDARY_INVARIANT_PATCH_20260527

Status: PASS_READY_FOR_REVIEW

## Scope

Patch top-level /api/brody/chat boundary invariant fields after Phase 12E5 regression.

## Problem

Phase 12E5 showed:

- semantic_bad_rows=0
- legacy_neo4j_drift_rows=0
- negation_false_positive_rows=0
- forbidden_drift_rows=0
- write_boundary_failed_rows=0
- domain_failed_rows=0
- memory_failed_rows=0

But:

- hard_bad_rows=16

Root cause:

All rows had x108_mutation=null at the top-level response.

## Patched

- apps/obsidia_api/routes/brody.py

## Added top-level invariants

- readonly=true
- advisory_only=true
- context_signal_only=true
- allowed_to_decide=false
- allowed_to_act=false
- emits_act=false
- emits_verdict=false
- response_only=true
- memory_write=false
- graphiti_write=false
- neo4j_write=false
- kernel_mutation=false
- x108_mutation=false
- decision_authority=KX108_ONLY

## Preserved

No behavior change to X108, Graphiti, memory, kernel, or Brody voice.

This is envelope consistency only.

## Validation

- BOM=false
- py_compile passed
- targeted pytest passed
- live boundary invariant check passed
