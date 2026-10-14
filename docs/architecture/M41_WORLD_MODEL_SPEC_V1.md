# M41 World Model — Minimal Spec V1

## 1. Status and authority

- Chapter: M41 — World Model. Layer: cognition / pre-forge. Phase: spec authoring.
- Doctrine: `docs/architecture/M41_WORLD_MODEL_DOCTRINE_V1.md` (commit `3526fb8f`), independently certified PASS_WITH_NONBLOCKING_FINDINGS.
- Spec readiness: independently certified PASS_WITH_NONBLOCKING_FINDINGS for owner option A (minimal independent contract; no MMonde, F12 or F16 import), with a corrected target of three new types.
- Normative hierarchy: `FOUNDATION_SEAL > M32_SPEC (sealed substrate) > M41_DOCTRINE > THIS_SPEC`. This spec refines the doctrine; it never contradicts it. Where this spec is silent, the doctrine applies.
- Status after authoring: awaiting independent spec certification. No runtime, RED or GREEN is authorized by this document.

## 2. Scope

M41 V1 defines exactly three new immutable data types:

| Type | Purpose |
|---|---|
| `WorldMaterialRef` | an unresolved, declared reference to external world material |
| `WorldStateHypothesis` | one non-sovereign hypothesis about a presumed referent, backed by material references |
| `WorldHypothesisSet` | a set of at least two coexisting hypotheses about one presumed subject, without fusion or selection |

Supporting artefacts that are not new types: closed string constants for `hypothesis_kind` (§7), one read-only effects mapping (§13), and error codes carried by the built-in `ValueError` (§14). No enum class, exception class, registry, adapter or service is created.

`WorldModelView` (doctrine §18) is deferred: V1 does not need it.

Out of scope for V1: resolving references, importing or wrapping MMonde, F12, F16, SENS, Brody or GPS objects, revision, prediction, education, calibration, selection, persistence and any action.

## 3. Runtime location and dependencies

- Location: `app/world_model/` (new package), outside the sealed paths `app/cognition/`, `app/knowledge/b8/`, `app/harness/state_explicit/` and outside every foundation-sentinel target.
- Allowed imports: the Python standard library, and `app.primitives.m32` for `TypedCognitiveDatum` and for M32 canonical JSON and SHA-256 identity (§11).
- Forbidden imports: anything under `periphery/`, `app/cognition/`, `app/knowledge/`, `app/semantic/`, `app/reconstruction/`, any network, filesystem, database, Graphiti/Neo4j, Binder or KX108 module.
- Reuse of M32 canonicalization follows the M33 precedent: the M32 canonical JSON and hashing used by M33 are reused as substrate; no second canonicalization system is introduced, and no M32 file is modified.

## 4. Reused M32 primitives and their limits

| M32 primitive | Use in M41 V1 | Limit recorded |
|---|---|---|
| `TypedCognitiveDatum` | optional `content` of a hypothesis | validated, frozen, NFC-normalized, deep-copied (M32 §16, §19 phase B); its canonical object is content identity only |
| M32 canonical JSON (§15) and `lowercase_hex(SHA256(UTF8(...)))` | `hypothesis_id`, `set_id` | identity of canonical bytes, never identity of a world referent |
| `DatumTypeRef` | not used | not validated by M32; M41 does not rely on it |
| `PrimitiveProvenance` | not used | describes primitive execution lineage only, is not validated, and is shallowly frozen; it is never material provenance |
| `EffectsContract` | not used | has no `external_io` or `durable_state_write` dimension; M41 declares its own effects (§13) |

## 5. Common validation rules

- `NAMESPACED_TOKEN`: a string matching `^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$` (at least one dot; lowercase ASCII letters, digits, underscores).
- `OPAQUE_STRING`: a `str` (never `bytes` or another type) that is non-empty after NFC normalization, contains no NUL character, and is stored NFC-normalized.
- Booleans are never accepted where an integer or number is required (`type(v) is bool` is rejected).
- Every sequence field is stored as a `tuple`; any input list or tuple is copied; mutable elements are rejected.
- Mapping inputs are never accepted for sequence fields.

## 6. Type A — WorldMaterialRef

Fields:

| Field | Required | Rule |
|---|---|---|
| `ref_kind` | yes | `NAMESPACED_TOKEN` naming the material family, declared by the producer (e.g. `mmonde.world_state_v0`, `sens.event_ref`, `f16.real_image_observation_v0`, `gps.domain_measurement`) |
| `ref_id` | yes | `OPAQUE_STRING` |
| `source_label` | no | `OPAQUE_STRING` or absent; a declared label of the source |

Semantics:

