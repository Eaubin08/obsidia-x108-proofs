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



## 14. Canonical Value Rules
Required for serialization:
- UTF-8
- JSON
- Object keys sorted lexicographically
- Compact separators
- No NaN
- No Infinity
- No implementation-specific object repr

Arrays preserve their declared order. Do not globally sort arbitrary arrays.
Named maps/bindings may be normalized by key where the contract explicitly declares unordered keyed semantics.

Freeze:
- `SERIALIZATION_ORDER != CAUSAL_ORDER`

## 15. PrimitiveInvocation
Define exact conceptual shape for `PrimitiveInvocation`:
- `schema_version`
- `primitive_type`
- `primitive_spec_version`
- `inputs`: canonical tuple of `PrimitiveInputBinding`
- `immutable_config`: canonical mapping
- `invocation_id`

`immutable_config` contains only configuration that may affect the primitive contract/result semantics. No wall-clock metadata belongs in semantic identity.

## 16. Invocation Identity Preimage
Freeze exact identity preimage:
```json
{
  "schema_version": "...",
  "primitive_type": "...",
  "primitive_spec_version": "...",
  "inputs": "canonical_input_bindings",
  "immutable_config": "canonical_config"
}
```

Invocation identity:
`SHA256(UTF8(CANONICAL_JSON(identity_preimage)))`

Freeze:
- `RANDOM_UUID_IN_INVOCATION_IDENTITY=NO`
- `WALL_CLOCK_IN_INVOCATION_IDENTITY=NO`
- `TIMESTAMP_IN_INVOCATION_IDENTITY=NO`

Same canonical preimage -> same `invocation_id`.
Different semantically relevant preimage -> different `invocation_id`.

## 17. Provider / Implementation Identity
Do NOT automatically include provider/runtime instance identity in `invocation_id`. Provider/implementation belongs in provenance.
If a future primitive contract declares an implementation choice semantically relevant, it must enter `immutable_config` explicitly.

Thus, same invocation identity may have different execution provenance, but provenance may never be silently discarded.

Freeze:
- `INVOCATION_IDENTITY != EXECUTION_PROVENANCE`

## 18. Input Validation
Before primitive execution, substrate validation must check:
- primitive type exists
- spec version matches
- required slots present
- unknown slots forbidden unless type spec explicitly allows them
- no duplicate slots
- datum type compatible with slot contract
- payload canonicalizable
- immutable config canonicalizable

Invalid invocation:
`FAIL_CLOSED`. No execution. No authority.

## 19. PrimitiveProvenance
Define exact conceptual shape for `PrimitiveProvenance`:
- `primitive_type`
- `primitive_spec_version`
- `implementation_id`
- `implementation_version`
- `provider_id`: optional
- `input_refs` / `source_refs`
- `invocation_id`

No timestamp is required for semantic identity. Operational timestamps may exist outside the identity contract if later needed.

Provenance:
- `!= truth`
- `!= verification`
- `!= authority`

## 20. PrimitiveResult
Define exact conceptual shape for `PrimitiveResult`:
- `invocation_id`
- `primitive_type`
- `status`
- `outputs`: tuple[TypedCognitiveDatum, ...]
- `provenance`
- `reason`: optional bounded reason identifier

`PrimitiveResult` is immutable after creation.

## 21. Result Enum
Freeze exact V1 status set:
- `PRODUCED`: primitive produced structurally valid output. It does NOT mean TRUE.
- `NOT_APPLICABLE`: input is valid but operation does not apply to this typed case.
- `INSUFFICIENT_INPUT`: required semantic information is absent/incomplete.
- `UNKNOWN`: operation completes without sufficient basis for a determinate cognitive result.
- `FAILED_RUNTIME`: execution mechanism failed.

Freeze:
- `PRODUCED != TRUE`
- `UNKNOWN != FALSE`
- `NOT_APPLICABLE != FAILED_RUNTIME`
- `INSUFFICIENT_INPUT != UNKNOWN`
- `FAILED_RUNTIME != FALSE`

