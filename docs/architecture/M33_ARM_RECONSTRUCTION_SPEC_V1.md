# M33_ARM_RECONSTRUCTION_SPEC_V1

Status: NORMATIVE SPECIFICATION (docs only). Not implemented. Not yet independently certified.

## 1. Normative hierarchy

`COGNITIVE_FOUNDATION_V1` > `M33_ARM_RECONSTRUCTION_DOCTRINE_V1` (certified, commit `0bb2b01c`) > `M33_ARM_RECONSTRUCTION_SPEC_V1` (this file) > future M33 runtime.

This specification refines names, fields, enums, identity preimages, canonical serialization usage, lifecycle, validation, error taxonomy, runtime API and test oracles. It never contradicts the doctrine.

- `FOUNDATION_REOPEN=NO`
- `M33_DOCTRINE_OVERRIDE_ALLOWED=NO`

Within this file, the section named as sole authority for a topic controls: types §9–§18, identity §19, ordering §20, lifecycle §22, errors §23, status rules §24, requirement oracles §36, adversarial oracles §37.

Process discipline: `PRESENT != WIRED != TESTED != PROVED != CLOSED`. After this file is committed: `M33_SPEC_PRESENT=YES`, `M33_RUNTIME_PRESENT=NO`, `M33_TESTED=NO`, `M33_PROVED=NO`, `M33_CLOSED=NO`.

## 2. Canonical ARM definition (carried from doctrine)

- `ARM_CANONICAL_EXPANSION=Agent Reconstruction Méthodique`
- `ARM_CANONICAL_MISSION` = « Reconstruire méthodiquement une structure cognitive explicite, traçable et non souveraine à partir d'un matériau fragmenté, dispersé, implicite, incomplet, contradictoire ou désordonné. »
- `ARM_IS_SCHEDULER=NO`, `ARM_IS_ROUTER=NO`, `ARM_IS_ROLE_SYSTEM=NO`, `ARM_IS_MEMORY=NO`, `ARM_IS_WORLD_MODEL=NO`, `ARM_IS_KNOWLEDGE_PROMOTION=NO`, `ARM_IS_ACTION_AUTHORITY=NO`
- `M32_IS_ARM=NO`, `M32_IS_ARM_SUBSTRATE=YES`

## 3. Source attribution (N1)

Three evidence levels are distinguished; later terminology is never attributed retroactively to the earliest source.

| Level | Content | Sources |
|---|---|---|
| A — direct historical source | methodological reconstruction of dispersed or latent material: reconnecting dissociated pieces of reasoning (« Reconnecter les morceaux dissociés du raisonnement »), recovering forgotten / latent / implicit concepts, detecting gaps and incoherence, classifying « déjà intégré / évoqué non verrouillé / non présent », structured reporting | ARM prompt docx (outside repo); `arm_microagents` family B13 / C346–C355 (outside repo, inventoried in repo commits `ea27f591` and `d20356f0`); archived note `b78d5da2` |
| B — later lineage | extension of the mission to cognitive trajectories, paths, relations, decomposition/recomposition; ARM → chemins cognitifs → biologie → cycles/cosmos | « Concept Obsi », source 94 and later cognitive-path material supplied by the project owner (not present in this repository); SENS-14 roadmap line (`4a6fd23f`, reference only) |
| C — current certified synthesis | `HISTORICAL_MISSION_MODERN_SUBSTRATE` | M33 doctrine `0bb2b01c`, independently certified |

The direct ARM source establishes methodological reconstruction of dispersed or latent material. Later lineage extends that mission to reconstruction of cognitive trajectories and relations. The certified M33 doctrine unifies these generations without retroactively attributing later terminology to the earliest source.

- `N1_SOURCE_ATTRIBUTION_CORRECTED=YES`
- `HISTORICAL_SOURCE_RETROJECTION_FORBIDDEN=YES`
- `N1_RESOLVED_BY_SPEC=YES`
- Provenance hygiene: `d20356f0` VERIFIED as an inventory-only reference (`runtime_wiring/source_registry/source_file_registry.csv|json` list `family_specs/39_arm_microagents.spec.yaml` as `COPIED_READONLY`, advisory-only, no runtime import). It is not normative support for any rule in this file.

No historical source is runtime truth. Level A–B sources are lineage evidence only.

## 4. V1 model and scope

`M33_V1_MODEL=BOUNDED_TYPED_RECONSTRUCTION`: M33 V1 receives a bounded typed request and explicit reconstruction contributions and returns a deterministic bounded `ReconstructionResult`.

M33 V1 does NOT: discover external data; fetch context; query memory; select providers, roles or primitives; spawn agents; route capabilities; optimize cost; schedule primitives; persist anything; promote knowledge; act.

- `M33_AUTONOMOUS_ROLE_SELECTION=NO`
- `M33_AUTONOMOUS_PRIMITIVE_SELECTION=NO`
- `M33_AUTONOMOUS_PROVIDER_SELECTION=NO`
- `M33_SCHEDULER=NO`
- `M33_CONTEXT_FETCH=NO`
- `M33_MEMORY_LOOKUP=NO`

## 5. Runtime location

Seal §4 protects `app/cognition/`, `app/knowledge/b8/`, `app/harness/state_explicit/` (plus sentinel targets). `app/reconstruction/` is not protected.

