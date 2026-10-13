# M33_ARM_RECONSTRUCTION_DOCTRINE_V1

Status: DOCTRINE (frozen before the M33 specification). Not a runtime specification. No implementation.

Normative hierarchy: `COGNITIVE_FOUNDATION_V1` seal > this doctrine > any later M33 specification. A later M33 specification may refine names, enums, serialization, identity preimage and error codes; it may not contradict this doctrine. This doctrine cannot override the sealed foundation.

Base: M32 CLOSED (runtime `app/primitives/m32/`, certified at `58f8da59`), `COGNITIVE_FOUNDATION_V1=SEALED`, `FOUNDATION_REOPEN=NO`.

## 1. Canonical decision

- `ARM_CANONICAL_EXPANSION=Agent Reconstruction Méthodique`
- `ARM_DOCTRINE_DECISION=HISTORICAL_MISSION_MODERN_SUBSTRATE`
- `HISTORICAL_ARM_MISSION_PRESERVED=YES`
- `M32_USED_AS_MODERN_TYPED_SUBSTRATE=YES`
- `ARM_CANONICAL_MISSION` = « Reconstruire méthodiquement une structure cognitive explicite, traçable et non souveraine à partir d'un matériau fragmenté, dispersé, implicite, incomplet, contradictoire ou désordonné. »

ARM is NOT canonically:

- `ARM_IS_SCHEDULER=NO`
- `ARM_IS_ROUTER=NO`
- `ARM_IS_ROLE_SYSTEM=NO`
- `ARM_IS_MEMORY=NO`
- `ARM_IS_WORLD_MODEL=NO`
- `ARM_IS_KNOWLEDGE_PROMOTION=NO`
- `ARM_IS_ACTION_AUTHORITY=NO`

## 2. Evidence base (forensic, 2026-10-13, read-only at `58f8da59`)

| Source | Location | Content | Weight |
|---|---|---|---|
| Historical prompt « PROMPT AGENT – ARM : Agent_Reconstruction_Méthodique » | outside repo (`obsidia-engine-proof-core/.../_doc_curation/...docx`) | scan raw conversation/notes; recover concepts, methods, implicit reasoning, forgotten ideas; classify « déjà intégré / évoqué non verrouillé / absent »; report solide / évoqué / oublié / latent / questions ouvertes; reconnect dissociated pieces; detect gaps and incoherence | origin of mission (historical, not runtime truth) |
| `arm_microagents` family, legacy card B13, components C346–C355 | outside repo (`OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1*.zip`, `family_specs/39_arm_microagents.spec.yaml`); referenced in repo inventories (commits `ea27f591`, `d20356f0`) | registry, fast-path router, spawn/despawn policy, Shazam Cognitif, contextual cleaner, symbolic reducer, format converter, cost guard, trace; MicroUtility and activation thresholds; all advisory, KX108_ONLY | historical spec-only, never implemented as ARM |
| Archived backlog note « C346–C355 — ARM / micro-agents » | commit `b78d5da2` (archive) | « ARM → Context extraction → Memory candidate → Graphiti readonly / write candidate »; « ARM peut extraire. ARM ne décide pas quoi croire définitivement. » | historical boundary statement |
| R6 SENS roadmap « SENS-14 — ARM reconstruction with evidence vs inference separation » | commit `4a6fd23f` (branch `docs/gps-*`, not on this branch) | requirement-level reference only | see §18 |
| M32 spec §7 « ARM schedulers, routing, and optimizations are deferred to M33+ » | `docs/architecture/M32_COMMON_COGNITIVE_PRIMITIVES_SPEC_V1.md` | deferral wording inside M32 | interpreted narrowly, see §4 |
| Foundation seal §7 « ARM / Cross-domain transfer / Bio / COMOS » deferred | `docs/architecture/COGNITIVE_FOUNDATION_V1_SEAL.md` | ARM is a deferred layer outside the seal | normative boundary |
| « Concept Obsi » and « source 94 » (ARM → chemins cognitifs → biologie animale → cycles/cosmos) | provided by the project owner; not present in this repository | lineage material | lineage only, see §25 |
| Shazam Cognitif (C350 descendant) | `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/05_SHAZAM_COGNITIF/`; `tests/periphery/test_shazam_cognitif_context_only.py` | context-only, non-decisional tree activation | specialized descendant, see §17 |

