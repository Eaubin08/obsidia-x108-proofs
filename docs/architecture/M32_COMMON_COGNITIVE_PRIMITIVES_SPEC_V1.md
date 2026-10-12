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
This section is normative. Where §§1–13 are less precise, §§14–31 govern.

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

Implementation location (used by oracles in §31): M32 runtime code, when written, lives under `app/cognition/m32/`. Contract tests live under `tests/m32/`.

## 15. Canonical Value and Canonical JSON
`CanonicalValue` is exactly one of: `null`, `true`/`false`, a string, a finite JSON number, an array of `CanonicalValue`, or an object with string keys and `CanonicalValue` values (`CanonicalObject`).

The following MUST NOT appear inside a `CanonicalValue`: `set`, `frozenset`, any map type whose iteration order is not semantically fixed, bytes, enum objects, paths, dataclasses, or objects relying on a custom `repr`. Producers (normally domain adapters) MUST convert unordered collections, before `TypedCognitiveDatum` construction, into either an array whose semantic order is explicitly defined by the producer, or a `CanonicalObject`. A value violating this rule causes `NON_CANONICAL_VALUE` (§21). Tuples serialize as arrays.

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
Validation runs in exactly this order; the first failing step determines the outcome:

1. Resolve the registry key (`primitive_type`, `primitive_spec_version`): unknown type → `UNKNOWN_PRIMITIVE_TYPE`; known type, unknown version → `UNKNOWN_PRIMITIVE_VERSION`.
2. Validate invocation `schema_version == "m32.invocation.v1"`, else `INVALID_SCHEMA_VERSION`.
3. Validate `primitive_spec_version` is the exact registered string (no ranges, no "latest"), else `UNKNOWN_PRIMITIVE_VERSION`.
4. Validate binding structure (each binding has a str `slot_name` and a well-formed `TypedCognitiveDatum`), else `INVALID_BINDING`.
5. Detect duplicate `slot_name` → `DUPLICATE_INPUT_SLOT`.
6. Reject slots not declared in `input_slots` → `UNKNOWN_INPUT_SLOT`.
7. For each supplied slot: `datum_type` mismatch → `DATUM_TYPE_MISMATCH`; then datum `schema_version` ≠ slot `datum_schema_version` → `DATUM_SCHEMA_MISMATCH`.
8. Validate `immutable_config` against `ConfigSchema`, else `INVALID_IMMUTABLE_CONFIG`.
9. Validate all values are canonically serializable (§15), else `NON_CANONICAL_VALUE`.
10. Classify missing required slots (not an error).
11. Construct the canonical invocation representation.
12. Compute `invocation_id`.
13. If any required slot is missing: return `PrimitiveResult(status=INSUFFICIENT_INPUT, output=null)` without calling the implementation.
14. Otherwise the implementation may execute.

No implementation code may execute before steps 1–12 succeed. A failure in steps 1–9 raises `InvocationValidationError`; no `PrimitiveResult` and no `invocation_id` are produced.

## 21. Two Outcomes: Invalid vs. Incomplete
A. INVALID INVOCATION → `InvocationValidationError` (immutable): `code: str`, `message: str`, `field_path: str | absent`. Invocation codes (closed V1 set): `UNKNOWN_PRIMITIVE_TYPE`, `UNKNOWN_PRIMITIVE_VERSION`, `INVALID_SCHEMA_VERSION`, `INVALID_BINDING`, `DUPLICATE_INPUT_SLOT`, `UNKNOWN_INPUT_SLOT`, `DATUM_TYPE_MISMATCH`, `DATUM_SCHEMA_MISMATCH`, `INVALID_IMMUTABLE_CONFIG`, `NON_CANONICAL_VALUE`. Registry/adapter/result codes use the same error shape: `REGISTRY_CONFLICT`, `INVALID_TYPE_SPEC`, `TEST_PRIMITIVE_IN_PRODUCTION`, `ADAPTER_INPUT_INVALID`, `ADAPTER_REVERSE_UNSUPPORTED`, `INVALID_RESULT`.

