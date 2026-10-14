# M41 World Model — Doctrine V1

## 1. Status and authority

- Chapter: M41 — World Model. Layer: cognition / pre-forge. Phase: doctrine authoring only.
- Base: `COGNITIVE_FOUNDATION_V1=SEALED`, `FOUNDATION_REOPEN=NO`; M32, M33, M34, M36, M37, M38, M39 and M40/B10 CLOSED; M35 DEFERRED (evidence incomplete) and not a dependency.
- Basis: the M41 forensic and cross-repository reconciliation reported by the project owner, and three explicit owner decisions (OD-M41-1, OD-M41-2, OD-M41-3, §4).
- Normative hierarchy: `FOUNDATION_SEAL > CURRENT_CANONICAL_ARCHITECTURE > OWNER_DECISIONS > THIS_DOCTRINE > EXTERNAL_EXPERIMENTAL > HISTORICAL`.
- Status after authoring: `DOCTRINE_AUTHORED_AWAITING_INDEPENDENT_CERTIFICATION`. M41 is not closed by this document.

M41 defines no runtime, spec, schema, class, enum, constructor, field set or deterministic identity. Every structural name below is doctrinal vocabulary only.

## 2. Evidence classes and sources

Each major statement in this doctrine is tagged with one class:

| Class | Meaning |
|---|---|
| `CURRENT_CANONICAL` | present on this branch and certified, or part of the foundation seal |
| `DIRECT_SOURCE` | a contract or document read directly, but not merged into this branch |
| `EXTERNAL_EXPERIMENTAL` | an experiment or precursor in an external repository |
| `HISTORICAL` | historical corpus or recovered artefact |
| `OWNER_DECISION` | explicit project-owner decision for M41 |
| `INFERENCE` | conclusion drawn by this doctrine from the above |
| `DEFERRED` | explicitly left open |

Sources consulted:

| Source | Where | Class | Status on this branch |
|---|---|---|---|
| Foundation seal; M32–M39 doctrines; M40/B10 doctrine and B10 V1 runtime | `docs/architecture/`, `app/knowledge/b10/` | CURRENT_CANONICAL | present |
| MMonde V0 contract (`WorldObservationV0`, `WorldStateV0`) | `docs/architecture/MMONDE_V0_CONTRACT.md`, `periphery/mmonde/contracts_v0.py`, commits `d28eb83d`, `f355f8a0` (origin `Eaubin08/obsidia-x108-proofs`) | DIRECT_SOURCE | not merged into this branch |
| F12 Situated World Dynamics V0 (`TimeEnvelopeV0`, `SpatialFrameRefV0`, `RelationStatusV0`, `TypedRelationV0`, `ContinuityStatusV0`, `TransitionV0`, `TrajectoryV0`) | `docs/architecture/SITUATED_WORLD_DYNAMICS_V0.md`, commit `af3dc668` | DIRECT_SOURCE, self-declared "IMPLEMENTED / VALIDATION REQUIRED" | not merged into this branch |
| F16 real image vision (`RealImageObservationV0`, `CandidateInterpretationV0`, `VisualPrimitiveV0`, `CaptureContextV0`, `ImageIntegrityReportV0`) | `periphery/vision/contracts_v0.py`, commits `f2986add`, `87cf931f` | DIRECT_SOURCE | not merged into this branch |
| Brody World Physique | `Eaubin08/brody-world-physique-obsidien-` (README read) | EXTERNAL_EXPERIMENTAL; its own status states "WORLD MODEL / GENERATOR / LEARNING RUNTIME NOT CONNECTED" | external |
| GPS Defense evidence pipeline | `Eaubin08/obsidia-gps-defense-` (README read) | EXTERNAL_EXPERIMENTAL / domain evidence, with an explicit claim matrix | external |
| SENS event and occurrence machinery (`OccurrenceClaim`, `OccurrenceDerivation`, `EventCandidate`, `EventRef`) | `app/semantic/lattice/` | CURRENT_CANONICAL | present |
| "Téléportation — Continuation, reconstruction ou copie ?" (infographic 8) | recovered artefact, as integrated by M37 | HISTORICAL | via M37 doctrine |

Only the README level of the Brody and GPS repositories was read for this doctrine; their deeper documents are not presented as verified here. The MMonde, F12 and F16 contracts were read directly from git history, but are not part of this branch; M41 references them as owners without assuming they are merged.

## 3. Why M41 exists

Several organs already produce situated material about an external world: MMonde observations and states, F12 time/space/relation/transition/trajectory contracts, F16 image observations and candidate interpretations, Brody perception and prediction experiments, GPS domain evidence, and SENS events and occurrences. Each keeps its own language, provenance, hypotheses and authority boundary.