No source is treated as current runtime truth. There is no ARM runtime, no ARM test, no canonical ARM document in the repository before this note.

## 3. ARM lineage

| Generation | Name | Purpose | Status |
|---|---|---|---|
| G1 | ARM prompt agent | methodical reconstruction of concepts/ideas from raw conversational material | historical, doc-only |
| G2 | `arm_microagents` (C346–C355) | decomposition into advisory micro-agents with utility/activation metrics | historical spec-only; responsibilities redistributed (§24) |
| G3 | SENS-14 | reconstruction with evidence vs inference separation | reference-only (§18) |
| G4 | M32 §7 deferral | higher-order mechanisms over primitives deferred | narrowed by §4 |
| M33 | this doctrine | historical mission on the modern typed substrate | doctrine frozen |

## 4. Resolution of the apparent conflict

Historical ARM was already broader than document extraction. It included recovery of forgotten or implicit concepts, reconstruction of cognitive trajectories, identification of possible paths, decomposition and recomposition, and search for latent structure. The historical reconstruction mission and modern cognitive reconstruction are descendants of the SAME conceptual lineage.

The M32 §7 wording « ARM schedulers, routing, and optimizations are deferred to M33+ » does not define ARM. It is read narrowly as: higher-order mechanisms that consume M32 primitives are out of M32 scope. It confers no scheduler, router or optimizer identity on ARM.

- `M32_SECTION_7_REDEFINES_ARM=NO`
- `ARM_SCHEDULER_FRAMING_CANONICAL=NO`

## 5. Core transformation (doctrine level)

INPUT: fragmented, incomplete, noisy, historical or heterogeneous cognitive material; its available provenance; admissible typed context; references to already-known structures when available.

PROCESS: decompose → identify → relate → distinguish evidence from inference → detect explicit / implicit / forgotten / latent material → expose contradiction, missing information and unresolved relationships → reconstruct a candidate structure.

OUTPUT: typed reconstruction candidates carrying explicit provenance and epistemic qualification.

Exact types, fields and enums are left to the M33 specification.

## 6. Evidence is not inference

Central M33 doctrine:

- `EVIDENCE != INFERENCE`
- `EXPLICIT != INFERRED`
- `OBSERVED != RECONSTRUCTED`
- `RECONSTRUCTED != VERIFIED`
- `RECONSTRUCTED != PROMOTED`
- `RECONSTRUCTED != TRUTH`

Every candidate element MUST preserve enough information to distinguish: directly supported evidence; inference; unresolved relation; contradiction; absence or missing material. `EVIDENCE_VS_INFERENCE_SEPARATION_REQUIRED=YES`. Exact spellings are left to the specification.

## 7. Historical integration status

The historical classification « déjà intégré / évoqué non verrouillé / absent » is preserved as descriptive reconstruction metadata only. It never means truth, verification, promotion, memory status or authority.

- `INTEGRATION_STATUS_IS_DESCRIPTIVE_ONLY=YES`

The specification may rename the values while preserving these semantics.

## 8. Output model

- `M33_CANONICAL_OUTPUT=TYPED_RECONSTRUCTION_CANDIDATES`
- `HUMAN_REPORT_IS_CANONICAL_RUNTIME_OUTPUT=NO`
- `HUMAN_REPORT_IS_PROJECTION=YES`

Historical report views (solide, évoqué, oublié, latent, questions ouvertes) may exist as human-facing projections over typed candidates. They do not define runtime truth semantics.

## 9. B6 boundary

B6 owns state-explicit context assembly, query-aware projection, visibility, context packaging and the retrieval/routing seams closed there. M33 may consume admissible context; it does not redefine Context Assembly. Historical ARM « context extraction » is classified ABSORBED_BY_B6.

- `ARM_CONTEXT_EXTRACTION_OWNERSHIP=NO`
- `B6_CONTEXT_ASSEMBLY_REMAINS_OWNER=YES`

## 10. B7 boundary

