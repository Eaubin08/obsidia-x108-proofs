# BRODY X108 ONLY BUILD MODE READONLY V1

## Purpose

Freeze the current build target.

For this phase, new Brody / memory / bridge readonly modules must be built directly inside:

obsidia-x108-proofs\periphery\brody_memory_readonly\

The obsidia-engine-candidate folder is not the active build target.

## Boundary

- BUILD_TARGET=obsidia-x108-proofs
- CANDIDATE_BUILD_TARGET=false
- X108_PROOF_NATIVE_BUILD=true
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