M41 is the cognitive layer that composes references to this material into structured, situated, non-sovereign views of the presumed state of a world, without erasing the languages, provenances or boundaries of the contributing organs, and without becoming a new universal world engine. (OWNER_DECISION, INFERENCE)

It also prepares, without implementing, future interfaces with education and training (§17).

## 4. Owner decisions

### OD-M41-1 — Direct subject (OWNER_DECISION)

```
M41_DIRECT_SUBJECT=COGNITIVE_WORLD_MODEL_VIEW_OVER_EXISTING_WORLD_CONTRACTS
NO_NEW_ROOT_WORLD_ONTOLOGY=YES
WORLD_OBSERVATION_OWNER=MMONDE
WORLD_STATE_OWNER=MMONDE
TIME_FRAME_RELATION_TRANSITION_OWNER=F12
M41_ROLE=STRUCTURAL_COMPOSITION_OF_WORLD_STATE_HYPOTHESES_AND_VIEWS
```

M41 does not own a universal definition of a world object. It composes references to, and representations from, existing contracts.

Compatibility check: MMonde V0 declares `WorldStateV0` "readonly and distinct from memory/cognition" (`cognition_object=False`). M41 is a cognitive layer that refers to `WorldStateV0` instances; it does not turn them into cognition objects and does not redefine them. No incompatibility was found. (DIRECT_SOURCE, INFERENCE)

### OD-M41-2 — Persistence (OWNER_DECISION)

```
M41_V1_PERSISTENCE=TRANSIENT_ONLY
M41_OWNS_BACKEND=NO
M41_DIRECT_B10_WRITE=NO
M41_MEMORY_WRITE=NO
MEMORY != WORLD_MODEL
```

B10 durably keeps the governed epistemic history of B8; B10 V1 explicitly excludes world-model state (`WORLD_MODEL_STATE_B10_V1=NO`, M40 doctrine). M41 composes world views. Any later persistence of M41-derived structures requires a separate explicit contract. (CURRENT_CANONICAL, OWNER_DECISION)

### OD-M41-3 — Multiple hypotheses (OWNER_DECISION)

```
M41_MULTI_HYPOTHESIS=YES
AUTOMATIC_FUSION=NO
AUTOMATIC_COLLAPSE_TO_BEST_WORLD=NO
AUTOMATIC_SUPERSESSION=NO
RANKING != TRUTH
CONFIDENCE != AUTHORITY
```

Contradictory hypotheses may coexist. Each keeps its source, references, modality, uncertainty and contradictions. KX108 never becomes an arbiter of world truth.

No canonical source examined establishes an incompatibility with these three decisions; no HOLD was required.

## 5. Canonical mission

M41 represents structured, situated hypotheses about the state of an external world or modelled domain, built from governed references, without automatically turning those representations into truths, promoted knowledge, durable memory or action authorizations. (OWNER_DECISION)

Distinctions M41 keeps apart (doctrinal meanings only):

- referenced world: the external world or modelled domain the material is about;
- observation: a situated record produced by a source (MMonde `WorldObservationV0`, F16 `RealImageObservationV0`, domain observations);
- representation: any encoding of material in some modality;
- state: a candidate situation at a validity time (MMonde `WorldStateV0` is a "candidate reality");
- entity: what an observation or state is presumed to be about;
- relation: a typed link between referenced items (F12 `TypedRelationV0`);
- hypothesis: a proposed reading of what the world is or was like;
- prediction: a projected state not yet observed;
- transformation: a described change between states (F12 `TransitionV0`);
- uncertainty: what the sources declare as not known or imprecise;
- contradiction: incompatibility between material, kept visible;
- provenance: where each element comes from.

Where these notions are undefined in current contracts, M41 leaves them undefined; it creates no mechanism to fill the gap.

## 6. One referent, many views

```
ONE PRESUMED REFERENT
MANY OBSERVATIONS
MANY REPRESENTATIONS
MANY RELATIONS
MANY TEMPORAL VIEWS
MANY HYPOTHESES
NO AUTOMATIC FUSION
```

A phenomenon may be represented as an image, a geometry, a motion, a physical measurement, a position, a trajectory, a semantic event, a hypothesis, a projection or a simulation. These modalities do not automatically prove that a single referent exists.

`PRESUMED_COMMON_REFERENT != DEMONSTRATED_IDENTITY` (INFERENCE from M37 and MMonde `OBSERVATION != TRUTH`)

## 7. Identity boundary with M37

