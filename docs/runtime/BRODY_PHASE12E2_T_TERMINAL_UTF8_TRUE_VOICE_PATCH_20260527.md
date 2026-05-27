# BRODY_PHASE12E2_T_TERMINAL_UTF8_TRUE_VOICE_PATCH_20260527

Status: PASS_READY_FOR_REVIEW

## Scope

Repair terminal Brody chat after Phase 12E1-R showed:

- API true voice is stable
- terminal --once crashes before rendering
- terminal does not expose true_voice / LLM obsidien regime metadata

## Root cause

Windows terminal output used cp1252 and crashed on Unicode box-drawing characters before rendering Brody output.

## Patched

- tools/brody_chat.py

## Added

- UTF-8/replacement console configuration
- ASCII-safe terminal headers
- true_voice_snapshot final_answer priority
- TRUE VOICE / LLM OBSIDIEN section
- voice_source / final_answer_source / source_mode visibility
- model_position visibility from true_response_structure_snapshot
- explicit structure-first / memory-enrichment / KX108_ONLY line

## Preserved

- /api/brody/chat remains primary endpoint
- readonly=true
- emits_act=false
- memory_write=false
- graphiti_write=false
- kernel_mutation=false
- decision_authority=KX108_ONLY

## Validation

- BOM=false
- py_compile passed
- terminal --once LLM obsidien passed
- terminal --once Mmonde / 34 arbres passed
- terminal --once ACT boundary passed
