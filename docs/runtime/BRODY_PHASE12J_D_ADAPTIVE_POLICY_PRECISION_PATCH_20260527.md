# BRODY_PHASE12J_D_ADAPTIVE_POLICY_PRECISION_PATCH_20260527

Status: PASS_READY_FOR_REVIEW

## Scope

Patch adaptive response policy precision after 12J-C terminal stress failed.

## 12J-C failed rows

- short_boundary classified as SHORT/NONE instead of BOUNDARY_COMPACT/BOUNDARY
- architecture_deep classified as SUBJECT instead of ARCHITECTURE
- nonsense_compact classified as MEMORY instead of SHORT/NONE
- explicit_deep classified as SHORT/NONE instead of DEEP/SUBJECT

## Patched

- apps/obsidia_api/brody_adaptive_response_policy.py

## Changes

- decision-boundary questions are treated as BOUNDARY_COMPACT
- architecture context takes priority over generic explicit DEEP
- nonsense anchors remain SHORT/NONE even if memory exists
- “complète / réponse complète” is recognized as DEEP explicit hint

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
- live precision check passed

## Decision

Adaptive response policy now better separates subject depth, architecture depth, boundary compactness, and nonsense compactness.