M37 V1 is restricted to the continuity of a person or living entity through transformation (`M37_V1_SUBJECT=PERSON_OR_LIVING_ENTITY_CONTINUITY_THROUGH_TRANSFORMATION`) and defers generic world-object identity (`M37_GENERIC_WORLD_OBJECT_IDENTITY=DEFERRED`). (CURRENT_CANONICAL)

M41 preserves:

```
SIMILARITY != IDENTITY_PROOF
STATE_EQUIVALENCE != IDENTITY_PROOF
COPY != AUTOMATIC_CONTINUATION
RECONSTRUCTION != IDENTITY_PROOF
ANALOGY != IDENTITY
OBSERVATION != SUBJECT
REPRESENTATION != SUBJECT
```

(CURRENT_CANONICAL: M36 §14, M37; HISTORICAL: infographic 8 as integrated by M37)

M41 distinguishes two kinds of multiplicity:

1. several hypotheses about the state of an entity presumed to be the same;
2. several hypotheses about whether it is the same entity at all.

M41 represents both kinds; it resolves neither. It defines no universal identity resolver and derives no object-permanence rule from the teleportation infographic or from experiments. An object that disappears and reappears may remain unresolved. `AUTOMATIC_IDENTITY_RESOLUTION=NO`.

## 8. Observed, inferred, predicted, simulated

```
OBSERVED != INFERRED
INFERRED != VERIFIED
PREDICTED != OBSERVED
SIMULATED != REALIZED
GENERATED != PHYSICAL_OBSERVATION
UNKNOWN != FALSE
CONTRADICTED != RESOLVED
```

These terms come from different layers (MMonde, F12, F16, Brody, B8). M41 does not unify them into one enum without a spec and proof of compatibility. (INFERENCE)

A hypothesis does not become true because it explains several observations. Explanatory coverage is not verification; promotion belongs to B8.

## 9. Time and frames

M41 reuses F12 temporal notions: F12 represents "multiple clocks without inventing missing timestamps". (DIRECT_SOURCE)

M41 keeps apart: event time, observation time, reception time, processing time, model time, prediction horizon, M39 epistemic revision, and B10 durable commit.

```
WORLD_TIME != EPISTEMIC_REVISION
WORLD_TIME != MEMORY_COMMIT_TIME
OBSERVED_AT != VALID_AT
RECEIVED_ORDER != WORLD_ORDER
RECORDED_ORDER != WORLD_ORDER
SERIALIZATION_ORDER != CAUSAL_ORDER
```

(CURRENT_CANONICAL: M38/M39 order laws and the no-universal-clock doctrine; DIRECT_SOURCE: MMonde `observed_at` vs `valid_at`, F12 `TEMPORAL != CORRELATED != DERIVED != CAUSAL_ASSERTED != CAUSAL_PROVEN`)

No new global clock. No automatic conversion between temporal frames without a validated transformation.

## 10. Space and situated worlds

Existing frames are kept: image frame, camera frame, physical frame, GNSS frame, world frame, synthetic frame (F12 `SpatialFrameRefV0`, F16 `CaptureContextV0`, GPS domain frames). A position is interpretable only relative to an appropriate frame. (DIRECT_SOURCE, EXTERNAL_EXPERIMENTAL)

M41 does not impose spatial coordinates on intrinsically abstract domains. The World Model V1 stays structurally generic.

## 11. Transformations and trajectories

```
STATE != TRANSITION
TRANSITION != TRAJECTORY
TRAJECTORY != IDENTITY_PROOF
DESCRIBED_TRANSFORMATION != AUTHORIZED_ACTION
PREDICTED_CHANGE != OBSERVED_CHANGE
```

F12 remains owner of `TransitionV0`, `TrajectoryV0` and `ContinuityStatusV0` (continuity / drift / rupture); each is read-only with `decision_authority = KX108_ONLY`. M41 creates no second dynamics engine. (DIRECT_SOURCE)

## 12. Prediction and delta

Descriptive pattern, taken from the Brody experiments:

```
MODEL_STATE(t)
     ↓
PROJECTION(t+1)
     ↓
OBSERVATION(t+1)
     ↓
DELTA
```

Brody describes this loop (`WorldStateV0(t)` + transformation → `WorldStateProjectionV0(t+1)` → compare → `WorldStateDeltaV0` → `WorldExperienceCandidateV0`) and states that its world model, generator and learning runtime are not connected. (EXTERNAL_EXPERIMENTAL)

- M41 may represent a projection, an observation and a recorded delta as distinct items with their provenance.
- M41 does not compute deltas, evaluate predictions or learn from them.
- A delta is not a causal proof.
- Evaluation and learning from deltas belong to evaluation and education layers (§17); reconciliation with the realized state belongs to B13. M41 does not absorb B13.