## 22. Output Rules
For `PRODUCED`:
- outputs may be non-empty according to primitive type contract.

For other statuses (`NOT_APPLICABLE`, `INSUFFICIENT_INPUT`, `UNKNOWN`, `FAILED_RUNTIME`):
- no authoritative output payload.

If diagnostic structured data is allowed, distinguish it from cognitive outputs explicitly. Do not allow failure payloads to masquerade as produced claims.

## 23. Composition Compatibility
Define structural composition only.
Primitive A output may feed Primitive B input iff:
- A output `type_id` is structurally compatible with B declared input-slot type.

No implicit coercion. No arbitrary dict conversion. Domain adapters may perform explicit typed translation.

Freeze:
- `COMPOSITION_COMPATIBILITY != TRUTH_COMPATIBILITY`
- `COMPOSITION_COMPATIBILITY != AUTHORIZATION`

## 24. Domain Adapter
Domain adapters may:
- translate domain material into `TypedCognitiveDatum`
- validate domain-specific type compatibility
- translate primitive outputs back into domain representations

They may NOT grant the common primitive:
- action authority
- knowledge promotion authority
- memory authority
- truth status

Freeze:
- `DOMAIN_ADAPTER_CANNOT_ESCALATE_AUTHORITY=YES`

## 25. Pure Execution Contract
Define invocation execution contract conceptually:
`PrimitiveTypeSpec` + validated `PrimitiveInvocation` -> `PrimitiveResult`

The M32 core itself has:
- `memory_write=False`
- `emits_act=False`
- `kernel_mutation=False`
- `binder_mutation=False`
- `kx108_mutation=False`
- `b8_mutation=False`

No external effects.

## 26. Registration / Type Resolution
The substrate must be implementable with zero canonical primitives.
Define a structural primitive registry contract conceptually:
`primitive_type` + `spec_version` -> `PrimitiveTypeSpec`

Registration itself grants no authority.
Duplicate exact registrations: idempotent or rejected deterministically.
Conflicting registrations for same `primitive_type` + `spec_version` must fail closed.
Do NOT implement dynamic plugin loading.

## 27. Versioning
Freeze:
- `PrimitiveTypeSpec` semantic contract changes require a new `spec_version`.
- A changed semantic contract must not silently reuse the old version.
- Invocation identity commits to `primitive_spec_version`.
- Implementation bugfixes that preserve semantic contract may change `implementation_version`/`provenance` without changing `primitive_spec_version`.

## 28. Immutability
Require immutable/copy-safe conceptual objects for:
- `PrimitiveTypeSpec`
- `PrimitiveInvocation`
- `PrimitiveResult`
- `PrimitiveProvenance`

Canonical input/config payload must not change underneath an already-computed `invocation_id`.
No mutable alias may invalidate identity after construction.

## 29. Exact Implementation Questions

- **What object defines a primitive type?** `PrimitiveTypeSpec`
- **What object carries a typed datum?** `TypedCognitiveDatum`
- **What object represents an invocation?** `PrimitiveInvocation`
- **What object represents result?** `PrimitiveResult`
- **What object represents provenance?** `PrimitiveProvenance`
- **How are input slots represented?** `PrimitiveInputBinding`
- **How are inputs canonicalized?** Through `CANONICAL_JSON` serialization rules (UTF-8, sorted keys, compact separators, no NaN/Infinity).
- **How is invocation_id computed?** `SHA256(UTF8(CANONICAL_JSON(identity_preimage)))`
- **How are config values canonicalized?** Through the same `CANONICAL_JSON` rules.
- **How is a primitive type resolved?** Via the structural primitive registry mapping `primitive_type` + `spec_version` -> `PrimitiveTypeSpec`.
- **How are incompatible inputs rejected?** By substrate input validation yielding `FAIL_CLOSED`.
- **How is composition compatibility checked?** By verifying the output `type_id` is structurally compatible with the declared input-slot type (no implicit coercion).
- **Which statuses exist?** `PRODUCED`, `NOT_APPLICABLE`, `INSUFFICIENT_INPUT`, `UNKNOWN`, `FAILED_RUNTIME`.
- **Which outputs are legal for each status?** Non-empty outputs are legal only for `PRODUCED`. Other statuses yield no authoritative output payload.
- **Where does provider identity live?** In `PrimitiveProvenance.provider_id`.
- **What fields participate in semantic invocation identity?** `schema_version`, `primitive_type`, `primitive_spec_version`, `inputs` (canonical bindings), and `immutable_config`.

