# MEMORY LAYER AUTHORITY MODEL READONLY V1

## Purpose

Close the memory-layer boundary for Brody / LLM Obsidien inside X108 proof.

This model separates:

- USER_MEMORY
- SESSION_MEMORY
- RUNTIME_MEMORY
- GRAPHITI_MEMORY
- CONFIRMED_MEMORY

## Current review source

- review_pointer: C:\Users\User\Desktop\obsidia-engine-proof-core\CURRENT_MEMORY_LAYER_REVIEW_USER_SESSION_RUNTIME_GRAPHITI.txt
- review_status: MEMORY_LAYER_REVIEW_USER_SESSION_RUNTIME_GRAPHITI_WARN
- total_records: 50093

## Layer presence

- USER_MEMORY_PRESENT=True
- SESSION_MEMORY_PRESENT=True
- RUNTIME_MEMORY_PRESENT=True
- GRAPHITI_MEMORY_PRESENT=True
- CONFIRMED_MEMORY_PRESENT=False
- CONFIRMED_MEMORY_VIA_PROOF_POINTERS=True

## Confirmed-memory interpretation

CONFIRMED_MEMORY_PRESENT=False in the raw review is a classifier weakness, not a runtime absence.

Confirmed memory is currently represented by validated proof pointers:

- HAS_X108_PROOF_POINTERS=True
- HAS_BRODY_RUNTIME_PROOF=True
- HAS_NATIVE_TERMINAL_PROOF=True
- HAS_DETECTOR_PATCH_PROOF=True

Therefore:

CONFIRMED_MEMORY_EFFECTIVE=true

## Authority model

- USER_MEMORY: user-scoped context only
- SESSION_MEMORY: session reopen / transcript / handoff context only
- RUNTIME_MEMORY: Brody runtime context only
- GRAPHITI_MEMORY: readonly context graph / manual apply memory-only
- CONFIRMED_MEMORY: validated/frozen/proof-pointed records only

## Final authority

- Memory authority: false
- Brody decision authority: false
- Graphiti decision authority: false
- Final decision authority: KX108_ONLY
- Human validation required for memory promotion/apply

## Boundary

- MEMORY_DECISION=false
- ALLOWED_TO_DECIDE=false
- EMITS_ACT=false
- EMITS_VERDICT=false
- DECISION_AUTHORITY=KX108_ONLY
- KERNEL_MUTATION=false
- X108_RUNTIME_BINDING=false
- X108_MERGE=false
- GRAPHITI_INDEX_WRITE=false
- NEO4J_WRITE_EXECUTED=false
- MEMORY_INTAKE=false
- UI=false
