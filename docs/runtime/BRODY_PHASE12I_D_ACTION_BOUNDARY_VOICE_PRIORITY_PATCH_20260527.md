# BRODY_PHASE12I_D_ACTION_BOUNDARY_VOICE_PRIORITY_PATCH_20260527

Status: PASS_READY_FOR_REVIEW

## Scope

Micro-patch the remaining Phase 12I-C minor drift.

## Problem

ACT / mutation attack stayed safe, but voice_source was MEMORY_RESPONSE_CHAIN instead of ACTION_BOUNDARY.

## Patched

- apps/obsidia_api/brody_true_voice_adapter.py

## Change

Memory response chain can no longer overwrite the action boundary voice when request_type is ACTION_OR_ACT_REQUEST or MEMORY_WRITE_REQUEST.

## Preserved

- readonly=true
- emits_act=false
- memory_write=false
- graphiti_write=false
- kernel_mutation=false
- x108_mutation=false
- decision_authority=KX108_ONLY

## Validation

- BOM=false
- py_compile passed
- targeted pytest passed
- live check passed

## Decision

ACT / mutation requests now keep ACTION_BOUNDARY as the visible voice source.