- M41 never resolves, dereferences, fetches or imports the referenced material.
- There is no registry of allowed `ref_kind` values; any syntactically valid namespaced token is accepted. The example families are illustrative.
- A `WorldMaterialRef` proves neither that the referenced object exists, nor that it is reliable, nor its identity, nor that its provenance is valid. `source_label` is declared, never verified: `DECLARED_SOURCE != VERIFIED_SOURCE`.
- Two refs are equal iff their three fields are equal (absent `source_label` differs from any present value).

Canonical object: `{"ref_id": ref_id, "ref_kind": ref_kind}` plus `"source_label": source_label` when present.

## 7. Type B — WorldStateHypothesis

Fields:

| Field | Required | Rule |
|---|---|---|
| `hypothesis_kind` | yes | exactly `"STATE_OF_PRESUMED_REFERENT"` or `"REFERENT_IDENTITY"` |
| `presumed_referent_ref` | yes | a `WorldMaterialRef` |
| `content` | no | a `TypedCognitiveDatum` or absent |
| `material_refs` | yes | non-empty tuple of `WorldMaterialRef`, no duplicates; stored sorted by canonical JSON of each ref |
| `modality_label` | yes | `NAMESPACED_TOKEN`, declared by the source (e.g. `mmonde.observed`, `brody.predicted`, `f16.generated`) |
| `contradiction_refs` | no (default empty) | tuple of `WorldMaterialRef`, no duplicates; stored sorted by canonical JSON |
| `unknowns` | no (default empty) | tuple of `OPAQUE_STRING`, no duplicates; stored sorted by code point |
| `rank` | no | `int` ≥ 0 (not `bool`) or absent; descriptive only |
| `confidence` | no | finite `float` or `int` in [0, 1] (not `bool`) or absent; without authority |

Derived, read-only: `hypothesis_id` (§11).

Semantics:

- `STATE_OF_PRESUMED_REFERENT`: a hypothesis about the state of a referent presumed to be the one named by `presumed_referent_ref`.
- `REFERENT_IDENTITY`: a hypothesis about which referent the material concerns, or whether two referents are the same. It is never an identity decision.
- `presumed_referent_ref` is a candidate reference, never proof of existence or continuity.
- `content` is supplied by the source. M41 imposes no physical state schema and defines no `datum_type`, universal or otherwise; any `datum_type` valid under M32 is accepted as-is. A hypothesis may have no content when it has its references.
- `modality_label` is preserved exactly; M41 never interprets, converts or compares it (§10).
- Duplicate entries in `material_refs`, `contradiction_refs` or `unknowns` are rejected, not silently removed.
- `rank` and `confidence` are excluded from `hypothesis_id` and from member ordering (§8, §11).

## 8. Type C — WorldHypothesisSet

Fields:

| Field | Required | Rule |
|---|---|---|
| `subject_ref` | yes | a `WorldMaterialRef`: the presumed common subject, never proof of identity |
| `members` | yes | tuple of at least two `WorldStateHypothesis` |

Derived, read-only: `set_id` (§11).

Membership and order policy:

- Every valid member is kept. There is no deduplication by content, by similarity or by referent.
- Two members whose `hypothesis_id` values are equal are the same hypothesis; such an input is rejected (`M41_DUPLICATE_MEMBER`), never silently collapsed. Members whose `content` is identical but whose `material_refs`, `contradiction_refs`, `unknowns`, `modality_label`, `hypothesis_kind`, `presumed_referent_ref` or any `source_label` differ have different ids and are all kept.
- Two members that differ only by `rank` and/or `confidence` have the same `hypothesis_id` and are rejected as duplicates; ranking is not a way to multiply a hypothesis.
- `members` is stored sorted ascending by `hypothesis_id` (lowercase hex string order). The input order is not preserved; the stored order carries no meaning of priority, preference or truth.
- Members may disagree on `presumed_referent_ref` (identity hypotheses) or share it (state hypotheses); M41 resolves neither.

The type exposes no operation to add, remove, replace, merge, fuse, select, rank, choose a best member, resolve identity, supersede or promote. It has no truth field or method. A future revision is represented by constructing a new set; V1 implements no revision mechanism.

## 9. Identity boundaries

```
CONTENT_IDENTITY != WORLD_ENTITY_IDENTITY
SIMILARITY != IDENTITY_PROOF
STATE_EQUIVALENCE != IDENTITY_PROOF
HYPOTHESIS_ID != REFERENT_CONTINUITY_PROOF
DECLARED_SOURCE != VERIFIED_SOURCE
```

