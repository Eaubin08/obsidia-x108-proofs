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



## 14. Frozen M32 V1 Model and Foundation Values
Sections 14 onward are NORMATIVE for M32 V1 implementation. Sections 1–13 are retained as historical rationale and are not altered. If any statement in §§1–13 conflicts with a normative clause in §14 or later, the later normative clause controls implementation behavior and tests.

- `M32_V1_MODEL=SUBSTRATE_ONLY`
- `CORE_PRIMITIVE_COUNT=0`
- `ZERO_CORE_PRIMITIVES_ACCEPTABLE=YES`
- `PRIMITIVE_GRANULARITY=ATOMIC_REUSABLE_UNITS`
- `DOMAIN_INDEPENDENT_CORE=YES`
- `DOMAIN_SPECIALIZATION=TYPE_ADAPTER`
- `M32_IS_B10=NO`
- `M32_REDEFINES_B7=NO`, `M32_REDEFINES_B8=NO`, `M32_REDEFINES_B9=NO`
- `M32_DEFINES_COMPLETE_ARM_GRAPH=NO`
- `MEMORY_WRITE=False`, `EMITS_ACT=False`, `KERNEL_MUTATION=False`
- `DECISION_AUTHORITY=KX108_ONLY`
- `DATA_EXISTS != TRUE`, `DATA_EXISTS != VERIFIED`, `DATA_EXISTS != AUTHORIZED`
- `EFFECT_DECLARATION != AUTHORITY`

Sealed foundation laws are preserved unchanged: ONE OBJECT, MANY PROJECTIONS, MANY RELATIONS, MANY PATHS, NO AUTOMATIC FUSION; `CONTENT != SCOPE != COMMITMENT != OCCURRENCE != EPISTEMIC != EVIDENCE != VERIFICATION != AUTHORITY`; `UNKNOWN != FALSE`; `MEMORY != TRUTH`; `CONFIDENCE != AUTHORITY`; `COMPETENCE != AUTHORITY`; `COGNITION != AUTHORITY`; ONE FINAL ACTION AUTHORITY=`KX108_ONLY`.

M32 V1 does NOT: define truth; define B8 promotion or knowledge promotion; write durable memory; define a World Model; select, authorize or execute actions; replace B7 roles, B8 promotion or B9 cognitive paths; implement ARM, Bio or COMOS; perform calibration; self-modify.

Implementation location (used by oracles in §35–§36): M32 runtime code, when written, lives under `app/cognition/m32/`. Contract tests live under `tests/m32/`.

## 15. Canonical Value and Canonical JSON
`CanonicalValue` is exactly one of: `null`, `true`/`false`, a string, a finite JSON number, an array of `CanonicalValue`, or an object with string keys and `CanonicalValue` values (`CanonicalObject`).

The following MUST NOT appear inside a `CanonicalValue`: `set`, `frozenset`, any map type whose iteration order is not semantically fixed, bytes, enum objects, paths, dataclasses, or objects relying on a custom `repr`. Producers (normally domain adapters) MUST convert unordered collections, before `TypedCognitiveDatum` construction, into either an array whose semantic order is explicitly defined by the producer, or a `CanonicalObject`. A datum value violating these rules causes `NON_CANONICAL_VALUE` at datum construction; an `immutable_config` violating them causes `INVALID_IMMUTABLE_CONFIG` (§33). Tuples serialize as arrays.

Canonical JSON (`CANONICAL_JSON`) MUST be produced as follows:
1. Every string (values and object keys) is normalized to Unicode NFC.
2. Object keys are sorted ascending by Unicode code point of the NFC-normalized key. Two keys equal after NFC normalization: `NON_CANONICAL_VALUE`.
3. Separators are exactly `,` and `:`; no insignificant whitespace.
4. Non-ASCII characters are emitted literally (`ensure_ascii=false`); string escaping follows RFC 8785.
5. Arrays preserve their declared order, except `PrimitiveInvocation.inputs`, which MUST be sorted by `slot_name` (§18) before serialization.
6. Numbers follow RFC 8785 (JSON Canonicalization Scheme) number serialization: integers in minimal decimal form; finite floats in the shortest round-trip form RFC 8785 prescribes; `-0` serializes as `0`.
7. `NaN`, `+Infinity` and `-Infinity` are forbidden: `NON_CANONICAL_VALUE`.
8. Integers with |n| > 2^53 − 1 are forbidden: `NON_CANONICAL_VALUE`.
9. The resulting text is encoded as UTF-8 bytes without BOM.

The `NON_CANONICAL_VALUE` codes in this list apply to datum values (Phase B); the same violations inside `immutable_config` raise `INVALID_IMMUTABLE_CONFIG` (§33).

No implementation-specific `repr()` output may enter canonical JSON. If an implementation cannot produce the required canonical form, it MUST fail closed before identity calculation.

Freeze: `SERIALIZATION_ORDER != CAUSAL_ORDER`.

## 16. TypedCognitiveDatum
Immutable. Exact fields:

| field | type | required |
|---|---|---|
| `schema_version` | non-empty str | yes |
| `datum_type` | non-empty str | yes |
| `value` | `CanonicalValue` | yes |
| `semantic_refs` | tuple[str, ...] | no (absent ≠ empty) |

Canonical serialization: a `CanonicalObject` with exactly the present keys among `datum_type`, `schema_version`, `semantic_refs`, `value`. `semantic_refs`, when present, keeps declared order and is part of the datum's semantic representation (and thus of invocation identity). An absent `semantic_refs` is omitted, not serialized as `[]`.

