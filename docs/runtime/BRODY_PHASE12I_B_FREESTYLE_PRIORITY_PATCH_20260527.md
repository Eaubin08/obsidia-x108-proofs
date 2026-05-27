# BRODY_PHASE12I_B_FREESTYLE_PRIORITY_PATCH_20260527

Status: PASS_READY_FOR_REVIEW

## Scope

Patch freestyle drifts found in Phase 12I-A.

## 12I-A problem

Security passed, but semantic priority drifted:

- code_debug was detected but answered too much as NEGATION_GUARD
- architecture question was reduced to X108/negation instead of explaining components
- "garde KX108_ONLY" triggered mutation_request
- bare kernel/x108 mention triggered mutation_request
- ACT/write/canon boundaries remained safe

## Patched

- apps/obsidia_api/brody_domain_raccord_adapter.py
- apps/obsidia_api/brody_true_voice_adapter.py

## Added

- CODE_DEBUG_GUIDANCE domain
- ARCHITECTURE_EXPLANATION domain
- real mutation request detector
- boundary-preserving instruction detector
- mutation_request no longer triggered by bare kernel/x108/KX108_ONLY mention
- useful freestyle intent priority over generic negation guard

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
- live priority check passed

## Decision

Brody remains safe while becoming more useful under freestyle pressure.
