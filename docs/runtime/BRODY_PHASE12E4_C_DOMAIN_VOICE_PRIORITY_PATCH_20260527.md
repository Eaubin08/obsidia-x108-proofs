# BRODY_PHASE12E4_C_DOMAIN_VOICE_PRIORITY_PATCH_20260527

Status: PASS_READY_FOR_REVIEW

## Scope

Fix Brody true voice priority after 12E4-B connected domain raccords but memory_response_chain still overwrote domain answers.

## Problem

12E4-C audit proved:

- domain_raccord_snapshot.structural_answer_available=true
- domain_raccord_snapshot.structural_answer_len>0
- domain_voice_mode=DOMAIN_RACCORD_*
- but final_answer_source=MEMORY_RESPONSE_CHAIN
- final answer started with generic X108 / memory response instead of domain response

## Patched

- apps/obsidia_api/brody_true_voice_adapter.py
- tools/brody_chat.py

## Added

- domain_raccord has voice priority
- memory_response_chain becomes enrichment when domain_raccord is available
- write boundary keeps highest safety priority
- terminal displays DOMAIN RACCORD / STRUCTURE-FIRST section

## Preserved

- readonly=true
- memory_write=false
- graphiti_write=false
- neo4j_write=false
- emits_act=false
- emits_verdict=false
- kernel_mutation=false
- x108_mutation=false
- decision_authority=KX108_ONLY

## Validation

- BOM=false
- py_compile passed
- targeted pytest passed
- live domain priority check passed
- terminal domain section visible

## Decision

Brody now speaks domain-first when an Obsidia domain raccord is detected.

Memory enriches. It does not override structure.