A datum carries no provider/runtime provenance, no truth status, no verification status and no authority. Freeze: `DATUM_EXISTS != TRUE`, `DATUM_EXISTS != VERIFIED`, `DATUM_EXISTS != AUTHORIZED`.

## 17. PrimitiveTypeSpec and its Parts
Immutable. Exact fields:

| field | type |
|---|---|
| `schema_version` | str, exactly `"m32.primitive_type_spec.v1"` |
| `primitive_type` | non-empty str, explicit and stable |
| `spec_version` | non-empty str |
| `input_slots` | tuple[InputSlotSpec, ...], sorted ascending by `slot_name`, names unique |
| `output_type` | DatumTypeRef |
| `immutable_config_schema` | ConfigSchema |
| `composition_contract` | CompositionContract |
| `domain_adapter_policy` | DomainAdapterPolicy |
| `effects_contract` | EffectsContract |

- `InputSlotSpec`: `slot_name: str` (non-empty), `datum_type: str`, `datum_schema_version: str`, `required: bool`.
- `DatumTypeRef`: `datum_type: str`, `datum_schema_version: str`.
- `ConfigSchema`: `fields: tuple[ConfigFieldSpec, ...]`, sorted by `name`, names unique. `ConfigFieldSpec`: `name: str`, `value_kind` ∈ {`null`, `boolean`, `string`, `number`, `array`, `object`}, `required: bool`. Undeclared config keys, missing required keys or wrong kinds → `INVALID_IMMUTABLE_CONFIG`. An empty schema admits only `{}`.
- `CompositionContract`: `direct_composition_rule`, whose only V1 value is `"EXACT_TYPE_AND_SCHEMA_MATCH"` (§26).
- `DomainAdapterPolicy`: `admitted_adapter_ids: tuple[str, ...]` (sorted, may be empty). Admission never alters primitive semantics.
- `EffectsContract`: exactly `memory_write`, `emits_act`, `b8_mutation`, `binder_mutation`, `kernel_mutation`, `kx108_mutation`, all `false` for M32 V1. Any `true` makes the spec unregistrable (`INVALID_TYPE_SPEC`). These are testable substrate declarations, not authorization: `EFFECT_DECLARATION != AUTHORITY`.

Primitive semantics are determined only by (`primitive_type`, `spec_version`) and this spec; they are never inferred from a class name, free text or provider. A `PrimitiveTypeSpec` does not imply truth, authority, memory promotion or action permission.

## 18. PrimitiveInputBinding and PrimitiveInvocation
`PrimitiveInputBinding` (immutable): `slot_name: str`, `datum: TypedCognitiveDatum`. Serialized as `{"datum": <datum>, "slot_name": <name>}`.

`PrimitiveInvocation` (immutable after construction):

| field | type |
|---|---|
| `schema_version` | str, exactly `"m32.invocation.v1"` |
| `primitive_type` | str |
| `primitive_spec_version` | str, always explicit |
| `inputs` | tuple[PrimitiveInputBinding, ...], sorted ascending by `slot_name` (code point, after NFC) |
| `immutable_config` | `CanonicalObject` |
| `invocation_id` | str, derived (§19), never supplied by the caller |

`inputs` serialize as an ARRAY of bindings in sorted order. `slot_name` is authoritative for binding identity; no positional interpretation exists. Freeze: `INPUT_POSITION != INPUT_SEMANTICS`.

Copy safety: at construction, every caller-supplied container is deep-copied into canonical immutable equivalents. Later mutation of the caller's original list/dict MUST NOT change `inputs`, `immutable_config`, the canonical representation or `invocation_id`.

## 19. Invocation Identity
Identity preimage (exact keys, no others):
```json
{
  "immutable_config": {},
  "inputs": [],
  "primitive_spec_version": "<str>",
  "primitive_type": "<str>",
  "schema_version": "m32.invocation.v1"
}
```
(`immutable_config` holds the canonical config object, `inputs` the sorted binding array.)

`invocation_id = lowercase_hex(SHA256(UTF8(CANONICAL_JSON(preimage))))`: exactly 64 lowercase hexadecimal characters, no prefix.

Excluded from identity unless a primitive's `ConfigSchema` explicitly places them in `immutable_config`: random UUIDs, wall-clock timestamps, PIDs, memory addresses, host paths, machine identity, provider/model identity, provider latency, ephemeral request IDs, process-local ordering.

Freeze: `INVOCATION_IDENTITY != EXECUTION_PROVENANCE`; `SAME_INVOCATION_IDENTITY != SAME_TRUTH`.

## 20. Validation Order
Validation runs in exactly this order; the first failing step determines the outcome. Steps 1–13 constitute Phases E–G of §32; no step before 12 reads or relies on `invocation_id`.

