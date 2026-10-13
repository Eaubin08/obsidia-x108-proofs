# M37 Long-lived Identity — Doctrine V1

## 1. Status and authority

- Chapter: M37 — Long-lived Identity. Layer: cognition / pre-forge.
- Form: `M37_FORM=DOCTRINE_ONLY`. This document is the whole of M37 V1.
- Base: `COGNITIVE_FOUNDATION_V1=SEALED`, `FOUNDATION_REOPEN=NO`; M33, M34 and M36 CLOSED; M35 DEFERRED (evidence incomplete) and not a dependency.
- Basis: an independently certified M37 forensic, followed by independent certification of a recovered direct historical artifact (“Téléportation — Continuation, reconstruction ou copie ?”), followed by explicit project-owner decisions (scope = person/living entity continuity through transformation, form = doctrine-only, role = continuity hypothesis and evidence boundary).
- Normative hierarchy: `FOUNDATION_SEAL > CURRENT_CANONICAL_ARCHITECTURE > THIS_DOCTRINE > HISTORICAL_GENEALOGY`. Historical material never overrides this doctrine or anything above it.

M37 V1 does not solve identity. Its mission is to preserve the problem and its boundaries.

## 2. Historical problem

Historically, several distinct notions clustered under “identity”:

- technical identifiers (content hashes, UUIDs, domain keys) used by M32/M33/SENS and governed runtime;
- narrative or self identity (persona, story, authentication) used in agent registry and interface work;
- cross-domain structural identity (analogy, “same invariant”) partially owned by M36;
- visual or object permanence (VisualFingerprint, VisualInvariant, object persistence in world models);
- version and supersession (what replaces what, how states succeed one another);
- the core unresolved problem: whether a person or living entity undergoing transformation remains the same entity, and how to distinguish continuation from copy, replica, reconstruction or mere similarity.

M37 V1 owns exactly this last residual. Every other meaning is owned elsewhere or excluded (see boundary sections below).

The residual is not a solved problem. The certified historical artifact leaves the final identity criterion explicitly open: “tant que nous ne le savons pas, la téléportation reste une question ouverte”. M37 V1 preserves that openness without filling it.

## 3. Evidence levels

| Source | Evidence level | Use in M37 |
|---|---|---|
| Foundation seal (M37 milestone “Long-lived Identity” deferred) | CURRENT_CANONICAL | milestone existence only |
| M36 doctrine: `ANALOGY != IDENTITY` (closed) | CURRENT_CANONICAL | boundary M37 must not weaken |
| Temporal architecture: “transform identity and history prerequisites” (canonical, undefined) | CURRENT_CANONICAL | plausible relation to M37; meaning unresolved |
| M32/M33/SENS technical identifiers (content hash, UUID) | CURRENT_CANONICAL | boundary: technical id is not long-lived identity |
| “Téléportation — Continuation, reconstruction ou copie ?” (infographic 8, recovered direct historical artifact, independently certified 2026-10-13) | HISTORICAL_DIRECT, external | primary evidence for the continuity problem; subject = person/living entity |
| M37 forensic (independently certified) | INTERNAL_FORENSIC | confirms milestone existence; no primary source of its own |
| Historical genealogy: VisualFingerprint, VisualInvariant, LOCK/FLEX/IGNORE, InvariantDynamic, object permanence, ball identity, world-object identity | HISTORICAL_SECONDARY, unrecovered primary sources | excluded from V1; genealogy pending |
| Historical genealogy: Arbre de l’Identité, IDN, narrative self identity, authentication | HISTORICAL_SECONDARY | excluded from V1 scope |

No source defines a canonical identity criterion, a formal invariant, a preservation threshold, or a fork model. The recovered artifact explicitly leaves the final question open.

## 4. Canonical mission

M37 V1 defines the semantic boundary for representing whether a person or living entity may be continuous with an earlier instance through transformation, while preserving uncertainty and without treating similarity, copy, reconstruction, state equivalence or technical identity as sufficient proof of same identity.