B7 owns CognitiveRoleSpec. The functional idea « several specialized cognitive functions may participate in a reconstruction » survives; role definitions remain B7's.

- `ARM_MAY_USE_COGNITIVE_ROLES=YES`
- `ARM_MAY_DEFINE_NEW_ROLE_AUTHORITY=NO`
- `ARM_MICROAGENT_ROLE_TAXONOMY_CANONICAL=NO`

## 11. B8 boundary

ARM may produce candidates, relations, hypotheses, reconstruction structures and evidence/inference classifications. ARM may not promote belief to knowledge, declare truth, or write canonical knowledge.

- `ARM_OUTPUT_IS_CANDIDATE_ONLY=YES`
- `B8_PROMOTION_REMAINS_EXTERNAL=YES`

## 12. B9 boundary

B9 owns CognitivePath, FailedPath and PathHistory. ARM may reconstruct or refer to trajectories; relations between candidate elements do not automatically become B9 CognitivePaths.

- `ARM_MAY_REFERENCE_COGNITIVE_PATH=YES`
- `ARM_MAY_REDEFINE_COGNITIVE_PATH=NO`
- `B9_PATH_SEMANTICS_REMAIN_EXTERNAL=YES`

## 13. M32 boundary

- `M32_IS_ARM=NO`
- `M32_IS_ARM_SUBSTRATE=YES`

M32 provides typed cognitive material, primitive invocation/result contracts, canonical identity, structural composition, domain adapters and provenance. M33 consumes them and does not redefine PrimitiveTypeSpec, TypedCognitiveDatum, PrimitiveInvocation, PrimitiveResult, M32 canonicalization or the M32 result taxonomy.

- `M33_MAY_USE_M32_PRIMITIVES=YES`
- `M33_MAY_REDEFINE_M32_PRIMITIVES=NO`
- `CORE_PRIMITIVE_COUNT=0` unless a later independently certified doctrine changes it. M33 does not require canonical core primitives.

## 14. ARM is not a required graph

Historical material mentions paths, branches, relations and multi-dimensional structures, but no canonical ARM graph contract was established.

- `ARM_GRAPH_REQUIRED=NO`
- `GRAPH != ARM`
- `ARM != GRAPH_SCHEDULER`

A graph MAY later be one representation of a reconstruction result. The specification must not introduce ARMGraph, ARMNode or ARMEdge without independent justification.

## 15. Memory boundary

Historical ARM produced memory candidates and Graphiti write candidates. Persistence now belongs downstream.

- `MEMORY_WRITE=False`
- `ARM_MAY_PRODUCE_MEMORY_CANDIDATE_CONTENT=YES` (as candidate content only, never persisted by M33)
- `ARM_MAY_PERSIST_MEMORY=NO`
- `GRAPHITI_WRITE_ALLOWED=NO`
- `MEMORY_CANDIDATE_PERSISTENCE_DEFERRED_TO_B10=YES`
- `GRAPHITI_WRITE_DEFERRED_TO_B10=YES`

## 16. Calibration / selection boundary

MicroUtility, activation thresholds, spawn/despawn policies, fast-path routing and cost guards are historically valuable and no longer owned by M33. Selecting a useful reconstruction route confers no authority.

- `MICROUTILITY_DEFERRED_TO_B11_B12=YES`
- `MICROAGENT_ACTIVATION_THRESHOLD_DEFERRED_TO_B11_B12=YES`
- `FAST_PATH_SELECTION_DEFERRED_TO_B12=YES`
- `CAPABILITY_SELECTION_DEFERRED_TO_B12=YES`

## 17. Shazam Cognitif

- `SHAZAM_IS_ARM=NO`
- `SHAZAM_IS_SPECIALIZED_DESCENDANT=YES`

Shazam runtime is not absorbed into M33 and the existing periphery code is not rewritten in this chapter.

## 18. SENS-14

Targeted read-only check: SENS-14 appears only as a roadmap line in `docs/architecture/R6_SENS_COGNITION_CANONICAL_AUDIT_V0.md` (commit `4a6fd23f`, reachable from `origin/docs/gps-defense-global-plan-20261008`, not from this branch). No code, test or closure proof was found in this repository's history.