- Equal `content` (equal M32 canonical datum) never makes two hypotheses one, and never makes two referents one.
- Equal `presumed_referent_ref` values are equal references, not a demonstrated identity of the world entity.
- A `REFERENT_IDENTITY` hypothesis is a hypothesis; no field, method or derived value turns it into a decision.
- M37 keeps its restricted doctrine; M41 V1 creates no object-permanence or identity resolver.

## 10. Modality

```
OBSERVED != INFERRED
INFERRED != VERIFIED
PREDICTED != OBSERVED
SIMULATED != REALIZED
```

- There is no universal modality enum; `modality_label` is a namespaced token attached to the context of its declaring source.
- M41 guarantees only that a declared modality is preserved byte-for-byte and never converted, upgraded or replaced by any M41 operation.
- M41 cannot establish that a source qualified its observation correctly. A label such as `mmonde.observed` is a declaration, not a certification.

## 11. Identity computation

All identifiers reuse M32 canonical JSON (M32 spec §15: sorted keys, compact separators, NFC, RFC 8785 numbers, UTF-8) and are computed as `lowercase_hex(SHA256(UTF8(CANONICAL_JSON(preimage))))` — exactly 64 lowercase hexadecimal characters, no prefix. `REF(r)` is the canonical object of §6; `DATUM(d)` is the M32 §16 canonical object of datum `d`.

`hypothesis_id` preimage:

```
{
  "schema_version": "m41.world_state_hypothesis.v1",
  "hypothesis_kind": kind,
  "presumed_referent": REF(presumed_referent_ref),
  "content": DATUM(content)            (key omitted when content is absent),
  "material_refs": [REF(r), ...]        (stored order),
  "modality_label": modality_label,
  "contradiction_refs": [REF(r), ...]   (stored order),
  "unknowns": [u, ...]                  (stored order)
}
```

`set_id` preimage:

```
{
  "schema_version": "m41.world_hypothesis_set.v1",
  "subject": REF(subject_ref),
  "member_ids": [hypothesis_id, ...]    (stored order)
}
```

Excluded from every preimage: `rank`, `confidence`, input order, wall-clock time, process or machine identity, memory addresses. Identifiers are computed once at construction and exposed read-only. They are technical identities of canonical bytes; they never assert referent continuity, world identity or truth.

## 12. Immutability

- All three types are immutable after construction: assigning or deleting any attribute raises an error.
- Every collection field is a tuple built from a copy of the input; mutating the caller's original list afterwards changes nothing.
- `content` is stored as the M32 `TypedCognitiveDatum` instance, already frozen and deep-copied by M32.
- `hypothesis_id` and `set_id` are computed at construction and never recomputed; they cannot drift from the stored fields.
- Nothing is lazily resolved or cached after construction.

## 13. Effects and authority

The module exposes one read-only mapping (not a type) named `M41_EFFECTS`:

```
memory_write=False
emits_act=False
b8=False
binder=False
kernel=False
kx108=False
external_io=False
durable_state_write=False
```

These are declared effect dimensions; they authorize no connection. M41 does not claim that the M32 `EffectsContract` covers `external_io` or `durable_state_write`.

```
M41_ACTION_AUTHORITY=NONE
M41_MEMORY_WRITE=FALSE
M41_EXTERNAL_IO=FALSE
KX108_ONLY=YES
FOUNDATION_REOPEN=NO
```

Construction of any M41 object performs no I/O, no logging to files, no network access, no memory or B10 write, no B8 call and no action.

## 14. Error model

Validation failures raise `ValueError` whose message starts with one of these codes followed by `": "`:

| Code | Raised when |
|---|---|
| `M41_INVALID_REF` | `ref_kind` not a `NAMESPACED_TOKEN`, `ref_id` or `source_label` not an `OPAQUE_STRING`, or a non-`WorldMaterialRef` where one is required |
| `M41_INVALID_KIND` | `hypothesis_kind` outside the two constants |
| `M41_MISSING_MATERIAL` | `material_refs` empty |
| `M41_INVALID_MODALITY` | `modality_label` not a `NAMESPACED_TOKEN` |
| `M41_INVALID_CONTENT` | `content` present but not a `TypedCognitiveDatum` |
| `M41_DUPLICATE_ENTRY` | duplicate within `material_refs`, `contradiction_refs` or `unknowns` |
| `M41_INVALID_SCALAR` | invalid `rank` or `confidence` (type, range, bool, non-finite) |
| `M41_INVALID_COLLECTION` | a sequence field given as a mapping, set or other non-sequence, or containing a wrong element type |
| `M41_INSUFFICIENT_MEMBERS` | fewer than two members |
| `M41_DUPLICATE_MEMBER` | two members with equal `hypothesis_id` |

Validation never repairs, drops or reorders input silently, except the documented canonical sorting of §7 and §8.

## 15. Time and space

