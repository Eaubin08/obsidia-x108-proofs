# M32_COMMON_COGNITIVE_PRIMITIVES_SPEC_V1

## 1. Context and Authority
This specification defines the M32 Common Cognitive Primitives.
References:
- COGNITIVE_FOUNDATION_V1_SEAL.md
- B7_COGNITIVE_ROLE_SPEC_V1.md
- B8_KNOWLEDGE_PROMOTION_SPEC_V1.md
- B9_PATH_SPEC_V1.md

## 2. Purity & Side Effects
Core primitives are side-effect free with respect to authority/state.
- PRIMITIVE_ACTION_AUTHORITY=NONE
- PRIMITIVE_MEMORY_WRITE=NO
- PRIMITIVE_KERNEL_MUTATION=NO
- PRIMITIVE_BINDER_MUTATION=NO
- PRIMITIVE_KX108_MUTATION=NO
- PRIMITIVE_B8_MUTATION=NO

A primitive may produce a typed result, but it cannot cause external execution.

## 3. Domain Independence
- COMMON_CORE_DOMAIN_INDEPENDENT=YES
- COMMON_CORE != DOMAIN_TRUTH

Operations like COMPARE are common. Domain-specific interpretations (e.g., physics vs. finance) belong to domain/type adapters.

## 4. Identity Model
- PRIMITIVE_TYPE_IDENTITY: The operation being invoked.
- PRIMITIVE_INVOCATION_IDENTITY: Type + canonical typed inputs + immutable config.
- PRIMITIVE_SEMANTIC_TRUTH_IDENTITY: NONE.
- SAME_INVOCATION_IDENTITY != SAME_TRUTH.

Wall-clock time and random UUIDs are excluded from semantic invocation identity.

## 5. Result Model
Taxonomy of primitive-local results:
- PRODUCED
- NOT_APPLICABLE
- INSUFFICIENT_INPUT
- UNKNOWN
- FAILED_RUNTIME

Invariants:
- UNKNOWN != FALSE
- NOT_APPLICABLE != FAILED
- FAILED_RUNTIME != SEMANTIC_FALSE

## 6. Determinism
DETERMINISTIC_CONTRACT vs. DETERMINISTIC_IMPLEMENTATION.
The contract defines deterministic canonical inputs, identity, output schema, and provenance. Later provider models may be non-deterministic internally provided provenance is explicit, output remains typed, and no authority is gained.

## 7. Composition and M33 ARM Boundary
- PRIMITIVE_OUTPUT_MAY_FEED_COMPATIBLE_PRIMITIVE_INPUT=YES
- B9_PATH_MAY_REFERENCE_PRIMITIVE_INVOCATIONS=YES
- M32_DOES_NOT_DEFINE_COMPLETE_ARM_GRAPH=YES

ARM schedulers, routing, and optimizations are deferred to M33+.

## 8. Input and Output Contract
- UNTYPED_ARBITRARY_MAPPING_AS_AUTHORITY=NO
- PRIMITIVE_OUTPUT != VERIFIED_TRUTH
- PRIMITIVE_OUTPUT != PROMOTED_KNOWLEDGE
- PRIMITIVE_OUTPUT != ACTION
- PRIMITIVE_OUTPUT != AUTHORIZATION

Inputs and outputs rely on existing canonical typed structures.

## 9. Historical Cognitive Ideas Classification
We avoid forcing historical heuristics into the V1 core:
- reverse: COMPOSITE_PATTERN
- friction: EXPERIMENTAL
- interstice: SUPERSEDED
- symmetry: M33_PLUS_CANDIDATE
- reciprocity: M33_PLUS_CANDIDATE
- micro↔macro: M33_PLUS_CANDIDATE
- 360 exploration: HEURISTIC
- divergence/convergence: COMPOSITE_PATTERN

## 10. Learning Boundary
- PRIMITIVE_INTERFACE=STABLE
- PRIMITIVE_IMPLEMENTATION=EVOLVABLE
- PRIMITIVE_CALIBRATION=EVOLVABLE

Primitives do not own persistent learning, weight updates, or durable cross-session memory.

## 11. Provenance
Minimal invocation provenance requires: primitive type, input refs, configuration/version, provider identity, and output type. It must not imply truth or authority.

## 12. Local Failure
- PRIMITIVE_FAILURE != PATH_FAILURE
- PRIMITIVE_FAILURE != B8_REJECTION
- PRIMITIVE_FAILURE != FALSE
- PRIMITIVE_FAILURE != ACTION_DENIAL

## 13. Future RED Contract
Explicit normative cases for future testing (Not yet implemented):
- M32-R1: same primitive type + same canonical inputs/config -> same invocation identity
- M32-R2: different primitive type -> different invocation identity
- M32-R3: different semantically relevant input -> different invocation identity
- M32-R4: wall-clock difference -> does not alter invocation identity
- M32-R5: primitive cannot ACT
- M32-R6: primitive cannot write durable memory
- M32-R7: primitive cannot mutate B8
- M32-R8: UNKNOWN does not become FALSE
- M32-R9: NOT_APPLICABLE distinct from FAILED_RUNTIME
- M32-R10: FAILED_RUNTIME does not mean semantic FALSE
- M32-R11: invalid/untyped input fails closed
- M32-R12: output retains required provenance
- M32-R13: compatible primitive composition works
- M32-R14: domain adapter cannot grant authority to core primitive
- M32-R15: B7 role semantics unchanged
- M32-R16: B9 path semantics unchanged
- M32-R17: foundation sentinel remains PASS
- M32-R18: different implementation/provider does not silently masquerade as identical provenance
- M32-R19: primitive output cannot self-label itself VERIFIED/PROMOTED
- M32-R20: primitive cannot silently consume UNKNOWN as FALSE