- `M33_RUNTIME_LOCATION=app/reconstruction/m33/` (package `app.reconstruction.m33`)
- `M33_TEST_LOCATION=tests/m33/`
- `M33_RUNTIME_INSIDE_FOUNDATION_SEAL=NO`; `FOUNDATION_REOPEN=NO`
- No sealed `__init__.py` is edited to expose M33. M33 imports `app.primitives.m32` (consumption only).

## 6. M32 seam

M33 consumes from `app.primitives.m32`: `TypedCognitiveDatum`; invocation ids (64 lowercase hex) as provenance references; `PrimitiveResultStatus` semantics; M32 canonical JSON (§15 of the M32 spec, including RFC 8785 numbers and NFC); M32 provenance conventions; M32 exact type/schema compatibility rule.

- `M33_MAY_USE_M32_PRIMITIVES=YES`; `M33_MAY_REDEFINE_M32_PRIMITIVES=NO`
- `CORE_PRIMITIVE_COUNT=0`; M33 V1 registers no primitive. A future reconstruction primitive requires a separate certified change.
- `M32_STATUS_SEMANTICS_PRESERVED=YES`. Mapping when a contribution is derived from an M32 `PrimitiveResult` (§15):
  - `PRODUCED` → the contribution may carry items/relations; PRODUCED does not mean verified.
  - `UNKNOWN`, `NOT_APPLICABLE`, `INSUFFICIENT_INPUT` → contribution `COMPLETED` carrying no item derived from that result; it may carry an issue (§17). M32 UNKNOWN never becomes FALSE, ABSENT_IN_SCOPE or evidence.
  - `FAILED_RUNTIME` → contribution status `FAILED_RUNTIME` (§15). Never interpreted as absent material.

## 7. Identifiers and strings

- All strings are NFC-normalized at construction (M32 rule).
- `NAMESPACED_KIND` = regex `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$` (e.g. `arm.concept`). Used by `reconstruction_kind`, `item_kind`, `relation_kind`, derivation descriptors.
- `OPAQUE_ID` = non-empty NFC string without leading/trailing whitespace. Used by `material_id`, `contribution_id`, `source_ref`, `inspection_scope_ref`, `role_ref`, provenance ids.
- `HEX64` = `^[0-9a-f]{64}$` (computed ids, M32 invocation ids).
- `ITEM_KIND != PRIMITIVE_TYPE`: item kinds are descriptive reconstruction categories; they never name or create M32 primitive types.

## 8. Error type

`ReconstructionValidationError(code: str, message: str, field_path: str | absent)` — immutable exception. Codes and sole origins: §23. A validation error never means semantic FALSE and is never a `ReconstructionStatus`.

## 9. ReconstructionMaterial

Purpose: one bounded input unit, supplied by the caller (already admissible; B6 owns context assembly).

| Field | Type | Rule | Identity |
|---|---|---|---|
| `material_id` | OPAQUE_ID | required | yes (request) |
| `datum` | M32 `TypedCognitiveDatum` | required; `MATERIAL_PAYLOAD_TYPE=M32 TypedCognitiveDatum` | yes, M32 datum canonical form |
| `source_refs` | tuple[OPAQUE_ID, ...] | required, may be empty; stored sorted by code point, duplicates removed | yes |
| `context_origin` | OPAQUE_ID or absent | optional; descriptive reference to the B6 surface the caller used | NO (provenance only) |

Immutable; deep-copied. Violations → `INVALID_MATERIAL` at construction. Material supplied by a caller is not evidence of truth.

## 10. ReconstructionRequest

Purpose: immutable, fully validatable description of one bounded reconstruction.

| Field | Type | Rule | Identity |
|---|---|---|---|
| `schema_version` | str | exactly `"m33.request.v1"` | yes |
| `reconstruction_kind` | NAMESPACED_KIND | required | yes |
| `materials` | tuple[ReconstructionMaterial, ...] | may be empty; `material_id` unique; stored sorted by `material_id` | yes |
| `inspection_scope_ref` | OPAQUE_ID or absent | §11 | yes (absent omitted) |
| `bounds` | ReconstructionBounds | required | yes |

`ReconstructionBounds` (immutable): `max_items`, `max_relations`, `max_supports_per_unit`, `max_derivation_depth`, each an int with 1 ≤ n ≤ 2^53−1. All four participate in identity.

`request_id = SHA256(CANONICAL_JSON(request preimage))` (§19), exposed as a derived attribute.

The request carries no provider selector, role policy, clock, memory writer, action, Binder or KX108 handle. Violations (schema, kind, duplicate material ids, non-material element, bounds) → `INVALID_RECONSTRUCTION_REQUEST` at construction.

## 11. Bounded inspection scope

`ABSENT_IN_SCOPE` never means globally nonexistent. It means: not found within the materials of this request, labeled by `inspection_scope_ref`.

- `ABSENT != GLOBALLY_FALSE`; `ABSENT = NOT_FOUND_WITHIN_DECLARED_INSPECTION_SCOPE`
- The declared inspection scope of a request is exactly its `materials`; `inspection_scope_ref` names it.
- If `inspection_scope_ref` is absent, no contributed item may carry `ABSENT_IN_SCOPE` (→ `INVALID_INTEGRATION_STATUS`, checked per contributed item before merge, §22 step 3); `UNDETERMINED` is used instead.

## 12. IntegrationStatus

Enum, exactly:

| Value | Meaning |
|---|---|
| `ALREADY_INTEGRATED` | the reconstructed unit corresponds to structure the contributor reports as already established in the inspected materials |
| `EVOKED_NOT_LOCKED` | evoked in the materials but not established |
| `ABSENT_IN_SCOPE` | not found within the declared inspection scope (§11) |
| `UNDETERMINED` | no defensible determination |