## 13. Contradiction and competing hypotheses

Several incompatible representations may coexist. A contradiction never leads automatically to overwriting, fusion, selection of a truth, removal of provenance or epistemic promotion. Uncertainty and distinct sources are preserved. (OWNER_DECISION OD-M41-3; DIRECT_SOURCE: MMonde keeps `contradictions` and `unknowns`)

GPS evidence illustrates the structural property of refusing to replace an estimated state blindly with a contradicting observation, and of corroborating independent sources; its GNSS-specific laws stay in the GPS domain and are not universal M41 laws. (EXTERNAL_EXPERIMENTAL)

No arbitration engine is created in V1.

## 14. Canonical boundaries

| Owner | Responsibility | M41 position |
|---|---|---|
| B8 | epistemic promotion | M41 never promotes |
| B10 | governed durable persistence of B8 history | M41 never writes to B10 |
| M36 | cross-domain analogy | analogy is never identity for M41 |
| M37 | restricted continuity of identity | M41 never resolves identity |
| M38 | version and supersession of knowledge claims | M41 performs no automatic supersession |
| M39 | epistemic state at a logical revision | M41 does not reconstruct historical epistemic state |
| SENS | interpretation, events and occurrences (`OccurrenceClaim`, `OccurrenceDerivation`, `EventCandidate`, `EventRef`) | a SENS event is not a world state; M41 may refer to it |
| MMonde | world representation contracts | owner of observation and world state |
| F12 | time, space, relations, transitions, trajectories | owner of those contracts |
| F16 | real image observation and candidate interpretation | owner of image contracts |
| Brody | experiments in perception, prediction and learning | precursor, not canonical runtime |
| GPS | domain models and proofs for instrumented physics | domain owner |
| B11 | competence and calibration | M41 scores nothing |
| B12 | admissibility and selection | M41 selects nothing |
| B13 | reconciliation with realized state | deferred to B13 |
| KX108 | action authority | sole authority |

No integration runtime is created in this chapter.

## 15. Physical and abstract worlds

M41 is not a physics engine. Structurally, it may describe physical phenomena, digital environments, software systems, organizations, scientific domains and economic situations. The knowledge, laws and measurements specific to each remain in their domains (MMonde V0: "Domain-specific laws stay in domains"). M41 does not replace them with unverified universal abstractions. (DIRECT_SOURCE, INFERENCE)

## 16. Multiple scales

```
MICRO != MACRO
SCALE_CHANGE != SIMPLE_ZOOM
MACRO_STATE != AUTOMATIC_MICRO_STATE_RECOVERY
```

Moving between scales may require domain-specific hypotheses, laws, measurements or transformations. M41 V1 builds no multi-scale scientific engine. M34 multi-scale remains deferred and is not imported. (INFERENCE; CURRENT_CANONICAL for M34)

## 17. World model is not education

- M41: what the system represents about the world.
- Education / training: how the system acquires, confronts, corrects and improves its representations and competences.

Brody experiments are reusable precursors for education: prediction, error and surprise, comparison, occlusion, transfer, exploration, replay, spatial relations and multiple representations. (EXTERNAL_EXPERIMENTAL)

M41 is not a training engine. V1 defines no curriculum and no learning policy. `M41_LEARNING=NONE`.

## 18. Candidate vocabulary

The following terms are doctrinal vocabulary only. None is a class, schema, required field, constructor, method or deterministic identity.

**WorldModelView**

1. Definition: a transient, situated composition of references to existing world material (observations, states, relations, transitions) selected for a stated purpose and frame.
2. Why existing contracts are not enough: MMonde `WorldStateV0` groups observations as one candidate reality at one validity time; it does not express a cognitive view spanning several candidate states, frames and contributing organs.
3. MMonde: references MMonde objects; does not redefine or replace them.
4. M37: identity between referenced items is not established by inclusion in a view.
5. Authority: none.
6. Persistence: transient only.
7. V1 status: doctrinal vocabulary.

**WorldStateHypothesis**

1. Definition: one proposed reading of the state of a presumed referent or domain, with its sources, modality, uncertainty and contradictions.
2. Why existing contracts are not enough: `WorldStateV0` is a candidate reality; it does not represent several mutually incompatible readings kept side by side.
3. MMonde: may refer to one or more `WorldStateV0` instances as its material.
4. M37: may concern an entity presumed identical; that presumption is itself a hypothesis.
5. Authority: none; never true by construction.
6. Persistence: transient only.
7. V1 status: doctrinal vocabulary.