M37 does not compute identity, prove identity, issue an identity verdict, or authorize action on the basis of identity.

## 5. Canonical subject

`M37_V1_SUBJECT=PERSON_OR_LIVING_ENTITY_CONTINUITY_THROUGH_TRANSFORMATION`

The recovered artifact is specifically about persons and living entities (human silhouettes, “téléporter une personne”, “système vivant”). V1 does not generalize to:

- all world objects or physical objects;
- all semantic entities or cognitive objects;
- all agents in the software sense;
- object permanence for non-living entities.

Future evidence may reopen or broaden scope. Until then, any extension beyond person/living entity requires a new forensic and explicit owner decision.

`M37_GENERIC_WORLD_OBJECT_IDENTITY=DEFERRED`
`M37_COGNITIVE_OBJECT_IDENTITY=DEFERRED`

## 6. Continuity problem — conceptual form

The recovered artifact directly poses the continuity problem as:

```
EARLIER SUBJECT A
  → TRANSFORMATION / INTERVAL
  → LATER SUBJECT B
  → CONTINUITY HYPOTHESIS
```

This is descriptive doctrine only. There are no runtime types, schemas, fields or identifiers corresponding to these labels.

The central question preserved from the artifact: what must be transferred from A to B for B to be the genuine continuation of A — matter, state, information, history, trajectory? M37 V1 does not answer this. It preserves the question.

## 7. Continuity vs copy vs reconstruction vs destruction

The recovered artifact directly and explicitly distinguishes:

- **CONTINUATION**: B is the same person as A, whose existence continues elsewhere.
- **COPY / REPLICA**: B may possess the same properties as A while having its own history.
- **RECONSTRUCTION**: B may be reconstructed from data about A without a direct causal link.
- **DESTRUCTION**: A has ceased to exist (physically or functionally).

These are historical conceptual distinctions preserved as doctrinal vocabulary. They are not runtime classes, enum values or schema fields.

Safe law frozen:

```
COPY != AUTOMATIC_CONTINUATION
```

M37 V1 does NOT claim `EVERY_COPY_IS_DIFFERENT_IDENTITY`. The recovered artifact retains open questions about the copy case (panel 7: can a perfect copy differ from the original only because of its causal history?). The safe law prohibits automatic promotion of copy to continuation; it does not resolve every copy case.

## 8. State equivalence

```
STATE_EQUIVALENCE != IDENTITY_PROOF
```

The recovered artifact states directly (panel 3): same initial state, but not necessarily same history. An equivalent reconstructed state does not establish continued identity. M37 V1 defines no quantitative state-equivalence semantics and no equivalence threshold.

## 9. Similarity and analogy

```
SIMILARITY != IDENTITY
ANALOGY != IDENTITY
```

No similarity score establishes identity. M36 boundary preserved and strengthened: a structural resemblance, however strong, does not prove that A and B are the same person or entity. `M36_REOPEN=NO`.

## 10. Role of M37

`M37_ROLE=CONTINUITY_HYPOTHESIS_AND_EVIDENCE_BOUNDARY`

M37 represents continuity hypotheses and possible evidence. It does NOT:

- declare identity truth;
- prove identity;
- authorize identity;
- promote identity into canonical knowledge;
- select action on the basis of identity;
- issue a sovereign or final identity verdict.

`M37_ASSERTS_FINAL_IDENTITY=NO`

## 11. Preservation dimensions — candidates only

The recovered artifact lists the following as candidate dimensions for continuation:

| Dimension | Artifact description | M37 V1 status |
|---|---|---|
| Organisation | Functional structure and internal relations | CANDIDATE |
| Information | All relevant data | CANDIDATE |
| Causal history | Past events and their links | CANDIDATE |
| Intentions / goals | Current tendencies and objectives | CANDIDATE |
| Physiological state | Current state of the living system | CANDIDATE |
| Internal time | Clocks, rhythms, internal continuities | CANDIDATE |