- `SENS14_STATUS=REFERENCE_ONLY`
- `EVIDENCE_VS_INFERENCE_SEPARATION_REQUIRED=YES` regardless of delivery status.

If SENS-14 is later shown delivered canonically, M33 consumes it. Otherwise M33 may define its local reconstruction qualification contract without claiming retroactive SENS-14 closure.

## 19. State model

`M33_STATE_MODEL=EPHEMERAL_RECONSTRUCTION_STATE`: ephemeral, bounded to one reconstruction, non-durable by default. It may contain candidate elements, relations, provenance, evidence/inference classifications, unresolved items, contradictions and reconstruction progress. It never becomes durable canonical memory.

## 20. Execution model

`M33_EXECUTION_MODEL=BOUNDED_COGNITIVE_RECONSTRUCTION`.

M33 may: consume typed material; invoke or consume M32-compliant primitive behavior; use existing cognitive roles; construct candidate reconstruction structures.

M33 may not: become an autonomous scheduler; persist arbitrary state; act on the world; promote knowledge; self-authorize capability; select KX108 decisions.

## 21. Failure model

The specification MUST distinguish at least: insufficient evidence or material; unresolved reference or relation; contradictory evidence; ambiguous reconstruction; primitive/runtime failure; invalid typed input; and a successful-but-partial reconstruction.

- `FAILURE_IS_NOT_FALSE=YES`
- `UNKNOWN_IS_NOT_FALSE=YES`
- `PARTIAL_RECONSTRUCTION_IS_NOT_COMPLETE_RECONSTRUCTION=YES`

Exact status names belong to the specification.

## 22. Identity / determinism

Same semantic reconstruction inputs and configuration must be capable of a deterministic identity. Runtime, provider or wall-clock provenance must not silently change semantic identity. M32 canonicalization is reused where applicable; no second canonicalization system is created.

- `M33_IDENTITY_DOCTRINE=DETERMINISTIC_SEMANTIC_ID_REQUIRED`
- `M33_IDENTITY_ALGORITHM=DEFER_TO_SPEC`

## 23. Authority

`COGNITION != AUTHORITY`; `ARM_AUTHORITY=ADVISORY_ONLY`.

ARM may not authorize action, emit ACT, write durable memory, promote knowledge, mutate Binder, mutate KX108, override GuardX108, or declare world truth.

- `MEMORY_WRITE=False`
- `EMITS_ACT=False`
- `BINDER_MUTATION=False`
- `KERNEL_MUTATION=False`
- `KX108_MUTATION=False`
- `ONE_FINAL_ACTION_AUTHORITY=KX108_ONLY`

## 24. Historical feature classification

| Historical ARM feature | Current owner | M33 status |
|---|---|---|
| document / material reconstruction | M33 | KEEP_IN_M33 |
| implicit / forgotten concept recovery | M33 | KEEP_IN_M33 |
| trajectory reconstruction | M33 (references B9 paths, does not define them) | KEEP_IN_M33 |
| context extraction | B6 Context Assembly | CONSUME_FROM_EXISTING_LAYER |
| micro-agent roles | B7 CognitiveRoleSpec | CONSUME_FROM_EXISTING_LAYER |
| memory candidate (persistence) | B10 | DEFER_TO_LATER_LAYER |
| Graphiti writes | B10 | DEFER_TO_LATER_LAYER |
| MicroUtility | B11 / B12 | DEFER_TO_LATER_LAYER |
| activation threshold | B11 / B12 | DEFER_TO_LATER_LAYER |
| spawn / despawn | B12 | DEFER_TO_LATER_LAYER |
| fast-path routing | B12 | DEFER_TO_LATER_LAYER |
| Shazam Cognitif | periphery (C350 descendant) | SPECIALIZED_DESCENDANT |
| symbolic reduction | M32 primitive candidate / M33 use | HISTORICAL_ONLY (may return as a registered primitive under M32 rules) |
| format conversion | M32 domain adapters | CONSUME_FROM_EXISTING_LAYER |
| cost guard | B12 | DEFER_TO_LATER_LAYER |
| trace / provenance | M32 provenance + M33 candidate provenance | KEEP_IN_M33 (consuming M32 provenance) |
| evidence vs inference separation (SENS-14) | M33 | KEEP_IN_M33 |
| integration status (déjà intégré / évoqué / absent) | M33, descriptive only | KEEP_IN_M33 |