`INTEGRATION_STATUS_IS_DESCRIPTIVE_ONLY=YES`. It is not epistemic truth, verification, B8 state, memory state or authority. `UNKNOWN != ABSENT`; `UNDETERMINED != ABSENT_IN_SCOPE`.

## 13. Support

`ReconstructionSupportKind`: exactly `EVIDENCE`, `INFERENCE`. No `VERIFIED` value.

`ReconstructionSupportRef` (immutable): `ref_kind` ∈ {`MATERIAL`, `SOURCE`, `ITEM`}, `ref_id` (OPAQUE_ID for MATERIAL/SOURCE; HEX64 for ITEM).

`ReconstructionSupport` (immutable):

| Field | Type | Rule | Identity |
|---|---|---|---|
| `kind` | ReconstructionSupportKind | required | yes (result id) |
| `refs` | tuple[ReconstructionSupportRef, ...] | non-empty; stored sorted by (`ref_kind`, `ref_id`), duplicates removed | yes (result id) |
| `derivation` | NAMESPACED_KIND or absent | descriptive label only, never authority | yes if present (result id) |

Shape rules (construction, `INVALID_DERIVATION`): EVIDENCE refs are only MATERIAL or SOURCE; INFERENCE refs are only MATERIAL or ITEM and at least one ref (derivation basis). Inference with no basis is invalid.

Resolution rules (lifecycle step 6, `INVALID_SUPPORT_REFERENCE`): MATERIAL → a `material_id` of the request; SOURCE → a `source_ref` of some request material; ITEM → the `item_id` of an item present in the contributions. No dangling reference is accepted.

- `EVIDENCE != INFERENCE`; `INFERENCE != VERIFIED`; `EVIDENCE != VERIFIED`

## 14. ReconstructionItem and ReconstructionRelation

`ReconstructionItem` is the canonical M33 reconstructed unit: a typed, provenance-bearing, non-authoritative unit proposed by ARM. `M33_RUNTIME_RECONSTRUCTION_UNIT=ReconstructionItem`.

| Field | Type | Rule | Item identity |
|---|---|---|---|
| `item_kind` | NAMESPACED_KIND | required | yes |
| `content` | M32 `TypedCognitiveDatum` | required | yes |
| `supports` | tuple[ReconstructionSupport, ...] | 1..`max_supports_per_unit` (bound checked at lifecycle step 5); stored sorted by canonical JSON | no (aggregated, §21) |
| `integration_status` | IntegrationStatus | required | no |
| `item_id` | HEX64 | derived at construction (§19) | — |

Shape violations → `INVALID_RECONSTRUCTION_ITEM` at construction. No field named or meaning truth, verified, promoted, authority, confidence. `RECONSTRUCTION_ITEM != VERIFIED_KNOWLEDGE`; `!= B8_PROMOTION_OBJECT`; `!= MEMORY_RECORD`.

`ReconstructionEndpoint` (immutable): `kind` ∈ {`MATERIAL`, `ITEM`}, `ref_id`.

`ReconstructionRelation`:

| Field | Type | Rule | Relation identity |
|---|---|---|---|
| `relation_kind` | NAMESPACED_KIND | required | yes |
| `source` | ReconstructionEndpoint | required | yes |
| `target` | ReconstructionEndpoint | required; `source != target` | yes |
| `supports` | tuple[ReconstructionSupport, ...] | 1..`max_supports_per_unit` | no (aggregated) |
| `relation_id` | HEX64 | derived (§19) | — |

Shape violations (kind, self-relation, missing supports) → `INVALID_RECONSTRUCTION_RELATION` at construction; unknown endpoints → `INVALID_RELATION_REFERENCE` at lifecycle step 8.

Relations carry no transitive closure, truth, authority or memory propagation. `RELATION_SET != ARM_GRAPH`; `GRAPH_REQUIRED=NO`; a relation set may be projected as a graph downstream; M33 V1 defines no graph execution. `ReconstructionRelation != CognitivePath`.

Reserved relation kind: `arm.contradicts` (§17).

## 15. Contributions

`ReconstructionContributor` (immutable, provenance only, never in semantic identity): `role_ref` (OPAQUE_ID naming an existing B7 role, optional), `implementation_id`, `provider_id`, `model_id` (optional OPAQUE_ID), `primitive_invocation_id` (HEX64, optional). At least one field present.

`ContributionStatus`: exactly `COMPLETED`, `FAILED_RUNTIME`.

`ReconstructionContribution` (immutable):

| Field | Type | Rule |
|---|---|---|
| `contribution_id` | OPAQUE_ID | unique within one `reconstruct` call |
| `contributor` | ReconstructionContributor | required |
| `status` | ContributionStatus | required |
| `items` | tuple[ReconstructionItem, ...] | empty if `FAILED_RUNTIME` |
| `relations` | tuple[ReconstructionRelation, ...] | empty if `FAILED_RUNTIME` |
| `issues` | tuple[ReconstructionIssue, ...] | contributor-declared issues |
| `diagnostics` | tuple[str, ...] | non-semantic |

Construction violations → `INVALID_CONTRIBUTION`. M33 does not choose contributors; the caller supplies them explicitly. Role identity, if any, is provenance; M33 defines no role registry, no role semantics, no competence-based choice. `M33_UTILITY_SCORE_AUTHORITY=NO`; `M33_CONFIDENCE_AUTHORITY=NO`; V1 has no confidence field.