The artifact uses probabilistic language: “the more these elements are preserved, the higher the probability that B is the continuation of A.” This is graduated, not a threshold or requirement.

Frozen:

```
M37_IDENTITY_PRESERVING_CRITERIA=UNDEFINED
M37_IDENTITY_BREAKING_CRITERIA=UNDEFINED
```

No candidate above is a mandatory field, a required invariant, an identity test, or a threshold condition.

## 12. Causal continuity

The recovered artifact is internally tense on causal continuity:

- The vocabulary section implicitly presents causal link as necessary: COPY has its own history (different identity); RECONSTRUCTION has no direct causal link (not continuation).
- The takeaway bar states: “sans lien causal continu, il n’y a pas de ‘même personne’” — wording close to necessity.
- The final panel leaves the whole criterion explicitly open.

This tension is preserved as-is. Frozen:

```
CAUSAL_CONTINUITY_ROLE=CANDIDATE_ONLY
CAUSAL_CONTINUITY_NECESSARY=UNRESOLVED
CAUSAL_CONTINUITY_SUFFICIENT=NO
```

M37 V1 does NOT canonize “without causal continuity identity is impossible” as a doctrine law. That would resolve a question the artifact itself leaves open.

## 13. Temporal and trajectory continuity

The recovered artifact raises trajectory, interruption/resumption and internal time as relevant candidate dimensions (panels 8 and 9; internal time in the preservation list). These are candidates, not requirements.

```
M37_TEMPORAL_IDENTITY_CRITERION=UNDEFINED
M37_DOES_NOT_OWN_POINT_IN_TIME=YES
```

M39 owns Point-in-Time semantics. M37 acknowledges temporal continuity as a historically motivated candidate but does not reconstruct what was observed, known, believed or valid at historical time T.

## 14. Identity invariant

The recovered artifact raises the invariant concept as an open question: does a transformation T(A→B) exist such that I_A = I_B? The final question asks whether identity belongs to the invariant that remains through transformation. No invariant is defined.

```
M37_IDENTITY_INVARIANT=UNDEFINED
```

M37 V1 does not create: IdentityInvariant, InvariantId, a preservation algorithm, an identity equation, or an isomorphism criterion.

## 15. Copy / fork

The recovered artifact directly poses the fork case:

- Panel 4: if A remains alive after B appears, which is the original?
- Panel 11: if several B instances are created from A, can they be the same person?
- Scenario PARALLEL REPLICA: several B₁, B₂ instances → tree of parallel histories → inevitable divergence → identity = No.

No formal model is defined. Panel 11 ends: unique identity or multiple identity? — open.

```
M37_COPY_FORK_PROBLEM=ACKNOWLEDGED
M37_COPY_FORK_MODEL=NONE
M37_MULTIPLE_B_IDENTITY=UNRESOLVED
```

There is no fork runtime, fork engine, or parallel-replica registry.

## 16. Destruction

The recovered artifact is internally inconsistent on the destruction case:

- The scenario table labels TELEPORTATION (BY DESTRUCTION): continuity preserved = Yes.
- Panel 6 asks directly: does destruction of A change the identity of B? — open question.

This tension is preserved as-is. Frozen:

```
M37_DESTRUCTION_IDENTITY_EFFECT=UNRESOLVED
```

M37 V1 does not select either interpretation. Destruction is neither canonized as an identity break nor as identity-preserving.

## 17. Transform identity

Current temporal architecture contains the phrase “transform identity and history prerequisites” (canonical, undefined). The recovered artifact uses a transformation notation and addresses what is preserved through transformation.

```
M37_TRANSFORM_IDENTITY_RELATION=PLAUSIBLY_RELATED_BUT_UNRESOLVED
```

M37 V1 does not reinterpret the temporal contract. The relation remains plausible but unproven by current evidence. Future reconciliation requires independent evidence.