## 30. Synthetic RED Fixture Policy
Because `CORE_PRIMITIVE_COUNT=0`, future RED tests may define local synthetic primitive specs such as `test.echo` or `test.compare_stub` ONLY inside test scope.

Freeze:
- `SYNTHETIC_TEST_PRIMITIVE_IS_CANONICAL=NO`

## 31. MAP R1-R20 TO IMPLEMENTATION CONTRACT
Explicit normative mapping to runtime objects, fields/invariants, and expected behavior:

- **R1** -> `PrimitiveInvocation.invocation_id`: Same canonical preimage (type + inputs + config) yields exactly the same hash.
- **R2** -> `PrimitiveInvocation.primitive_type`: Different primitive types yield different preimages and thus different invocation identities.
- **R3** -> `PrimitiveInvocation.inputs` / `immutable_config`: Different semantically relevant inputs alter the preimage, yielding a different hash.
- **R4** -> `PrimitiveInvocation.invocation_id`: Wall-clock time is strictly excluded from the identity preimage, leaving the hash unchanged.
- **R5** -> Pure Execution Contract: `emits_act=False` invariant ensures a primitive cannot ACT.
- **R6** -> Pure Execution Contract: `memory_write=False` invariant ensures a primitive cannot write durable memory.
- **R7** -> Pure Execution Contract: `b8_mutation=False` invariant ensures a primitive cannot mutate B8.
- **R8** -> `PrimitiveResult.status`: The enum invariant `UNKNOWN != FALSE` prevents treating indeterminate results as semantically false.
- **R9** -> `PrimitiveResult.status`: The enum invariant `NOT_APPLICABLE != FAILED_RUNTIME` maintains distinct statuses.
- **R10** -> `PrimitiveResult.status`: The enum invariant `FAILED_RUNTIME != FALSE` prevents conflating runtime errors with logical falsehood.
- **R11** -> Input Validation: Invalid or untyped inputs trigger a `FAIL_CLOSED` mechanism, halting execution safely.
- **R12** -> `PrimitiveResult.provenance`: The result object must structurally retain a complete `PrimitiveProvenance` instance.
- **R13** -> Composition Compatibility: The substrate validates that a provider's output `type_id` matches the recipient's input-slot type exactly.
- **R14** -> Domain Adapter Rules: `DOMAIN_ADAPTER_CANNOT_ESCALATE_AUTHORITY=YES` invariant blocks adapters from granting authority to core primitives.
- **R15** -> Pure Execution Contract: `kernel_mutation=False` enforces that B7 role semantics remain completely unaltered.
- **R16** -> Pure Execution Contract: `binder_mutation=False` enforces that B9 path semantics remain completely unaltered.
- **R17** -> Sentinel Checking: All primitive execution environments must allow `foundation_sentinel.py` to remain in a `PASS` state.
- **R18** -> `PrimitiveProvenance`: Distinct `implementation_id` and `provider_id` entries ensure different providers cannot masquerade as identical provenance.
- **R19** -> Output Rules: `PRIMITIVE_OUTPUT != VERIFIED_TRUTH / PROMOTED_KNOWLEDGE` prevents primitives from self-certifying.
- **R20** -> Result Enum Invariants: Output rules explicitly forbid the silent consumption or translation of an `UNKNOWN` output into a `FALSE` value.