B. VALID BUT INCOMPLETE INVOCATION → `PrimitiveResult.status=INSUFFICIENT_INPUT`, `output=null`, implementation not called, `invocation_id` computed over the supplied bindings.

Freeze:
- `MISSING_REQUIRED_SLOT → INSUFFICIENT_INPUT`
- `DUPLICATE_SLOT → INVALID_INVOCATION`
- `WRONG_TYPE → INVALID_INVOCATION`
- `UNKNOWN_EXTRA_SLOT → INVALID_INVOCATION`
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

## 31. R1–R20 Executable Matrix
The wording of M32-R1..R20 is that of §13; this matrix gives each a direct oracle. Fixtures use `TEST_REGISTRY` with:
- `test.echo` v1: one required slot `x` (`test.text`/`v1`), one optional config field `tag` (string), output `test.text`/`v1`, returns PRODUCED echoing `x`;
- `test.na` v1, `test.unknown` v1, `test.failure` v1: same slot; return NOT_APPLICABLE, return UNKNOWN, raise an exception, respectively;
- `test.adapter` v1: `DomainAdapterSpec` with `reverse_supported=false`, target `test.text`/`v1`.

| ID | Requirement (§13) | Runtime object / field | Precondition | Test operation | Expected observable | Failure oracle |
|---|---|---|---|---|---|---|
| R1 | same type + canonical inputs/config → same identity | `PrimitiveInvocation.invocation_id` (§19) | `test.echo` v1 registered | build two invocations with equal type, version, bindings (supplied in different order) and config | ids equal; each is 64 lowercase hex | ids differ, or wrong format |
| R2 | different type → different identity | `primitive_type` in preimage | `test.echo`, `test.na` registered | same inputs/config, different type | ids differ | ids equal |
| R3 | different relevant input → different identity | `inputs`, `immutable_config` | `test.echo` | vary `x.value`; separately vary `tag` | each variation changes the id | any id unchanged |
| R4 | wall-clock does not alter identity | §19 exclusions | `test.echo` | build the same invocation under two patched clocks and two host/environment values | ids equal; preimage keys are exactly the five §19 keys | ids differ, or preimage holds time/host data |
| R5 | primitive cannot ACT | `PrimitiveTypeSpec.effects_contract.emits_act`; §24 | registry | register a spec with `emits_act=true`; execute `test.echo`; scan `app/cognition/m32/` imports | `INVALID_TYPE_SPEC`; no ACT emitter imported or invoked | registration succeeds, or an ACT emitter is imported/invoked |
| R6 | cannot write durable memory | `effects_contract.memory_write`; §24 | registry | register with `memory_write=true`; execute; scan imports | `INVALID_TYPE_SPEC`; no memory-store import or write | registration succeeds, or a write/import is observed |
| R7 | cannot mutate B8 | `effects_contract.b8_mutation`; §24 | registry; B8 state snapshot | register with `b8_mutation=true`; execute and compare snapshot; scan imports | `INVALID_TYPE_SPEC`; snapshot unchanged; no B8 promotion write-path import | registration succeeds, snapshot changes, or import found |
| R8 | UNKNOWN does not become FALSE | `PrimitiveResult.status`, `output` | `test.unknown` | execute | `status == UNKNOWN`; `output is None`; status enum has exactly the five §23 members | other status, non-null output, or extra/FALSE member |
| R9 | NOT_APPLICABLE distinct from FAILED_RUNTIME | `status` | `test.na`, `test.failure` | execute both | `NOT_APPLICABLE` and `FAILED_RUNTIME` respectively; members distinct | equal statuses, or exception escapes |
| R10 | FAILED_RUNTIME is not semantic FALSE | `status`, `output` | `test.failure` | execute | `status == FAILED_RUNTIME`; `output is None` | other status, or any output datum |
| R11 | invalid/untyped input fails closed | §20, §21-A | `test.echo`; implementation spy | duplicate slot; unknown slot; wrong `datum_type`; wrong datum schema; NaN value; raw dict instead of datum | `InvocationValidationError` with `DUPLICATE_INPUT_SLOT`, `UNKNOWN_INPUT_SLOT`, `DATUM_TYPE_MISMATCH`, `DATUM_SCHEMA_MISMATCH`, `NON_CANONICAL_VALUE`, `INVALID_BINDING` respectively; spy call count 0 | different code, no error, or implementation called |
| R12 | output retains required provenance | `PrimitiveResult.provenance` (§22) | `test.echo` | execute | provenance is a `PrimitiveProvenance` with non-empty `implementation_id`, and tuple-typed `source_refs` and `derived_from_invocation_ids` | provenance missing or a required field absent |
| R13 | compatible composition works | §26 | `test.echo` output `test.text`/`v1`; second test spec `test.echo2` v1 with slot `x` of `test.text`/`v2` | feed the PRODUCED output into `test.echo` slot `x`; then into `test.echo2` slot `x` | first is a valid invocation whose provenance lists the upstream id in `derived_from_invocation_ids`; second raises `DATUM_SCHEMA_MISMATCH` | first rejected, or second accepted |
| R14 | domain adapter cannot grant authority | §25 `DomainAdapterSpec`, `to_core`, `from_core` | `test.adapter` v1 | `to_core` a valid domain value, then execute `test.unknown` with it; call `from_core`; call `to_core` on invalid input | datum has exactly the §16 fields; result status stays `UNKNOWN`; `from_core` → `ADAPTER_REVERSE_UNSUPPORTED`; invalid input → `ADAPTER_INPUT_INVALID` | extra authority/verification field, status changed, reverse succeeds, or invalid input yields a datum |
| R15 | B7 role semantics unchanged | sealed B7 suite; M32 import graph | M32 change applied | run `python -m pytest tests/b7 -q`; statically scan `app/cognition/m32/` | B7 suite passes with no fewer tests than at foundation seal `dc548725`; M32 performs no attribute assignment into `app.cognition.b7` and does not subclass or redefine B7 contracts | any B7 failure, test-count drop, or M32 override of B7 |
| R16 | B9 path semantics unchanged | sealed B9 suite; M32 import graph | M32 change applied | run `python -m pytest tests/b9 -q`; statically scan `app/cognition/m32/` | B9 suite passes with no fewer tests than at `dc548725`; no M32 assignment into `app.cognition.b9`; no redefinition of B9 path contracts | any B9 failure, test-count drop, or override |
| R17 | foundation sentinel remains PASS | `scripts/foundation_sentinel.py` | M32 change applied | run `python scripts/foundation_sentinel.py` | exit code 0 and "All canonical foundation suites passed." | non-zero exit |
| R18 | different implementation/provider does not masquerade | `PrimitiveProvenance` | the same invocation executed by two implementations differing in `implementation_id` (and separately `provider_id`) | execute both | equal `invocation_id`; provenance records differ in exactly the differing field | provenance equal, or field dropped |
| R19 | output cannot self-label VERIFIED/PROMOTED | §23 `PrimitiveResult` schema | `test.echo` | execute; attempt to construct a result with an extra field `verified` or `promoted`, or with status `VERIFIED` | executed result has exactly the six §23 fields; each attempt raises `INVALID_RESULT` | extra label or unknown status accepted |
| R20 | cannot silently consume UNKNOWN as FALSE | §26 (only PRODUCED supplies a datum); §21-B | `test.unknown` upstream; `test.echo` downstream | take the UNKNOWN result's `output` and build the downstream invocation from available data | upstream `output is None`; downstream invocation has no `x` binding and returns `INSUFFICIENT_INPUT` without calling the implementation | any FALSE datum is produced, or downstream returns `PRODUCED` |