## 18. Self / agent identity — scope exclusions

M37 V1 concerns only continuity of a person or living entity through physical or structural transformation. It does NOT absorb:

- narrative self identity (personal story, self-representation);
- authentication identity (credentials, tokens, IDN, access control);
- persona identity (character or agent persona in UI or conversation);
- agent identifier identity (agent registry ID).

```
NARRATIVE_IDENTITY_IS_M37=NO
AUTHENTICATION_IDENTITY_IS_M37=NO
PERSONA_IDENTITY_IS_M37=NO
```

Historical constructs such as Arbre de l’Identité and IDN are not imported into M37 V1 unless those sources independently establish a continuity-through-transformation problem.

## 19. Technical identifiers

M32/M33/SENS/domain identifiers (content hashes, UUIDs, domain keys) do not establish M37 identity.

```
TECHNICAL_ID != LONG_LIVED_IDENTITY
```

Content hash equality, domain key match or UUID persistence does not establish that a person or living entity is continuous with an earlier instance.

## 20. Observation and representation

```
OBSERVATION != SUBJECT
REPRESENTATION != SUBJECT
```

A representation or observation is evidence and material about a subject, not the subject itself. M37 V1 does not derive generic world-object identity machinery from this boundary.

## 21. Identity hypothesis — epistemic status

An identity hypothesis is not automatically verified truth.

```
IDENTITY_HYPOTHESIS != VERIFIED
IDENTITY_HYPOTHESIS != PROMOTED
IDENTITY_HYPOTHESIS != TRUE
M37_PROMOTION=NONE
```

B8 owns knowledge promotion. M37 cannot accept a continuity hypothesis as knowledge, promote it, or mark it verified. Any future continuity-derived candidate that enters promotion machinery must cross the B8 boundary explicitly. This doctrine defines only that authority boundary, not an M37→B8 interface.

## 22. M38 boundary

M38 owns version / supersession: how states, representations or instances succeed one another.

M37 asks: is there continuity of the subject?
M38 asks: how do versions / states / representations supersede one another?

```
M37_DOES_NOT_OWN_VERSIONING=YES
```

## 23. M39 boundary

M39 owns Point-in-Time semantics: what was observed, known, believed or valid at historical time T.

M37 acknowledges trajectory and internal time as candidate dimensions without reconstructing historical valid state.

```
M37_DOES_NOT_OWN_POINT_IN_TIME=YES
```

## 24. B10 boundary

B10 owns durable persistence. M37 does not store identity history, continuity evidence or causal-link records.

```
M37_MEMORY_WRITE=NO
M37_IDENTITY_HISTORY_STORE=NONE
```

Persistence of any continuity evidence or causal history belongs to B10.

## 25. B11 / B12 / B8 boundaries

- B11: M37 defines no confidence calibration. `M37_CALIBRATION=NONE`. Any future calibrated identity-confidence mechanism belongs outside M37 V1.
- B12: M37 does not rank, score or select among continuity hypotheses. `M37_SELECTION=NONE`.
- B8: see §21. M37 defines the promotion boundary but not the interface.

## 26. M36 boundary

M36 CLOSED. `ANALOGY != IDENTITY`. No M36 reopen. M36 never establishes persistent or same-object identity. M37 owns the identity-continuity problem; M36 does not.

## 27. M33 boundary

A reconstructed candidate (M33 ARM) does not automatically inherit historical identity.

```
RECONSTRUCTION != IDENTITY_PROOF
M33_TO_M37_RUNTIME_INTERFACE=NONE
M37_TO_M33_RUNTIME_INTERFACE=NONE
```

## 28. World Model boundary

M37 is not a World Model implementation. Generic world-object continuity is deferred.

```
M37_WORLD_MODEL_RUNTIME_INTERFACE=NONE
```

World Model may later consume M37 concepts if explicitly justified through a new forensic.

## 29. VisualFingerprint family — excluded