1. Syntax: `primitive_type` not a non-empty string → `UNKNOWN_PRIMITIVE_TYPE`; `primitive_spec_version` not a non-empty string → `UNKNOWN_PRIMITIVE_VERSION`.
2. Resolve the registry key (`primitive_type`, `primitive_spec_version`) by exact string equality: unknown type → `UNKNOWN_PRIMITIVE_TYPE`; known type with unregistered version → `UNKNOWN_PRIMITIVE_VERSION`. No ranges, no "latest".
3. Validate invocation `schema_version == "m32.invocation.v1"`, else `INVALID_SCHEMA_VERSION`.
4. Supplied bindings are structurally valid by construction (Phases B–D guarantee each element is a constructed `PrimitiveInputBinding` holding a constructed `TypedCognitiveDatum`). This step raises no code.
5. Detect duplicate `slot_name` → `DUPLICATE_INPUT_SLOT`.
6. Reject slots not declared in `input_slots` → `UNKNOWN_INPUT_SLOT`.
7. For each supplied slot, in ascending `slot_name` order: `datum_type` mismatch → `DATUM_TYPE_MISMATCH`; then datum `schema_version` ≠ slot `datum_schema_version` → `DATUM_SCHEMA_MISMATCH`.
8. Validate `immutable_config` against `ConfigSchema`, else `INVALID_IMMUTABLE_CONFIG`.
9. Validate `immutable_config` values are canonical values (§15), else `INVALID_IMMUTABLE_CONFIG`. (Datum values were already proven canonical at Phase B.)
10. Determine missing required slots (not an error).
11. Canonicalize the validated invocation (Phase F).
12. Compute `invocation_id` (Phase G, §19).
13. Freeze the `FinalizedPrimitiveInvocation`.
14. If any required slot is missing: produce `PrimitiveResult(status=INSUFFICIENT_INPUT, output=null)` without calling the implementation (Phase H).
15. Otherwise the selected implementation executes (Phase I).
16. Validate and freeze the `PrimitiveResult` (Phase J).

No implementation code executes before step 13 succeeds. A failure in steps 1–9 raises `InvocationValidationError`; no `FinalizedPrimitiveInvocation`, no `invocation_id` and no `PrimitiveResult` are produced.

## 21. Two Outcomes: Invalid vs. Incomplete
A. INVALID MATERIAL → `InvocationValidationError` (immutable): `code: str`, `message: str`, `field_path: str | absent`. The closed V1 code set and the single lifecycle phase at which each code may be raised are fixed in §33. `message` and `field_path` are non-normative for equality; tests assert `code` only.

B. VALID BUT INCOMPLETE INVOCATION: a finalized invocation lacking a declared required slot → `PrimitiveResult.status=INSUFFICIENT_INPUT`, `output=null`, implementation not called, `invocation_id` = the finalized invocation's id (computed over the supplied bindings).

Freeze:
- `MISSING_REQUIRED_SLOT != MALFORMED_INVOCATION`
- `MISSING_REQUIRED_SLOT → INSUFFICIENT_INPUT`
- `DUPLICATE_SLOT → InvocationValidationError(DUPLICATE_INPUT_SLOT)`
- `WRONG_TYPE → InvocationValidationError(DATUM_TYPE_MISMATCH)`
- `UNKNOWN_EXTRA_SLOT → InvocationValidationError(UNKNOWN_INPUT_SLOT)`
- `VALIDATION_ERROR != SEMANTIC_FALSE`

## 22. PrimitiveProvenance
Immutable. Exact fields:

| field | type | required |
|---|---|---|
| `implementation_id` | non-empty str | yes |
| `implementation_version` | str | no |
| `provider_id` | str | no |
| `model_id` | str | no |
| `execution_environment_ref` | str | no |
| `source_refs` | tuple[str, ...] | yes (may be empty) |
| `derived_from_invocation_ids` | tuple[str, ...] of 64-hex ids | yes (may be empty) |

Provenance records execution lineage only. It does not imply truth, verification, knowledge promotion or authorization, and never participates in `invocation_id`. If a provider/model choice affects semantics by contract, it MUST be declared in `ConfigSchema` and supplied in `immutable_config`. Provenance is never silently dropped or replaced: executions by different `implementation_id`/`provider_id`/`model_id` MUST yield provenance records that differ in those fields.

## 23. PrimitiveResult
Immutable. Exact fields (no others):

| field | type |
|---|---|
| `schema_version` | str, exactly `"m32.result.v1"` |
| `invocation_id` | 64-hex str |
| `status` | PrimitiveResultStatus |
| `output` | TypedCognitiveDatum or null |
| `provenance` | PrimitiveProvenance |
| `diagnostics` | tuple[str, ...] (may be empty; never a cognitive output) |

`PrimitiveResultStatus` is exactly: `PRODUCED`, `NOT_APPLICABLE`, `INSUFFICIENT_INPUT`, `UNKNOWN`, `FAILED_RUNTIME`. No other member. Implementations MUST NOT define truthiness or any FALSE mapping for statuses.

Output rules (constructing a result that violates them, carries an extra field or an unknown status fails with `INVALID_RESULT`):
- `PRODUCED`: `output` MUST be non-null and its (`datum_type`, `schema_version`) MUST equal the spec `output_type`.
- `NOT_APPLICABLE`, `INSUFFICIENT_INPUT`, `UNKNOWN`, `FAILED_RUNTIME`: `output` MUST be null.

Semantics:
- `PRODUCED`: structurally valid output exists.
- `NOT_APPLICABLE`: valid input, operation does not apply.
- `INSUFFICIENT_INPUT`: required slot absent (§21-B), or the implementation reports required semantic information missing.
- `UNKNOWN`: completed without basis for a determinate result.
- `FAILED_RUNTIME`: execution mechanism failed; an exception raised by the implementation is captured as `FAILED_RUNTIME`.

Freeze: `PRODUCED != TRUE`; `UNKNOWN != FALSE`; `FAILED_RUNTIME != FALSE`; `NOT_APPLICABLE != FAILED_RUNTIME`; `INSUFFICIENT_INPUT != UNKNOWN`; `PRIMITIVE_OUTPUT != VERIFIED_TRUTH`; `PRIMITIVE_OUTPUT != PROMOTED_KNOWLEDGE`.

Diagnostics: `diagnostics` is non-semantic metadata. It never participates in `invocation_id`, never changes the meaning of `status`, preserves production order, and MUST NOT be parsed to determine truth, verification or authority. Its content is normative only where §34 fixes it (FAILED_RUNTIME exception class name).