## 16. Effects contract

`ReconstructionEffectsContract` (immutable), all fields fixed `False`: `memory_write`, `emits_act`, `b8_mutation`, `binder_mutation`, `kernel_mutation`, `kx108_mutation`, `external_io`, `durable_state_write`. Constructing it with any `True` value → `INVALID_EFFECTS_CONTRACT`. The module exposes one instance as `RECONSTRUCTION_EFFECTS`. No effect-capable handle is ever passed into or stored by reconstruction logic.

## 17. Issues

`ReconstructionIssueKind`: exactly

| Value | Meaning |
|---|---|
| `UNRESOLVED_REFERENCE` | a referent named by the material cannot be resolved within the request |
| `CONTRADICTORY_SUPPORT` | two structurally valid items are declared in contradiction |
| `AMBIGUOUS_RECONSTRUCTION` | more than one reconstruction is defensible, or contributors disagree on an item's integration status |
| `INSUFFICIENT_MATERIAL` | the materials do not suffice for an aspect of the requested reconstruction |

`ReconstructionIssue` (immutable): `issue_kind`, `subject_ids` (tuple of HEX64 item/relation ids or material ids; may be empty; stored sorted, duplicates removed), `detail` (NAMESPACED_KIND or absent; descriptive). Construction violations → `INVALID_RECONSTRUCTION_ISSUE`.

Issues come from: (a) contributors (`contribution.issues`); (b) the engine, deterministically: every relation of kind `arm.contradicts` yields `CONTRADICTORY_SUPPORT` with `subject_ids` = its two endpoint ids; two or more contributed items with the same `item_id` (in the same or in different contributions, §21) with different `integration_status` yield `AMBIGUOUS_RECONSTRUCTION` with `subject_ids=(item_id,)` and the item's status becomes `UNDETERMINED`.

Issues coexist with RECONSTRUCTED or PARTIAL results (§24). Contradictory items are both preserved; M33 never chooses a branch. `CONTRADICTION != AUTO_RESOLUTION`; `CONTRADICTION != FALSE`; `CONTRADICTION_DOES_NOT_GRANT_AUTHORITY=YES`. `UNKNOWN != FALSE`; `UNRESOLVED != ABSENT_IN_SCOPE`; `UNRESOLVED != FAILED_RUNTIME`.

## 18. ReconstructionResult and provenance

`ReconstructionStatus`: exactly `RECONSTRUCTED`, `PARTIAL`, `INSUFFICIENT_MATERIAL`, `FAILED_RUNTIME` (rules §24).

`ReconstructionProvenance` (immutable, never in semantic identity): `request_id`, `contribution_ids` (sorted), `contributors` (sorted by canonical JSON), `source_refs` (union of material `source_refs`, sorted, unique), `derived_from_material_ids` (MATERIAL refs used by any support or endpoint, sorted, unique), `derived_from_item_ids` (ITEM refs used, sorted, unique), `diagnostics` (tuple[str, ...], non-semantic).

`ReconstructionResult` (immutable):

| Field | Type | Identity |
|---|---|---|
| `schema_version` | `"m33.result.v1"` | yes |
| `reconstruction_id` | HEX64 (§19) | — |
| `request_id` | HEX64 | yes |
| `status` | ReconstructionStatus | yes |
| `items` | tuple[ReconstructionItem, ...] sorted by `item_id` | yes (with supports and status) |
| `relations` | tuple[ReconstructionRelation, ...] sorted by `relation_id` | yes (with supports) |
| `issues` | tuple[ReconstructionIssue, ...] sorted by canonical JSON | yes |
| `provenance` | ReconstructionProvenance | NO |
| `effects` | ReconstructionEffectsContract | NO (constant) |

Direct construction violating §24 rules → `INVALID_RECONSTRUCTION_RESULT`. No field implies truth or promotion. `RECONSTRUCTED != VERIFIED`; `RECONSTRUCTED != TRUE`.

## 19. Identity

Reuses M32 canonical JSON exactly (M32 spec §15, RFC 8785 numbers, NFC, sorted keys, compact separators, UTF-8); `id = lowercase_hex(SHA256(UTF8(CANONICAL_JSON(preimage))))`, no prefix. No second canonicalization system. `DATUM(d)` = the M32 §16 canonical object of datum `d`.

- Item: `{"content": DATUM(content), "item_kind": item_kind, "schema_version": "m33.item.v1"}`
- Relation: `{"relation_kind": k, "schema_version": "m33.relation.v1", "source": {"kind": s.kind, "ref_id": s.ref_id}, "target": {"kind": t.kind, "ref_id": t.ref_id}}`
- Request: `{"bounds": {"max_derivation_depth": d, "max_items": i, "max_relations": r, "max_supports_per_unit": s}, "inspection_scope_ref": ref (omitted if absent), "materials": [{"datum": DATUM, "material_id": id, "source_refs": [...]}, ...sorted by material_id], "reconstruction_kind": k, "schema_version": "m33.request.v1"}`
- Support canonical object: `{"derivation": label (omitted if absent), "kind": kind, "refs": [{"ref_id": id, "ref_kind": kind}, ...sorted]}`
- Issue canonical object: `{"detail": label (omitted if absent), "issue_kind": kind, "subject_ids": [...sorted]}`
- Result: `{"issues": [issue objects sorted by their canonical JSON], "items": [{"integration_status": s, "item_id": id, "supports": [support objects sorted by canonical JSON]}, ...sorted by item_id], "relations": [{"relation_id": id, "supports": [...]}, ...sorted by relation_id], "request_id": id, "schema_version": "m33.result.v1", "status": status}`