The recovered teleportation artifact does not validate:

- VisualFingerprint;
- VisualInvariant;
- InvariantDynamic;
- LOCK/FLEX/IGNORE;
- object permanence for non-living entities.

These remain secondary genealogy pending primary evidence recovery.

```
VISUALFINGERPRINT_IS_M37_V1=NO
VISUALINVARIANT_IS_M37_V1=NO
INVARIANTDYNAMIC_IS_M37_V1=NO
OBJECT_PERMANENCE_IS_M37_V1=NO
```

## 30. Runtime, state and memory

```
M37_RUNTIME=NONE
M37_TESTS=NONE
M37_STATE=NONE
M37_EXECUTION=NONE
M37_RUNTIME_INPUT=NONE
M37_RUNTIME_OUTPUT=NONE
```

There is no identity resolver, identity matcher, continuity scorer, fingerprint matcher, fork engine, identity database, or transformation checker.

## 31. Authority

```
M37_AUTHORITY=NONE
EMITS_ACT=False
KERNEL_MUTATION=False
KX108_ONLY=UNCHANGED
IDENTITY != AUTHORITY
```

No action may be authorized, and no kernel state may be mutated, on the basis of a continuity hypothesis or identity representation.

## 32. Safety laws

```
SIMILARITY != IDENTITY
ANALOGY != IDENTITY
COPY != AUTOMATIC_CONTINUATION
STATE_EQUIVALENCE != IDENTITY_PROOF
TECHNICAL_ID != LONG_LIVED_IDENTITY
RECONSTRUCTION != IDENTITY_PROOF
IDENTITY_HYPOTHESIS != VERIFIED
IDENTITY_HYPOTHESIS != PROMOTED
IDENTITY_HYPOTHESIS != TRUE
M37_IDENTITY_INVARIANT=UNDEFINED
M37_IDENTITY_PRESERVING_CRITERIA=UNDEFINED
M37_IDENTITY_BREAKING_CRITERIA=UNDEFINED
IDENTITY != AUTHORITY
OBSERVATION != SUBJECT
REPRESENTATION != SUBJECT
CAUSAL_CONTINUITY_NECESSARY=UNRESOLVED
CAUSAL_CONTINUITY_SUFFICIENT=NO
```

Why a doctrine-only milestone is useful: it preserves the historically grounded problem — whether a person or living entity remains continuous through transformation — while preventing that problem from being silently resolved by analogy, state equivalence, technical identity, or runtime heuristics. M37 is the semantic and safety boundary for any future identity-continuity reasoning.

## 33. Non-goals

M37 is not an identity resolver, identity matcher, continuity scorer, fingerprint matcher, fork engine, identity database, narrative-self system, authentication system, persona system, agent-registry system, versioning layer, Point-in-Time system, memory layer, knowledge-promotion layer, world-object permanence system, calibration layer, selection layer, authority layer, or action layer.

## 34. Explicit deferrals

The following questions are NOT silently resolved by M37 V1. They require independent primary evidence or an explicit architecture requirement before any doctrine update:

1. Generic physical / world-object identity (non-living entities).
2. Cognitive object identity.
3. Identity invariant: definition, type, preservation algorithm.
4. Preservation criterion: which dimensions are required and at what threshold.
5. Identity-breaking criterion: what definitively breaks identity.
6. Causal continuity necessity: whether absence of causal link is always identity-breaking.
7. Copy / fork semantics: formal model for parallel replicas and divergent histories.
8. Multiple-B identity: whether several instances from A can share identity.
9. Destruction identity effect: whether destruction of A changes identity of B.
10. VisualFingerprint, VisualInvariant, InvariantDynamic, object permanence: require primary evidence recovery.
11. Typed continuity relation: any formal typing of the A→B relation.
12. Runtime identity resolver: if and when a resolver is needed, and who owns it.
13. Transform-identity reconciliation with the temporal doctrine phrase “transform identity and history prerequisites”.