**WorldHypothesisSet**

1. Definition: a collection of coexisting world-state hypotheses about the same presumed referent or domain, with no ranking that implies truth.
2. Why existing contracts are not enough: no current contract expresses coexistence without fusion.
3. MMonde: none beyond the references held by its hypotheses.
4. M37: the set may contain hypotheses that disagree on identity; it resolves none.
5. Authority: none; no collapse to a best world.
6. Persistence: transient only.
7. V1 status: doctrinal vocabulary.

## 19. Invariants

| Invariant | Source |
|---|---|
| `MEMORY != WORLD_MODEL` | M40/B10 doctrine (OWNER_BOUNDARY); OD-M41-2 |
| `WORLD_MODEL != TRUTH` | MMonde `OBSERVATION != TRUTH`; foundation `MEMORY != TRUTH`; INFERENCE |
| `OBSERVATION != WORLD_STATE` | MMonde V0 (state groups observations as candidate reality) |
| `WORLD_STATE != IDENTITY_PROOF` | M37; INFERENCE |
| `PREDICTION != OBSERVATION` | Brody (EXTERNAL_EXPERIMENTAL); INFERENCE |
| `SIMULATION != REALIZATION` | INFERENCE; B13 boundary |
| `UNKNOWN != FALSE` | M32 foundation law |
| `CONTRADICTION != AUTOMATIC_FUSION` | OD-M41-3 |
| `ANALOGY != IDENTITY` | M36 |
| `RANKING != AUTHORITY` | OD-M41-3 |
| `CONFIDENCE != AUTHORITY` | OD-M41-3; foundation |
| `M41_MEMORY_WRITE=NO` | OD-M41-2 |
| `M41_EMITS_ACT=NO` | foundation; MMonde/F12 `allowed_to_act=False` |
| `M41_KERNEL_MUTATION=NO` | foundation |
| `KX108_ONLY=UNCHANGED` | foundation; MMonde/F12/F16 `decision_authority=KX108_ONLY` |

## 20. Non-goals and deferrals

Owned by another layer (not M41, ever): perception engine (F16, Brody, external models), physics and domain laws (domains, GPS), universal identity (M37 and its successors), durable memory backend (B10), truth resolution (no layer; B8 promotes), learning policy and curriculum (education), realized-state reconciliation (B13), action (KX108).

Deferred within M41: executable simulation, cross-repository wiring, any M41 runtime, persistence of derived world-model structures, world-model historical state (`WORLD_MODEL_HISTORICAL_STATE=DEFERRED`, M39).

## 21. Reopen protocol

M41 may evolve only explicitly, with justification, scope and suitable certification, when one of these occurs:

- new experimental evidence;
- a changed MMonde, F12 or F16 contract, or their merge into this branch;
- a new formal definition of continuity (M37 extension);
- a proposed persistence interface for derived world-model structures;
- an education interface;
- an extension toward a runtime;
- a new authority responsibility.

## 22. Lifecycle

```
FORENSIC
  ↓
CROSS-REPO RECONCILIATION
  ↓
OWNER DECISIONS
  ↓
DOCTRINE AUTHORING        ← this document
  ↓
INDEPENDENT CERTIFICATION
  ↓
M41 DOCTRINE CERTIFIED
  ↓
FUTURE RUNTIME READINESS
```

M41 is not closed by authoring. Whether a spec, RED and GREEN are needed will be decided separately, according to the runtime scope actually retained.

## 23. Canonical values

```
M41_DIRECT_SUBJECT=COGNITIVE_WORLD_MODEL_VIEW_OVER_EXISTING_WORLD_CONTRACTS
NO_NEW_ROOT_WORLD_ONTOLOGY=YES
WORLD_OBSERVATION_OWNER=MMONDE
WORLD_STATE_OWNER=MMONDE
TIME_FRAME_RELATION_TRANSITION_OWNER=F12
M41_V1_PERSISTENCE=TRANSIENT_ONLY
M41_OWNS_BACKEND=NO
M41_DIRECT_B10_WRITE=NO
M41_MEMORY_WRITE=NO
M41_MULTI_HYPOTHESIS=YES
AUTOMATIC_FUSION=NO
AUTOMATIC_COLLAPSE_TO_BEST_WORLD=NO
AUTOMATIC_SUPERSESSION=NO
AUTOMATIC_IDENTITY_RESOLUTION=NO
M41_LEARNING=NONE
M41_RUNTIME=NONE
M41_AUTHORITY=NONE
M41_EMITS_ACT=NO
M41_KERNEL_MUTATION=NO
KX108_ONLY=UNCHANGED
```