Excluded from every preimage: wall clock, PID, host path, memory address, provider latency, request/call ids, execution ordering, machine identity, contributor identity, `context_origin`, diagnostics, provenance. Source evidence references are semantic only as support refs. `PROVENANCE != SEMANTIC_IDENTITY`.

## 20. Canonical ordering and copy safety

Materials by `material_id`; support refs by (`ref_kind`, `ref_id`); supports, issues, contributors by canonical JSON; items by `item_id`; relations by `relation_id`; `source_refs`, `subject_ids`, `derived_from_*`, `contribution_ids` by code point, deduplicated. Caller insertion order, set order, scheduling and completion order never matter. All objects are deep-copied/frozen at construction; caller mutation never changes values or ids.

## 21. Duplicates, aggregation, no fusion

- Two items with the same `item_id` are the same item: one item in the result, supports = sorted union. Integration status: equal → kept; different → `UNDETERMINED` + `AMBIGUOUS_RECONSTRUCTION` (§17).
- Two relations with the same `relation_id` merge likewise (union of supports).
- Different ids are never merged (no fuzzy fusion, no LLM merge, no similarity). `MULTIPLE_RECONSTRUCTIONS != AUTOMATIC_SINGLE_TRUTH`.
- Aggregation never changes a support's kind; more evidence is not verification.

## 22. Entry point and lifecycle

Single public V1 surface: `reconstruct(request: ReconstructionRequest, contributions: tuple[ReconstructionContribution, ...]) -> ReconstructionResult`. Synchronous, no background work, no recursion beyond the finite derivation check.

Order. Steps 1–8 are structural validation: they only raise `ReconstructionValidationError`, the first failure determines the error, nothing is produced and no side effect occurs. They apply to ALL supplied contributions, whatever their `ContributionStatus`.

1. `request` is a `ReconstructionRequest` and every contribution a `ReconstructionContribution` (else `INVALID_RECONSTRUCTION_REQUEST` / `INVALID_CONTRIBUTION`).
2. Contribution ids unique (`INVALID_CONTRIBUTION`).
3. Pre-merge integration-status check: every contributed `ReconstructionItem` carrying `ABSENT_IN_SCOPE`, in every contribution, is checked individually against §11; if the request has no `inspection_scope_ref` → `INVALID_INTEGRATION_STATUS`. This happens before any merge, so a later merge into `UNDETERMINED` can never hide an invalid `ABSENT_IN_SCOPE`.
4. Collect items/relations/issues of `COMPLETED` contributions; merge per §21. (`FAILED_RUNTIME` contributions carry no items or relations — enforced at their construction, §15.)
5. Bounds: distinct items ≤ `max_items`, distinct relations ≤ `max_relations`, supports per merged unit ≤ `max_supports_per_unit` (`RECONSTRUCTION_BOUND_EXCEEDED`).
6. Resolve every support ref (§13) (`INVALID_SUPPORT_REFERENCE`).
7. Derivation graph: item → items referenced by its INFERENCE supports; any cycle → `DERIVATION_CYCLE`; longest chain > `max_derivation_depth` → `RECONSTRUCTION_BOUND_EXCEEDED`. Descriptive relation cycles are allowed.
8. Resolve relation endpoints (`INVALID_RELATION_REFERENCE`).
9. Only now, after steps 1–8 succeeded: evaluate contribution statuses; if any contribution is `FAILED_RUNTIME`, status is `FAILED_RUNTIME` (§24 rule 1).
10. Derive engine issues (§17) and status (§24).
11. Compute identities (§19) and provenance.
12. Return the immutable result.

Precedence (frozen): a validation defect anywhere in the request or in any contribution always raises its `ReconstructionValidationError`, even if some other contribution is `FAILED_RUNTIME`; `FAILED_RUNTIME` is reachable only after structural validation has succeeded.

- `VALIDATION_ERROR_PRECEDES_FAILED_RUNTIME=YES`
- `FAILED_RUNTIME_SUPPRESSES_VALIDATION_ERRORS=NO`
- `FAILED_CONTRIBUTION_SKIPS_OTHER_VALIDATION=NO`
- `ABSENT_IN_SCOPE_VALIDATED_PRE_MERGE=YES`; `MERGE_CAN_HIDE_INVALID_ABSENT_IN_SCOPE=NO`

An unexpected internal exception during steps 9–11 yields a result with `status=FAILED_RUNTIME` (§24); it is not propagated.

## 23. Error taxonomy (sole origins)

| Code | Origin |
|---|---|
| `INVALID_MATERIAL` | ReconstructionMaterial construction |
| `INVALID_RECONSTRUCTION_REQUEST` | ReconstructionRequest / ReconstructionBounds construction; lifecycle step 1 (request type) |
| `INVALID_DERIVATION` | ReconstructionSupport / SupportRef construction (shape) |
| `INVALID_RECONSTRUCTION_ITEM` | ReconstructionItem construction |
| `INVALID_RECONSTRUCTION_RELATION` | ReconstructionRelation / Endpoint construction |
| `INVALID_RECONSTRUCTION_ISSUE` | ReconstructionIssue construction |
| `INVALID_CONTRIBUTION` | ReconstructionContribution / Contributor construction (including any item or relation inside a `FAILED_RUNTIME` contribution); lifecycle steps 1–2 |
| `INVALID_EFFECTS_CONTRACT` | ReconstructionEffectsContract construction |
| `RECONSTRUCTION_BOUND_EXCEEDED` | lifecycle steps 5 and 7 (depth) |
| `INVALID_SUPPORT_REFERENCE` | lifecycle step 6 |
| `DERIVATION_CYCLE` | lifecycle step 7 |
| `INVALID_RELATION_REFERENCE` | lifecycle step 8 |
| `INVALID_INTEGRATION_STATUS` | lifecycle step 3, per contributed item, before merge |
| `INVALID_RECONSTRUCTION_RESULT` | direct ReconstructionResult construction |