Boolean status: `PrimitiveResultStatus` has no normative boolean coercion. `bool(status)` MUST NOT be used as semantic truth; if the implementation language exposes truthiness, it has no contract meaning. Consumers MUST branch on explicit enum values.

The substrate exposes no field through which a result becomes VERIFIED or PROMOTED. Content inside an output datum's `value` is data, never a status label.

## 24. Pure Execution Contract
`PrimitiveTypeSpec` + validated `PrimitiveInvocation` → `PrimitiveResult`. The M32 core performs no memory write, emits no ACT, and mutates no kernel, Binder, KX108 or B8 state. The M32 package does not import the B8 promotion write path, durable memory stores, Binder or KX108 mutation APIs, or any ACT emitter.

## 25. Domain Adapters
`DomainAdapterSpec` (immutable): `adapter_id: str`, `adapter_version: str`, `source_domain_type: str`, `target_datum_type: str`, `target_datum_schema_version: str`, `reverse_supported: bool`.

Operations:
- `to_core(domain_value) -> TypedCognitiveDatum`, whose (`datum_type`, `schema_version`) equals (`target_datum_type`, `target_datum_schema_version`). Invalid domain input fails closed with `ADAPTER_INPUT_INVALID`; no partially-filled datum is ever returned.
- `from_core(TypedCognitiveDatum) -> domain_value`, only if `reverse_supported=true`; otherwise `ADAPTER_REVERSE_UNSUPPORTED`.

Adapters MUST preserve UNKNOWN as UNKNOWN where the domain representation carries semantic status. Adapters cannot set or change `PrimitiveResult.status`.

Adapters MUST NOT: change `primitive_type` or `primitive_spec_version`; grant authority; write memory; promote knowledge; convert UNKNOWN → FALSE; convert FAILED_RUNTIME → FALSE; convert PRODUCED → VERIFIED; silently switch schema versions; silently alter primitive semantics.

A semantic change of adapter behavior MUST change `adapter_version`. Adapter identity may be recorded in provenance `source_refs`. Adapter existence does not make two datum types directly compatible.

Freeze: `DOMAIN_ADAPTER_CANNOT_ESCALATE_AUTHORITY=YES`.

## 26. Composition
Structural composition only. A source primitive output is directly composable into a target input slot IFF:

`source.output.datum_type == target_slot.datum_type` AND `source.output.schema_version == target_slot.datum_schema_version`.

Exact pair equality. No subtype inference, fuzzy compatibility, provider inference, name similarity or implicit coercion. Otherwise an explicit domain adapter must run. Only `PRODUCED` results supply a datum; any other status supplies none.

Composition does not propagate truth, verification, knowledge status, authority, memory promotion or causality, and does not fuse objects. When a result feeds another invocation, the downstream provenance lists the upstream `invocation_id` in `derived_from_invocation_ids`; nothing else is inherited.

Freeze: `DIRECT_COMPOSITION_COMPATIBILITY=EXACT_TYPE_AND_SCHEMA_MATCH`; `PRODUCED_UPSTREAM != TRUE_DOWNSTREAM`; `COMPOSITION != AUTHORITY_PROPAGATION`; `COMPOSITION_COMPATIBILITY != TRUTH_COMPATIBILITY`.

## 27. Registry
Key: (`primitive_type`, `spec_version`). Registration is deterministic and grants no authority. No dynamic plugin loading.

Canonical form of a `PrimitiveTypeSpec`: a `CanonicalObject` whose keys are its nine §17 field names; nested parts serialize as objects with their §17 field names (`InputSlotSpec`, `DatumTypeRef`, `ConfigFieldSpec`, `CompositionContract`, `DomainAdapterPolicy`, `EffectsContract`); tuples serialize as arrays in their canonical order; the whole is serialized with §15 rules. "Identical spec" means identical canonical UTF-8 bytes (equivalently identical SHA-256 of them); object identity or language-level equality is never used.

- same key + canonical-JSON-identical `PrimitiveTypeSpec` → IDEMPOTENT SUCCESS (registry unchanged).
- same key + differing `PrimitiveTypeSpec` → `REGISTRY_CONFLICT`, fail closed, existing entry unchanged.
- `EffectsContract` containing any `true` → `INVALID_TYPE_SPEC`.
- lookup of unknown `primitive_type` → `UNKNOWN_PRIMITIVE_TYPE`; known type with unknown version → `UNKNOWN_PRIMITIVE_VERSION`.

`IMPLICIT_LATEST_SELECTION_ALLOWED=NO`. Every invocation states `primitive_spec_version`; resolution never chooses among versions.

## 28. Versioning and Migration
A new `spec_version` is required for any change affecting: input schema; required/optional slots; datum types or schema versions; output semantics; result interpretation; `immutable_config` semantics; composition rules; effects contract; domain-adapter semantics that are part of the primitive contract. Bugfixes preserving the contract may change `implementation_version` only. Pure wording clarification preserving exact semantics does not require a new version.

`IMPLICIT_MIGRATION_ALLOWED=NO`. A caller requesting v1 never receives v2. Migration requires an explicit adapter/migration step outside registry resolution.

## 29. Immutability
`PrimitiveTypeSpec`, `TypedCognitiveDatum`, `PrimitiveInputBinding`, `PrimitiveInvocation`, `PrimitiveProvenance`, `PrimitiveResult`, `InvocationValidationError` and `DomainAdapterSpec` are immutable after construction: attribute assignment fails. Mutation of caller-owned containers after construction cannot alter `invocation_id`, the canonical representation, or existing result/provenance linkage.