## 35. Reopen protocol

M37 may be reopened only explicitly, through a new forensic and doctrine cycle with independent certification, when future evidence or architecture establishes one or more of:

- generic world-object scope with primary evidence;
- typed continuity evidence;
- a formally defined identity relation;
- a defined invariant;
- preservation or break rules grounded in primary evidence;
- a fork model;
- a runtime consumer requiring typed M37 objects;
- an identity resolver with an explicit architecture justification.

Doctrine-only M37 must never evolve silently into a runtime.

## 36. Closure model

`M37_CLOSURE_MODEL=RESTRICTED_DOCTRINE_ONLY_V1`

Lifecycle: forensic → independent forensic certification → primary evidence recovery → direct artifact reconciliation → independent artifact certification → owner decisions → restricted doctrine → independent doctrine certification → CLOSED.

There is no spec, RED, GREEN or runtime certification phase unless an explicit reopen occurs.

## 37. Canonical invariants

```
M37_FORM=DOCTRINE_ONLY
M37_V1_SUBJECT=PERSON_OR_LIVING_ENTITY_CONTINUITY_THROUGH_TRANSFORMATION
M37_ROLE=CONTINUITY_HYPOTHESIS_AND_EVIDENCE_BOUNDARY
M37_ASSERTS_FINAL_IDENTITY=NO
M37_GENERIC_WORLD_OBJECT_IDENTITY=DEFERRED
M37_COGNITIVE_OBJECT_IDENTITY=DEFERRED
M37_IDENTITY_INVARIANT=UNDEFINED
M37_IDENTITY_PRESERVING_CRITERIA=UNDEFINED
M37_IDENTITY_BREAKING_CRITERIA=UNDEFINED
M37_TEMPORAL_IDENTITY_CRITERION=UNDEFINED
CAUSAL_CONTINUITY_ROLE=CANDIDATE_ONLY
CAUSAL_CONTINUITY_NECESSARY=UNRESOLVED
CAUSAL_CONTINUITY_SUFFICIENT=NO
M37_COPY_FORK_PROBLEM=ACKNOWLEDGED
M37_COPY_FORK_MODEL=NONE
M37_MULTIPLE_B_IDENTITY=UNRESOLVED
M37_DESTRUCTION_IDENTITY_EFFECT=UNRESOLVED
M37_TRANSFORM_IDENTITY_RELATION=PLAUSIBLY_RELATED_BUT_UNRESOLVED
NARRATIVE_IDENTITY_IS_M37=NO
AUTHENTICATION_IDENTITY_IS_M37=NO
PERSONA_IDENTITY_IS_M37=NO
VISUALFINGERPRINT_IS_M37_V1=NO
VISUALINVARIANT_IS_M37_V1=NO
INVARIANTDYNAMIC_IS_M37_V1=NO
OBJECT_PERMANENCE_IS_M37_V1=NO
M37_WORLD_MODEL_RUNTIME_INTERFACE=NONE
M33_TO_M37_RUNTIME_INTERFACE=NONE
M37_TO_M33_RUNTIME_INTERFACE=NONE
M37_DOES_NOT_OWN_VERSIONING=YES
M37_DOES_NOT_OWN_POINT_IN_TIME=YES
M37_RUNTIME=NONE
M37_TESTS=NONE
M37_STATE=NONE
M37_EXECUTION=NONE
M37_RUNTIME_INPUT=NONE
M37_RUNTIME_OUTPUT=NONE
M37_MEMORY_WRITE=NO
M37_IDENTITY_HISTORY_STORE=NONE
M37_PROMOTION=NONE
M37_CALIBRATION=NONE
M37_SELECTION=NONE
M37_AUTHORITY=NONE
EMITS_ACT=False
KERNEL_MUTATION=False
KX108_ONLY=UNCHANGED
IDENTITY != AUTHORITY
COGNITION != AUTHORITY
```