Validation errors ≠ statuses ≠ FAILED_RUNTIME. M32 errors raised while building M32 datums keep their M32 codes.

## 24. Status rules

Evaluated in order:

1. `FAILED_RUNTIME` if, after lifecycle steps 1–8 succeeded, any contribution is `FAILED_RUNTIME` or an unexpected internal failure occurred in steps 9–11. This applies even if other contributions are `COMPLETED` (fail-closed: their items are discarded). Then `items=()`, `relations=()`, `issues=()`; diagnostics in provenance only.
2. `INSUFFICIENT_MATERIAL` if zero items result (e.g. empty materials, or contributions produced no item). Issues are kept.
3. `PARTIAL` if at least one issue of kind `UNRESOLVED_REFERENCE`, `AMBIGUOUS_RECONSTRUCTION` or `INSUFFICIENT_MATERIAL` exists.
4. `RECONSTRUCTED` otherwise (`CONTRADICTORY_SUPPORT` issues may be present).

`PARTIAL` means valid items exist but some requested aspect remains unresolved, ambiguous or incomplete; it does not mean low confidence, false, failed or unverified truth. `PARTIAL != COMPLETE`; `INSUFFICIENT_MATERIAL != UNKNOWN`; `FAILED_RUNTIME != FALSE`. Malformed input never yields a status (§23); insufficient material never raises.

## 25. B6 boundary

M33 does not retrieve context, select visibility, assemble B6 context packets or own query-aware projection. It receives already admissible bounded material. `ARM_CONTEXT_EXTRACTION_OWNERSHIP=NO`; `B6_CONTEXT_ASSEMBLY_REMAINS_OWNER=YES`.

## 26. B7 boundary

M33 may record a B7 role reference in contributor provenance. It defines no role semantics, no role registry, no competence- or utility-based selection, and grants no role authority. `ARM_MAY_USE_COGNITIVE_ROLES=YES`; `ARM_MAY_DEFINE_NEW_ROLE_AUTHORITY=NO`.

## 27. B8 boundary — ReconstructionItem vs B8 candidate (N2)

`ReconstructionItem != B8 candidate/promotion object.`

- The M33 public API contains no type, field, enum or function named `Candidate` or `*Candidate*`, and none reusing B8 claim/transition vocabulary (e.g. `KnowledgeClaim`, `ClaimState`, `TransitionRequest`).
- No implicit conversion, shared enum, shared lifecycle or automatic submission to B8.
- M33 never imports or calls B8 transition/promotion functions.
- A future explicit downstream adapter may translate eligible M33 output for B8 review; that adapter is outside M33 V1.
- « Reconstruction candidate » remains a conceptual doctrine phrase only; the runtime term is `ReconstructionItem`.

`RECONSTRUCTION_ITEM_IS_B8_CANDIDATE=NO`; `RECONSTRUCTION_ITEM_AUTO_CONVERTS_TO_B8=NO`; `B8_CANDIDATE_NAMESPACE_REUSED=NO`; `B8_PROMOTION_REMAINS_EXTERNAL=YES`; `N2_RESOLVED_BY_SPEC=YES`.

## 28. B9 boundary

M33 may reference an existing CognitivePath identifier only as an OPAQUE_ID (source ref or contributor provenance). It never constructs an object presented as a canonical B9 CognitivePath. `ReconstructionRelation != CognitivePath`; reconstruction history != PathHistory.

## 29. Memory / B10 boundary

`MEMORY_WRITE=False`; `GRAPHITI_WRITE=False`; `DURABLE_RECONSTRUCTION_STORE=NO`. Output may be memory-eligible reconstruction content; `ReconstructionItem != memory candidate object`; M33 exposes no MemoryCandidate type. Persistence is B10's.

## 30. B11 / B12, Shazam, SENS-14, seven fluxes

- M33 V1 owns no MicroUtility, calibration, competence, activation threshold, spawn/despawn, fast path, capability admissibility or selection.
- Shazam Cognitif remains a specialized periphery descendant; M33 V1 does not import it; `periphery/.../05_SHAZAM_COGNITIF/` is not modified.
- `SENS14_STATUS=REFERENCE_ONLY`; M33 implements its own EVIDENCE/INFERENCE distinction; `M33_DOES_NOT_RETROACTIVELY_CLOSE_SENS14=YES`.
- `SEVEN_FLUXES_CANONICAL_FOR_M33=NO`; `SEVEN_FLUXES_RUNTIME_TYPES_IN_M33=0`; `SEVEN_FLUXES_RELEVANT_FOR_M34=YES`.

## 31. Authority

`COGNITION != AUTHORITY`; `ARM_AUTHORITY=ADVISORY_ONLY`. M33 cannot authorize action or capability, promote knowledge, write memory, decide world truth, mutate Binder / kernel / KX108, or emit ACT. `EMITS_ACT=False`; `B8_MUTATION=False`; `BINDER_MUTATION=False`; `KERNEL_MUTATION=False`; `KX108_MUTATION=False`; `ONE_FINAL_ACTION_AUTHORITY=KX108_ONLY`.