## 25. Source 94 and biology lineage

Lineage preserved: ARM → chemins cognitifs → biologie animale → cycles/cosmos. Source 94 demonstrates the reconstruction of old metaphors and concepts into modern structural primitives, and the recurring pattern chaos → tri → ordre → synthèse.

- `SOURCE94_SUPPORTS_ARM_RECONSTRUCTION_LINEAGE=YES`
- `SOURCE94_AUTHORIZES_M34_IMPLEMENTATION=NO`

M34 (Biology) remains separate. Source 94 is lineage evidence supplied by the project owner; it is not present in this repository.

## 26. Seven fluxes / organic model

The seven fluxes are a `HISTORICAL_CONCEPTUAL_MODEL` (also marked out of the public canonical corpus in `docs/REPO_BOUNDARY.md`). Likely relevance: M34 Biology Patterns, M35 COMOS, cross-domain transfer.

- `SEVEN_FLUXES_CANONICAL_FOR_M33=NO`
- `SEVEN_FLUXES_RELEVANT_FOR_M34=YES`

Flux Analytique, Visionnaire, Directionnel, Symbolique, Emotionnel, Fractal and Réciproque are not M33 runtime types.

## 27. Doctrine invariants

- `ARM != SCHEDULER`
- `ARM != ROUTER`
- `ARM != ROLE_SYSTEM`
- `ARM != KNOWLEDGE_PROMOTION`
- `ARM != MEMORY`
- `ARM != WORLD_MODEL`
- `ARM != AUTHORITY`
- `M32 != ARM`; `M32 = ARM_SUBSTRATE`
- `RECONSTRUCTED != VERIFIED`; `RECONSTRUCTED != PROMOTED`; `RECONSTRUCTED != TRUTH`
- `EVIDENCE != INFERENCE`; `EXPLICIT != INFERRED`; `UNKNOWN != FALSE`
- `INTEGRATION_STATUS != EPISTEMIC_STATUS`; `INTEGRATION_STATUS != MEMORY_STATUS`; `INTEGRATION_STATUS != AUTHORITY`
- `GRAPH != ARM`
- `COGNITION != AUTHORITY`
- `ONE_FINAL_ACTION_AUTHORITY=KX108_ONLY`

Sealed foundation laws are unchanged (ONE OBJECT, MANY PROJECTIONS, MANY RELATIONS, MANY PATHS, NO AUTOMATIC FUSION; `MEMORY != TRUTH`; `CONFIDENCE != AUTHORITY`; `COMPETENCE != AUTHORITY`).

## 28. What the later M33 specification may and must formalize

May formalize (left open here): exact Python API; types and field names of reconstruction candidates; enums for evidence/inference qualification, integration status and failure states; canonical serialization (reusing M32 canonical JSON); identity preimage and algorithm; error codes; runtime location outside the seal.

Must not: contradict any freeze in this note; introduce durable persistence, scheduling, routing, role definitions, promotion, world-model or authority; redefine M32, B6, B7, B8 or B9 contracts.

Doctrinal readiness for the specification (author self-assessment; requires independent certification):

| Item | Resolved at doctrine level |
|---|---|
| canonical meaning | YES (§1, §4) |
| boundary B6 / B7 / B8 / B9 / M32 | YES (§9–§13) |
| memory / world model / authority boundaries | YES (§15, §1, §23) |
| input model | YES at doctrine level (§5) |
| output model | YES at doctrine level (§8) |
| state model | YES (§19) |
| execution model | YES (§20) |
| failure model | YES at doctrine level (§21); names deferred |

Status: `M33_DOCTRINE_FROZEN=YES`; `M33_SPEC_WRITTEN=NO`; `M33_IMPLEMENTED=NO`; `M33_CLOSED=NO`. Next step: fresh independent read-only certification of this doctrine before writing the M33 specification.