M41 V1 defines no time or space. Times, frames and spatial references stay inside the referenced source material. There is no global clock, frame conversion, universal trajectory, competing `TimeEnvelope`, or empirical validation of world state. Their absence does not block V1.

## 16. RED requirements

| Id | Requirement | Mandatory cases |
|---|---|---|
| R1 | Coexistence: incompatible hypotheses stay distinct members | two members with identical M32 `content` but different `material_refs` both remain; idem with different `source_label` only; idem with different `modality_label` only |
| R2 | No fusion or selection | the public surface of all three types contains no add/remove/replace/merge/fuse/select/best/resolve/supersede/promote/truth member (introspection test) |
| R3 | Identity unresolved | members with divergent `presumed_referent_ref` coexist; equal `presumed_referent_ref` does not merge members; a `REFERENT_IDENTITY` member exposes no decision |
| R4 | Preservation | materials, contradiction refs, unknowns, referent and modality are equal to the inputs (after canonical sorting) and survive mutation of caller-side lists |
| R5 | Modality | the stored `modality_label` equals the declared one byte-for-byte; no operation yields a different modality; no field or method converts a prediction, generation or simulation into an observation |
| R6 | No effects | `M41_EFFECTS` has exactly the eight keys, all `False`, and is read-only; constructing objects performs no file, network, memory or B10 write (filesystem and socket guards in the test); the module imports nothing forbidden (static import scan) |
| R7 | Order without authority | stored member order is ascending `hypothesis_id`; changing `rank` or `confidence` of any member changes neither its `hypothesis_id`, nor its position, nor `set_id`; a member with the highest `rank` or `confidence` is not made first |

Negative matrix:

| Case | Expected |
|---|---|
| empty or whitespace-only `ref_id`; `ref_kind` without a dot; uppercase `ref_kind`; `bytes` values | `M41_INVALID_REF` |
| unknown `hypothesis_kind` | `M41_INVALID_KIND` |
| empty `material_refs` | `M41_MISSING_MATERIAL` |
| `modality_label` not namespaced | `M41_INVALID_MODALITY` |
| `content` given as a dict | `M41_INVALID_CONTENT` |
| duplicate material ref, contradiction ref or unknown | `M41_DUPLICATE_ENTRY` |
| `rank=True`, `rank=-1`, `confidence=1.5`, `confidence=float("nan")` | `M41_INVALID_SCALAR` |
| sequence field given as a dict or set, or containing a plain string where a ref is required | `M41_INVALID_COLLECTION` |
| set with zero or one member | `M41_INSUFFICIENT_MEMBERS` |
| two identical members; two members differing only by `rank` | `M41_DUPLICATE_MEMBER` |
| `hypothesis_id` differs from an independently computed §11 preimage hash | identity test fails |
| attribute assignment or deletion after construction; mutation of the caller's list | error, or no effect on stored data |
| a contradiction ref dropped or altered after construction | preservation test fails |
| a `source_label` treated as verified (any field or method implying verification) | introspection test fails |

Tests are not written in this phase.

## 17. Future compatibility

Future adapters (MMonde, F12, F16, SENS, Brody, GPS, education / training, B11, B12, B13) can produce `WorldMaterialRef` values in their own `ref_kind` namespaces and build hypotheses and sets without M41 importing them. Each adapter is separate work requiring its own decision and certification.

Both future directions remain representable without being implemented:

```
EXPERIENCE → REPRESENTATION → HYPOTHESIS
HYPOTHESIS → PREDICTION → EXPERIENCE → REVISION
```

A prediction is a hypothesis whose source declares a predictive modality; a revision is a new set. V1 implements neither education, prediction nor revision.

## 18. Doctrine conformity

| Doctrine | Spec |
|---|---|
| OD-M41-1 no new root world ontology | no state schema, no `datum_type`, material is referenced only (§6, §7) |
| OD-M41-2 transient only, no memory write | §12, §13 |
| OD-M41-3 multiple hypotheses, no fusion, collapse or supersession | §8 |
| §7 two kinds of multiplicity | `hypothesis_kind` (§7, §9) |
| §8 no unified modality enum | `modality_label` opaque (§10) |
| §9–§10 no global clock or frame conversion | §15 |
| §18 vocabulary | `WorldStateHypothesis`, `WorldHypothesisSet` specified; `WorldModelView` deferred |

## 19. Lifecycle

```
DOCTRINE (certified)
  ↓
SPEC-READINESS (certified, option A)
  ↓
SPEC AUTHORING        ← this document
  ↓
INDEPENDENT SPEC CERTIFICATION
  ↓
RED → GREEN → INDEPENDENT RUNTIME CERTIFICATION
```

M41 is not closed by this document.