## 32. Human report projection (non-normative)

A downstream projection may label results: solid (items with EVIDENCE support and `ALREADY_INTEGRATED`), evoked (`EVOKED_NOT_LOCKED`), forgotten/latent (`ABSENT_IN_SCOPE` or INFERENCE-only items), open questions (issues). `HUMAN_REPORT_IS_PROJECTION=YES`; `HUMAN_REPORT_IS_RUNTIME_TRUTH=NO`; no report generator or LLM is part of M33 V1.

## 33. Foundation boundary for runtime work

`M33_SPEC_BASE` = the commit at which this spec is independently certified (recorded in that certification). For all M33 runtime work: `git diff --name-only M33_SPEC_BASE..HEAD -- <PROTECTED_PATHS>` must be empty, with `PROTECTED_PATHS` taken from seal §4 and the sentinel targets (as in M32 spec §35). `python scripts/foundation_sentinel.py` must pass.

## 34. Public surface collision

Public (non-underscore) top-level names defined under `app/reconstruction/m33/` must not intersect the public names (AST rule of M32 spec §35) of B7, B8, B9 (`app/cognition/b7`, `app/knowledge/b8`, `app/cognition/b9`), of B6 (`app/harness/state_explicit`) or of M32 (`app/primitives/m32`); and must not contain `Candidate` as a substring. Current symbol sets are discovered from the repository when RED is written.

## 35. Out of scope

M34 Biology Patterns; seven-fluxes runtime; COMOS; cross-domain transfer; long-lived identity; version/supersession; point-in-time; B10 durable memory; world model; B11 calibration; B12 capability/admissibility/selection; B13 realized-state reconciliation; Forge; Binder/KX108 action authority; provider selection; autonomous agents; external IO; persistent Graphiti; training/fine-tuning.

## 36. Requirement matrix R1–R24

| ID | Requirement | Positive oracle | Negative oracle | Expected failure if violated | § |
|---|---|---|---|---|---|
| R1 | Source provenance / N1 attribution | this spec §3 contains levels A/B/C and the « without retroactively attributing » sentence | search §3: no claim that the earliest ARM source defines trajectories/paths | doc audit fails | 3 |
| R2 | M32-typed bounded input | material with M32 datum constructs; request with materials constructs | non-datum payload → `INVALID_MATERIAL`; duplicate material ids → `INVALID_RECONSTRUCTION_REQUEST` | wrong/no error | 9, 10 |
| R3 | ReconstructionItem / N2 | item constructs, `item_id` HEX64 | module public names contain no `Candidate`; no B8 import in `app/reconstruction/m33` (AST) | name or import found | 14, 27 |
| R4 | Evidence vs inference | EVIDENCE→MATERIAL and INFERENCE→ITEM supports construct | EVIDENCE→ITEM and INFERENCE with no refs → `INVALID_DERIVATION`; kind preserved after aggregation | wrong code / kind changed | 13, 21 |
| R5 | Scope-bounded integration status | `ABSENT_IN_SCOPE` accepted when request has `inspection_scope_ref` | same without scope → `INVALID_INTEGRATION_STATUS`; enum has exactly 4 values; B2 oracle: request without `inspection_scope_ref`, contribution A has item X `ABSENT_IN_SCOPE`, contribution B has the same item X `EVOKED_NOT_LOCKED` → `INVALID_INTEGRATION_STATUS` raised (no result, no `UNDETERMINED` merge) | accepted, or merged into UNDETERMINED | 11, 12, 22 |
| R6 | Relations without mandatory graph | relation constructs; relation cycle A→B→A accepted | self-relation → `INVALID_RECONSTRUCTION_RELATION`; unknown endpoint → `INVALID_RELATION_REFERENCE`; no graph type exported | accepted / graph present | 14, 22 |
| R7 | Contradiction preserved | `arm.contradicts` relation → both items kept + `CONTRADICTORY_SUPPORT` issue, status `RECONSTRUCTED` | item count reduced or one item dropped | merge observed | 17, 24 |
| R8 | Unknown/unresolved preserved | contributor `UNRESOLVED_REFERENCE` issue → status `PARTIAL`, issue kept | issue dropped or status RECONSTRUCTED | wrong status | 17, 24 |
| R9 | Immutable deterministic result | two `reconstruct` calls with same inputs → equal `reconstruction_id`; attribute assignment fails | contributions in different order → same id | ids differ | 18, 20 |
| R10 | Canonical identity reuse | `item_id` equals externally computed SHA-256 of §19 preimage with M32 canonical JSON (incl. float `1e-7`) | — | mismatch | 19 |
| R11 | Ephemeral/provider excluded | same items via contributors with different provider/model/implementation → same `reconstruction_id` | patched clock → same ids | ids differ | 19 |
| R12 | Provenance normalization / derivation trace | provenance `source_refs`, `derived_from_*` sorted unique; `derived_from_item_ids` lists INFERENCE item refs | unsorted or duplicates present | mismatch | 18 |
| R13 | Bounded execution | bounds respected | `max_items` exceeded → `RECONSTRUCTION_BOUND_EXCEEDED`; depth exceeded → same code | accepted | 10, 22 |
| R14 | Explicit contributors | only supplied contributions' items appear | duplicate `contribution_id` → `INVALID_CONTRIBUTION`; no item appears without a contribution | extra items | 15, 22 |
| R15 | B6 ownership | — | AST: no import of `app.harness.state_explicit` assembly functions or retrieval in M33 package | import found | 25 |
| R16 | B7 ownership | role_ref recorded in provenance only | AST: no class/assignment redefining B7 public names; no role registry | found | 26, 34 |
| R17 | B8 ownership | — | AST: no import of `app.knowledge.b8` transition/promotion API; no `Candidate` names | found | 27 |
| R18 | B9 ownership | — | AST: no definition of `CognitivePath`/`PathHistory`/`FailedPath` in M33 | found | 28, 34 |
| R19 | No durable memory / Graphiti | effects all False | AST: no file/DB/network/Graphiti imports (`open` for write, `sqlite3`, `socket`, `requests`, graphiti) | found | 16, 29 |
| R20 | No world model / calibration / selection | — | no confidence/utility/score fields in any public type | found | 15, 30 |
| R21 | Validation/error taxonomy | each §23 code raised at its origin by a targeted bad input | wrong code or wrong phase | mismatch | 23 |
| R22 | Partial / insufficient / runtime failure | empty materials → `INSUFFICIENT_MATERIAL`; `FAILED_RUNTIME` contribution → `FAILED_RUNTIME` with empty items | malformed request never yields a status; insufficient never raises; B1 oracle: contribution A valid `FAILED_RUNTIME`, contribution B `COMPLETED` with an INFERENCE support referencing an unknown item id → `INVALID_SUPPORT_REFERENCE` raised, not a `FAILED_RUNTIME` result (same with a derivation cycle → `DERIVATION_CYCLE`) | mismatch, or FAILED_RUNTIME returned | 22, 24 |
| R23 | Effects/authority | `RECONSTRUCTION_EFFECTS` all False | constructing effects with True → `INVALID_EFFECTS_CONTRACT`; no ACT/KX108/Binder imports | accepted / found | 16, 31 |
| R24 | Public surface isolation | sentinel PASS; protected diff 0 | §34 collision check fires on a synthetic `class CognitivePath` | collision / diff | 33, 34 |