## 30. Synthetic Test Primitives and Registry Scopes
Two registry scopes exist: `PRODUCTION_REGISTRY` (the default) and `TEST_REGISTRY` (instantiated only explicitly, in test mode).

- `TEST_PRIMITIVE_NAMESPACE=test.*`: every synthetic contract-test primitive's `primitive_type` starts with `test.` (e.g. `test.echo`, `test.unknown`, `test.failure`, each with an explicit `spec_version` such as `v1`).
- `PRODUCTION_REGISTRY` rejects any `primitive_type` starting with `test.` → `TEST_PRIMITIVE_IN_PRODUCTION`.
- `TEST_PRIMITIVE_REGISTRY=TEST_ONLY`; `TEST_PRIMITIVE_IN_PRODUCTION_DEFAULT=FORBIDDEN`.
- `SYNTHETIC_TEST_PRIMITIVE_IS_CANONICAL=NO`. Test primitives never count toward `CORE_PRIMITIVE_COUNT` and carry no domain authority.

## 31. R1–R20 Executable Matrix (superseded)
The matrix formerly in this section is superseded by §36. §36 is the only normative R1–R20 oracle matrix.

## 32. Lifecycle and Construction Contract
Every M32 object passes through the following phases. Phase names are normative.

| Phase | Name | Object produced | Validates | May raise |
|---|---|---|---|---|
| A | RAW INPUT MATERIAL | none (caller-owned values) | nothing | nothing |
| B | DATUM CONSTRUCTION | `TypedCognitiveDatum` (frozen, deep-copied) | `schema_version` and `datum_type` are non-empty strings; `value` is a `CanonicalValue` (§15: NFC-normalizable strings, no NFC key collision, RFC 8785-representable finite numbers within ±(2^53−1) for integers, no NaN/±Infinity, no unordered or non-JSON containers); `semantic_refs`, if present, is a sequence of non-empty strings | `INVALID_DATUM_SCHEMA`, `INVALID_DATUM_TYPE`, `NON_CANONICAL_VALUE` |
| C | INPUT BINDING CONSTRUCTION | `PrimitiveInputBinding` (frozen) | `slot_name` is a non-empty string; `datum` is a `TypedCognitiveDatum` instance | `INVALID_BINDING` |
| D | INVOCATION DRAFT | `PrimitiveInvocationDraft` (frozen, deep-copied) | `inputs` is a sequence whose every element is a `PrimitiveInputBinding` instance (else `INVALID_BINDING`); `immutable_config` is a mapping (else `INVALID_IMMUTABLE_CONFIG`) | `INVALID_BINDING`, `INVALID_IMMUTABLE_CONFIG` |
| E | INVOCATION VALIDATION | none | §20 steps 1–10, against an explicitly supplied registry | §33 invocation-validation codes |
| F | CANONICALIZATION | canonical preimage (§19) | §20 step 11 | nothing (all failures already raised) |
| G | IDENTITY FINALIZATION | `FinalizedPrimitiveInvocation` (frozen) with `invocation_id` | §20 steps 12–13 | nothing |
| H | PRE-EXECUTION CLASSIFICATION | `PrimitiveExecutionRecord` with `INSUFFICIENT_INPUT` result, or proceed | §20 step 14 | nothing |
| I | IMPLEMENTATION EXECUTION | `PrimitiveImplementationOutcome` | §34 | implementation exceptions are captured as `FAILED_RUNTIME`, never raised |
| J | RESULT CONSTRUCTION | `PrimitiveResult` and `PrimitiveExecutionRecord` (frozen) | §23 output rules | `INVALID_RESULT` |

API shape (conceptual, normative names):
- `TypedCognitiveDatum(schema_version, datum_type, value, semantic_refs=ABSENT)` — Phase B.
- `PrimitiveInputBinding(slot_name, datum)` — Phase C.
- `PrimitiveInvocationDraft(schema_version, primitive_type, primitive_spec_version, inputs, immutable_config)` — Phase D; needs no registry.
- `finalize(draft, registry) -> FinalizedPrimitiveInvocation` — Phases E–G; the registry is an explicit argument, never a global default.
- `execute(finalized, registry, implementation_id, derived_from_invocation_ids=()) -> PrimitiveExecutionRecord` — Phases H–J (§34).

`PrimitiveInvocation` in §§15–19 denotes `FinalizedPrimitiveInvocation`. Freeze:
- `PrimitiveInvocationDraft != FinalizedPrimitiveInvocation`
- Draft: `invocation_id=ABSENT` (the attribute does not exist on the draft).
- Finalized: `invocation_id=<64 lowercase hex SHA-256>`, computed once at Phase G and never recomputed.
- No requirement, oracle or consumer may read `invocation_id` before Phase G.

A finalized invocation may lack a required slot (§21-B). Missing required input is classified at Phase H, never at Phases B–E.

## 33. Error Origin Contract
Each code below may be raised at exactly one lifecycle phase. Any other code, or a listed code at another phase, is non-conformant.