## 37. Adversarial matrix A1–A24

| ID | Bad implementation | Rejected by | Expected oracle |
|---|---|---|---|
| A1 | earliest ARM source credited with trajectory wording | R1 | doc audit §3 |
| A2 | public type named `Candidate`, confused with B8 | R3, R17 | name scan fails |
| A3 | inference marked as evidence | R4 | EVIDENCE→ITEM → `INVALID_DERIVATION` |
| A4 | item treated as verified | R3, R20 | no verified/truth field; enum has no VERIFIED |
| A5 | ABSENT without bounded scope | R5 | `INVALID_INTEGRATION_STATUS` |
| A6 | UNKNOWN collapsed into ABSENT/FALSE | R5, R8 | M32 UNKNOWN-derived contribution yields no ABSENT item; UNDETERMINED distinct |
| A7 | contradictory items auto-merged | R7 | both items present |
| A8 | fuzzy item/relation fusion | R9, R21 | different ids never merged |
| A9 | new B7 role semantics | R16 | AST check |
| A10 | direct B8 promotion | R17 | AST check |
| A11 | emits canonical CognitivePath | R18 | AST check |
| A12 | redefines PrimitiveResult semantics | R24 | collision check vs M32 names |
| A13 | registers a core primitive | R24 | M32 production registry untouched; no `register_type_spec` call in M33 package |
| A14 | writes Graphiti/durable memory | R19 | AST check; effects False |
| A15 | provider/model changes identity | R11 | same ids |
| A16 | wall clock changes identity | R11 | same ids |
| A17 | caller mutation changes identity | R9 | mutate nested source after construction → same ids |
| A18 | derivation cycle accepted | R13, R21 | `DERIVATION_CYCLE` |
| A19 | autonomous role/provider/primitive selection | R14 | items only from supplied contributions; `reconstruct` has no selector parameter |
| A20 | utility/confidence becomes authority | R20 | no such field |
| A21 | effect-capable handle reaches contributor | R23 | `reconstruct` signature takes only request and contributions; no callable invoked |
| A22 | emits ACT / mutates KX108/Binder | R23 | AST check; effects False |
| A23 | seven fluxes imported as types | R20, R24 | no `Flux*` public names |
| A24 | report label treated as runtime truth | R3, R20 | no report label field in result types |

## 38. RED test plan (not created here)

Layout: `tests/m33/{__init__.py, conftest.py, _harness.py, README.md, test_m33_r01_r06_red.py, test_m33_r07_r12_red.py, test_m33_r13_r18_red.py, test_m33_r19_r24_red.py, test_m33_foundation_boundary_red.py, test_m33_harness_selfcheck_red.py}`.

Rules: no skip-on-import, no xfail on missing runtime, no fake implementation, lazy runtime import inside test bodies (as in M32 RED) so that each requirement fails individually.

Mandatory positive controls: reference canonicalizer and SHA-256 recomputation (including RFC 8785 float vectors); non-vacuous test data; mutation probes really mutate; protected-diff and AST collision detectors fire on synthetic violations; evidence/inference oracle distinguishes two values; `Candidate` name detector fires on a synthetic bad module.

## 39. Readiness

`M33_SPEC_AUTHORED=YES`; `M33_SPEC_INDEPENDENTLY_CERTIFIED=NO`; `SAFE_FOR_M33_RED=NO` until an independent certification of this file passes; `M33_IMPLEMENTED=NO`; `M33_CLOSED=NO`.