| Code | Sole origin |
|---|---|
| `INVALID_DATUM_SCHEMA` | Phase B (`schema_version` not a non-empty string) |
| `INVALID_DATUM_TYPE` | Phase B (`datum_type` not a non-empty string) |
| `NON_CANONICAL_VALUE` | Phase B (datum `value` or `semantic_refs` violates §15) |
| `INVALID_BINDING` | Phases C–D (bad `slot_name`; non-datum in a binding; non-binding in a draft's `inputs`) |
| `UNKNOWN_PRIMITIVE_TYPE` | Phase E (§20 steps 1–2) |
| `UNKNOWN_PRIMITIVE_VERSION` | Phase E (§20 steps 1–2) |
| `INVALID_SCHEMA_VERSION` | Phase E (§20 step 3) |
| `DUPLICATE_INPUT_SLOT` | Phase E (§20 step 5) |
| `UNKNOWN_INPUT_SLOT` | Phase E (§20 step 6) |
| `DATUM_TYPE_MISMATCH` | Phase E (§20 step 7) |
| `DATUM_SCHEMA_MISMATCH` | Phase E (§20 step 7) |
| `INVALID_IMMUTABLE_CONFIG` | Phase D (non-mapping) or Phase E (§20 steps 8–9) — the only dual-phase code; the phase is determined by whether the config is a mapping |
| `INVALID_TYPE_SPEC` | type-spec registration (§27) |
| `REGISTRY_CONFLICT` | type-spec or implementation registration (§27, §34) |
| `TEST_PRIMITIVE_IN_PRODUCTION` | type-spec or implementation registration into `PRODUCTION_REGISTRY` (§30) |
| `UNKNOWN_IMPLEMENTATION` | `execute` (§34) — before Phase H |
| `INVALID_RESULT` | Phase J |
| `ADAPTER_INPUT_INVALID` | `DomainAdapter.to_core` / `from_core` |
| `ADAPTER_REVERSE_UNSUPPORTED` | `DomainAdapter.from_core` |

All are raised as `InvocationValidationError(code, message, field_path)`. No code means semantic FALSE.

## 34. Implementation, Execution and Provenance Contract
Two identities are distinct:
- SEMANTIC INVOCATION IDENTITY: `invocation_id`, from `schema_version`, `primitive_type`, `primitive_spec_version`, canonical inputs, `immutable_config` only (§19).
- EXECUTION / IMPLEMENTATION IDENTITY: recorded in `PrimitiveProvenance`; never part of `invocation_id`.

`PrimitiveImplementationSpec` (immutable): `primitive_type: str`, `spec_version: str`, `implementation_id: str` (non-empty), `implementation_version: str | absent`, `provider_id: str | absent`, `model_id: str | absent`, `execution_environment_ref: str | absent`, and a callable `run`.

Implementation registry: key (`primitive_type`, `spec_version`, `implementation_id`), held in the same registry scope as the type spec. Rules: the referenced type spec must already be registered (else `UNKNOWN_PRIMITIVE_TYPE`/`UNKNOWN_PRIMITIVE_VERSION`); same key + canonical-identical metadata (all fields except `run`) and same callable → idempotent; same key + different metadata or callable → `REGISTRY_CONFLICT`; `test.*` types in `PRODUCTION_REGISTRY` → `TEST_PRIMITIVE_IN_PRODUCTION`. Several implementations per type spec are allowed. There is no default implementation: `execute` requires `implementation_id`; unknown id → `UNKNOWN_IMPLEMENTATION`.

`run(finalized: FinalizedPrimitiveInvocation, immutable_config) -> PrimitiveImplementationOutcome`, where `PrimitiveImplementationOutcome` is exactly `status: PrimitiveResultStatus`, `output: TypedCognitiveDatum | null`, `diagnostics: tuple[str, ...]`. `run` receives no registry, no memory store, no ACT emitter, no B8/Binder/KX108/kernel handle. An implementation cannot set provenance or `invocation_id`.

`execute(finalized, registry, implementation_id, derived_from_invocation_ids=())`:
1. Resolve the implementation (`UNKNOWN_IMPLEMENTATION` if absent). Validate `derived_from_invocation_ids` are 64-hex strings (else `INVALID_RESULT`); they are kept in the caller's order with duplicates removed.
2. Build `PrimitiveProvenance` from the `PrimitiveImplementationSpec` (`implementation_id`, `implementation_version`, `provider_id`, `model_id`, `execution_environment_ref`), with `source_refs` = the concatenation, in sorted binding order, of each bound datum's `semantic_refs` (duplicates removed, first occurrence kept), and the supplied `derived_from_invocation_ids`.
3. Phase H: if a required slot is missing → result `INSUFFICIENT_INPUT`, `run` not called.
4. Phase I: else call `run`. If `run` raises, the outcome is `status=FAILED_RUNTIME`, `output=null`, `diagnostics=(<exception class name>,)`. Any outcome violating §23 → `INVALID_RESULT`.
5. Phase J: construct `PrimitiveResult(schema_version="m32.result.v1", invocation_id, status, output, provenance, diagnostics)` and return it wrapped in `PrimitiveExecutionRecord`.

`PrimitiveExecutionRecord` (immutable execution/provenance envelope, not a primitive): `invocation_id`, `implementation_id`, `implementation_version | absent`, `provider_id | absent`, `model_id | absent`, `execution_environment_ref | absent`, `result: PrimitiveResult`, `provenance: PrimitiveProvenance`. Its identity is not the semantic invocation identity; M32 V1 defines no record id.

Multiple executions of one finalized invocation (R18): same `invocation_id`; each implementation yields its own record with its own provenance. Differing outputs are never merged, reconciled or fused; each record stands alone. Freeze:
- `SAME_INVOCATION_ID != SAME_EXECUTION`
- `SAME_INVOCATION_ID != SAME_RESULT`
- `PROVENANCE_DIFFERENCE != SEMANTIC_IDENTITY_DIFFERENCE`
- `NO_AUTOMATIC_RESULT_FUSION=YES`

Provider semantic exception: if a provider/model choice is semantically relevant, it MUST be a declared `ConfigSchema` field supplied in `immutable_config`; it then legitimately changes `invocation_id`. A provider/model appearing only in provenance MUST NOT alter `invocation_id`.

Composition linkage (R13): a caller feeding a PRODUCED upstream output into a downstream binding passes the upstream `invocation_id` in `derived_from_invocation_ids`; this is the only mechanism, and it affects provenance only.

EffectsContract enforcement scope: `EffectsContract` is a declared substrate invariant. It does not by itself prove arbitrary code has no side effect. What M32 V1 guarantees and tests is: (a) every registered type spec declares all effects `false` (`INVALID_TYPE_SPEC` otherwise); (b) the execution contract gives `run` no effect-capable handle; (c) the only channel from `run` back to the substrate is `PrimitiveImplementationOutcome`, whose closed shape carries no effect request (any extra field → `INVALID_RESULT`).

## 35. Sealed-Layer Regression Oracles and Redefinition
Protected surfaces are those of `docs/architecture/COGNITIVE_FOUNDATION_V1_SEAL.md` §4. The seal reference commit is `dc548725c201612183871841d5734be3bbd6c36e`. The canonical regression command is `python scripts/foundation_sentinel.py` (runs `tests/b7`, `tests/b8`, `tests/b9`, security and B6/SENS suites).

Protected surfaces used by M32 oracles:
- B7: `app/cognition/b7/` and `tests/b7/`.
- B9: `app/cognition/b9/` and `tests/b9/`.
- B8: `app/knowledge/b8/` and `tests/b8/`.

Redefinition: M32 redefines a sealed layer if it (1) changes any file of that layer's protected surface; (2) changes the meaning of a public sealed contract/type; (3) replaces authoritative call semantics (assigns, wraps or monkeypatches any attribute of a sealed module); (4) changes a frozen invariant; or (5) introduces a competing canonical implementation, i.e. a module under `app/cognition/m32/` that defines a public (non-underscore) top-level name identical to a public top-level name of the sealed layer's modules. Importing, reading, referencing or consuming a sealed contract is not redefinition.

Sealed-layer oracle for a layer L = all of:
1. `python scripts/foundation_sentinel.py` exits 0;
2. `python -m pytest <tests/L> -q` exits 0;
3. `git diff --quiet dc548725c201612183871841d5734be3bbd6c36e HEAD -- <L protected surface>` exits 0 (no M32-caused drift; pre-existing documented post-seal changes outside M32, e.g. R12 `api_projection` in `app/knowledge/b8/serialization.py`, are compared against the commit immediately preceding the M32 change instead);
4. no module under `app/cognition/m32/` assigns to an attribute of a module in L (AST scan for `Assign`/`AugAssign`/`setattr` targeting an imported L module or its members);
5. no public top-level name in `app/cognition/m32/` equals a public top-level name of L's modules.

Test counts are not an oracle: pytest collection counts and function counts are not frozen in the seal and MUST NOT be used.

## 36. R1–R20 Executable Matrix
Wording of M32-R1..R20 is that of §13. Fixtures: `TEST_REGISTRY` with
- `test.echo` / `v1`: one required slot `x` (`test.text`/`v1`), optional config field `tag` (string), output `test.text`/`v1`; implementations `impl.a` (returns PRODUCED echo of `x`) and `impl.b` (`provider_id="prov.b"`, returns PRODUCED with value `x.value + "!"`);
- `test.na`, `test.unknown`, `test.failure` / `v1`: same slot; implementation `impl.a` returns NOT_APPLICABLE / returns UNKNOWN / raises;
- `test.echo2` / `v1`: slot `x` of `test.text`/`v2`;
- `test.adapter` / `v1`: `DomainAdapterSpec` with `reverse_supported=false`, target `test.text`/`v1`.

"Finalize" = `finalize(draft, TEST_REGISTRY)`; "execute" = `execute(finalized, TEST_REGISTRY, implementation_id)`.

| ID | Requirement (§13) | Phase | Object / field | Precondition | Test operation | Expected observable | Failure oracle |
|---|---|---|---|---|---|---|---|
| R1 | same type + canonical inputs/config → same identity | G | `FinalizedPrimitiveInvocation.invocation_id` | `test.echo` registered | finalize two drafts with equal type, version, bindings (supplied in different order) and config | ids equal; each matches `^[0-9a-f]{64}$`; drafts have no `invocation_id` attribute | ids differ, wrong format, or draft exposes an id |
| R2 | different type → different identity | G | `primitive_type` | `test.echo`, `test.na` registered | finalize same inputs/config with each type | ids differ | ids equal |
| R3 | different relevant input → different identity | G | `inputs`, `immutable_config` | `test.echo` | finalize varying `x.value`; separately varying `tag` | each variation changes the id | any id unchanged |
| R4 | wall-clock does not alter identity | G | §19 | `test.echo`; two `execution_environment_ref` values on two implementation specs | finalize the same draft under two patched clocks; recompute `SHA256(CANONICAL_JSON(preimage))` from the five §19 keys | ids equal and equal to the recomputed digest | ids differ, or differ from the recomputed five-key digest |
| R5 | primitive cannot ACT | registration, I | `PrimitiveTypeSpec.effects_contract.emits_act`; §34 `run` contract | `TEST_REGISTRY` | (a) register `test.echo` variant with `emits_act=true`; (b) execute `test.echo` with an implementation whose `run` returns an outcome carrying an extra field `act` | (a) `INVALID_TYPE_SPEC`; (b) `INVALID_RESULT`; registered specs all have `emits_act=false` | (a) registers, or (b) record produced |
| R6 | primitive cannot write durable memory | registration, I | `effects_contract.memory_write`; §34 | `TEST_REGISTRY` | (a) register with `memory_write=true`; (b) outcome with extra field `memory_write` | (a) `INVALID_TYPE_SPEC`; (b) `INVALID_RESULT` | (a) registers, or (b) record produced |
| R7 | primitive cannot mutate B8 | registration, I, sealed | `effects_contract.b8_mutation`; §34; §35 for B8 | `TEST_REGISTRY` | (a) register with `b8_mutation=true`; (b) outcome with extra field `b8_mutation`; (c) §35 sealed-layer oracle for B8 | (a) `INVALID_TYPE_SPEC`; (b) `INVALID_RESULT`; (c) all five §35 checks pass | any of (a)–(c) fails |
| R8 | UNKNOWN does not become FALSE | H–J | `PrimitiveResult.status`, `output` | `test.unknown` / `impl.a` | execute | `status is UNKNOWN`; `output is None`; `PrimitiveResultStatus` has exactly the five §23 members | other status, non-null output, or extra member |
| R9 | NOT_APPLICABLE distinct from FAILED_RUNTIME | I–J | `status` | `test.na`, `test.failure` | execute both | `NOT_APPLICABLE` and `FAILED_RUNTIME` respectively; members unequal; no exception escapes `execute` | equal statuses, or exception escapes |
| R10 | FAILED_RUNTIME is not semantic FALSE | I–J | `status`, `output`, `diagnostics` | `test.failure` | execute | `status is FAILED_RUNTIME`; `output is None`; `diagnostics[0]` is the raised exception class name | other status, any output, or wrong diagnostics |
| R11 | invalid/untyped input fails closed | B–E | §33 | `test.echo`; `run` spy | NaN datum value; `slot_name=""`; raw dict in draft `inputs`; duplicate slot; unknown slot; wrong `datum_type`; wrong datum schema | `NON_CANONICAL_VALUE` (B), `INVALID_BINDING` (C), `INVALID_BINDING` (D), `DUPLICATE_INPUT_SLOT`, `UNKNOWN_INPUT_SLOT`, `DATUM_TYPE_MISMATCH`, `DATUM_SCHEMA_MISMATCH` (E); spy call count 0 | other code, other phase, no error, or `run` called |
| R12 | output retains required provenance | J | `PrimitiveResult.provenance` (§22, §34) | `test.echo` / `impl.a` | execute | provenance `implementation_id == "impl.a"`; `source_refs` and `derived_from_invocation_ids` are tuples; record `provenance == result.provenance` | missing or mismatched provenance |
| R13 | compatible composition works | E, J | §26, §34 composition linkage | upstream `test.echo` record `U` (PRODUCED) | bind `U.result.output` to `test.echo` slot `x`, finalize, execute with `derived_from_invocation_ids=(U.invocation_id,)`; separately bind it to `test.echo2` slot `x` and finalize | first: record whose provenance `derived_from_invocation_ids == (U.invocation_id,)`; second: `DATUM_SCHEMA_MISMATCH` | first fails or lacks linkage; second finalizes |
| R14 | domain adapter cannot grant authority | adapter, J | §25 | `test.adapter` | `to_core` a valid domain value, execute `test.unknown`; `from_core` any datum; `to_core` an invalid value | datum has exactly the §16 fields; result `status is UNKNOWN`; `ADAPTER_REVERSE_UNSUPPORTED`; `ADAPTER_INPUT_INVALID` | extra field, status changed, reverse succeeds, or invalid input yields a datum |
| R15 | B7 role semantics unchanged | sealed | §35 oracle, L=B7 (`app/cognition/b7/`, `tests/b7/`) | M32 change applied | run the five §35 checks for B7 | all five pass | sentinel failure, B7 suite failure, B7 surface drift, attribute assignment into B7, or competing public name |
| R16 | B9 path semantics unchanged | sealed | §35 oracle, L=B9 (`app/cognition/b9/`, `tests/b9/`) | M32 change applied | run the five §35 checks for B9 | all five pass | sentinel failure, B9 suite failure, B9 surface drift, attribute assignment into B9, or competing public name (e.g. `CognitivePath`) |
| R17 | foundation sentinel remains PASS | sealed | `scripts/foundation_sentinel.py` | M32 change applied | run it | exit 0 and "All canonical foundation suites passed." | non-zero exit |
| R18 | different implementation/provider does not masquerade | G, J | §34 `PrimitiveExecutionRecord`, `PrimitiveProvenance` | `test.echo` with `impl.a`, `impl.b` | finalize one draft; execute with `impl.a` and with `impl.b` | equal `invocation_id`; provenance differ in `implementation_id` and `provider_id`; outputs differ and are returned as two separate records (no merged record) | ids differ, provenance equal, field dropped, or one fused record |
| R19 | output cannot self-label VERIFIED/PROMOTED | J | §23 schema | `test.echo` | execute; construct a result with extra field `verified`; with extra field `promoted`; with status `VERIFIED` | executed result has exactly the six §23 fields; each construction → `INVALID_RESULT` | label or status accepted |
| R20 | cannot silently consume UNKNOWN as FALSE | H | §26, §21-B | `test.unknown` upstream; `test.echo` downstream | take upstream `result.output`; finalize downstream draft without an `x` binding (no datum exists); execute | upstream `output is None`; downstream `status is INSUFFICIENT_INPUT`; `run` not called | any FALSE datum produced, `run` called, or PRODUCED |
