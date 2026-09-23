# Cognitive Convergence Master Map

Verified head: `3ce425fe97ef7b35fae876b6997dd36016d7e6ae`

This map is generated from `COGNITIVE_CONVERGENCE_MASTER_REGISTRY.json`.

It is an architectural index, not proof of authority.

## V5 Signal Dedup Closure

V5 closed without runtime modification.

Canonical conclusions:

- V5_RUNTIME_PATCH_REQUIRED=FALSE;
- C1_PROJECTION_REQUIRED=FALSE;
- NEW_C1_HOOKS_PROVEN=0;
- DISTINCT_MATERIAL_SIGNAL_REQUIRING_NEW_HOOK=0;
- symbolic/fractal/temporal/prediction/weak-signal material remains non-authoritative and readonly;
- Native Memory remains the canonical memory target;
- MEMZUM remains the memory gate;
- no duplicate C1 projection is authorized for these signals.

V5 classifications:

- symbolic_signal=ALREADY_ABSORBED;
- fractal_signal=ALREADY_ABSORBED;
- temporal_signal=ALREADY_ABSORBED;
- prediction_signal=ALREADY_ABSORBED via projection_not_prediction_signal;
- weak_signal_path=ALREADY_ABSORBED;
- symbolic_fractal_memory=HISTORICAL/SUPERSEDED.

## V4 Semantic Continuity - CLOSED

V4 closed without runtime modification.

Proven conclusions:

- semantic query is already connected to C1;
- canonical intent is already connected to C1;
- Reverse OS / IR already enters C1;
- ContextPacketV2 / IR feed the final answer path;
- C265-C278 are real, ordered semantic calibration stages;
- C265-C278 remain on their existing semantic/response path;
- no duplicate C265-C274 projection into C1 is required;
- known_concept_ids is context/provenance only for reasoning control;
- CIC remains readonly/debug;
- semantic_plan belongs to the Obsidure engineering/build path;
- Cognitive Layer Router identity remains unproven and must not be wired blindly;
- SSR remains documented, not runtime.

## Canonical Semantic Flow

```text
user input
-> semantic query
-> canonical intent
-> pre-reasoning C265/C266/C273/C274
-> bounded reasoning directive
-> Brody response pipeline
-> C275/C276/C277/C278

parallel governed cognition:
semantic query / intent / Reverse OS / IR / memory / signals
-> C1
-> ContextPacketV2 / IR candidate
-> V1.4.12A
-> Brody full context
-> True Voice
-> final answer
```

The semantic calibration path and C1 are complementary, not duplicate engines.

## ACTIVE + CONNECTED

| ID | NAME | TYPE | STATUS | CURRENT LOCATION | CURRENT CONSUMER | TARGET | BLOCKER | NEXT ACTION |
|---|---|---|---|---|---|---|---|---|
| c1_cognitive_join | C1 cognitive join | COGNITIVE_SIGNAL | ACTIVE_CONNECTED | apps/obsidia_api/brody_real_cognitive_join.py | ContextPacketV2, brody_full_context, V1.4.12A final answer adapter | run_real_cognitive_join(...) | - | Keep frozen; update this registry when new projections are added. |
| context_packet_v2 | ContextPacketV2 | PROVENANCE | ACTIVE_CONNECTED | apps/obsidia_api/brody_real_cognitive_join.py | routes/brody.py, V1.4.12A, brody_full_context | ContextPacketV2.context_items / source_refs | - | Preserve compactness; add only symbolic markers or bounded refs. |
| ir_candidate | IR candidate | SEMANTIC_LAYER | ACTIVE_CONNECTED | apps/obsidia_api/brody_real_cognitive_join.py | brody_full_context, V1.4.12A, True Voice | governed_cognitive_projection.ir_candidate | - | Keep readonly; do not promote raw IR into final authority. |
| micro_core | Brody cognitive micro-core | COGNITIVE_SIGNAL | ACTIVE_CONNECTED | apps/obsidia_api/brody_cognitive_micro_core.py | C1 cognitive join, ContextPacketV2 | ContextPacketV2.context_items | - | Keep frozen and update tests when changing projection shape. |
| balance_engine | Balance engine | COGNITIVE_SIGNAL | ACTIVE_CONNECTED | apps/obsidia_api/brody_balance_engine.py | C1 cognitive join, ContextPacketV2 | ContextPacketV2.context_items | - | Keep frozen and update tests when changing projection shape. |
| point_cloud_21d | 21D point cloud | COGNITIVE_SIGNAL | ACTIVE_CONNECTED | apps/obsidia_api/brody_point_cloud_21d_selector.py | C1 cognitive join, ContextPacketV2 | ContextPacketV2.context_items | - | Keep frozen and update tests when changing projection shape. |
| memzum | MEMZUM activation | MEMORY | ACTIVE_CONNECTED | apps/obsidia_api/brody_memzum_activation_adapter.py | C1 cognitive join, ContextPacketV2 | ContextPacketV2.context_items | - | Keep frozen and update tests when changing projection shape. |
| native_memory | Native Memory | MEMORY | ACTIVE_CONNECTED | apps/obsidia_api/brody_obsidia_native_memory.py | C1 cognitive join, ContextPacketV2 | C1 optional precomputed input | - | Keep frozen and update tests when changing projection shape. |
| tree_signal_packet | TreeSignalPacket | COGNITIVE_SIGNAL | ACTIVE_CONNECTED | apps/obsidia_api/brody_tree_signal_packet.py | C1 cognitive join, ContextPacketV2 | ContextPacketV2.context_items | - | Keep frozen and update tests when changing projection shape. |
| tree_policy | Tree policy snapshot | COGNITIVE_SIGNAL | ACTIVE_CONNECTED | apps/obsidia_api/brody_tree_policy_adapter.py | C1 cognitive join, ContextPacketV2 | ContextPacketV2.context_items | - | Keep frozen and update tests when changing projection shape. |
| mmonde_34d | MMONDE / 34D cognitive trees | WORLD_MODEL | ACTIVE_CONNECTED | apps/obsidia_api/brody_tree_signal_packet.py | C1 cognitive join, ContextPacketV2 | ContextPacketV2.context_items | - | Do not expand raw tree corpus into C1; preserve compact markers. |
| dominant_trees | Dominant trees | COGNITIVE_SIGNAL | ACTIVE_CONNECTED | periphery/cognitive_trees/dominant_trees.py | C1 cognitive join | ContextPacketV2.context_items | - | Keep selection bounded. |
| shazam_cognitif | Shazam Cognitif | COGNITIVE_SIGNAL | ACTIVE_CONNECTED | periphery/cognitive_trees/shazam_cognitif.py | C1 cognitive join, TreeSignalPacket | ContextPacketV2.context_items | - | Keep context-only; never allow Shazam to decide. |
| memory_world_mapper | memory_world_mapper | WORLD_MODEL | ACTIVE_CONNECTED | periphery/cognitive_trees/memory_world_mapper.py | C1 cognitive join | ContextPacketV2.context_items | - | Keep separated from Native Memory records. |
| source_pack_routing | source-pack routing | SOURCE_ROUTING | ACTIVE_CONNECTED | runtime_wiring/source_runtime/brody_source_context_bridge.py | C1 cognitive join, ContextPacketV2, True Voice | C1 optional precomputed input; ContextPacketV2.source_refs; True Voice source_pack_context | - | Keep raw source content out of C1; extend tests for new families. |
| semantic_query_router | semantic query/router | SEMANTIC_LAYER | ACTIVE_CONNECTED | apps/obsidia_api/brody_semantic_query_router.py | Brody route, C1 cognitive join | run_real_cognitive_join(precomputed_semantic_query=semantic_query_snapshot) | - | Keep the existing Brody route -> C1 semantic-query binding. Do not create a second semantic-query path. |
| intention | canonical intent | SEMANTIC_LAYER | ACTIVE_CONNECTED | apps/obsidia_api/routes/brody.py | Brody route, C1 cognitive join, V1.4.12A | run_real_cognitive_join(precomputed_intent=intent) | - | Preserve the canonical _detect_intent -> C1 path and keep it separate from specialized capability-query recognition. |
| c265 | C265 sense to symbolic integration | SEMANTIC_LAYER | ACTIVE_CONNECTED | periphery/language/pre_reasoning_calibrator.py | Brody real response pipeline | pre_reasoning_snapshot.C265 | - | V4 CLOSED. Preserve the current proven pipeline hook; do not rewire or duplicate into C1. |
| c266 | C266 symbolic alignment | SEMANTIC_LAYER | ACTIVE_CONNECTED | periphery/language/pre_reasoning_calibrator.py | Brody real response pipeline | pre_reasoning_snapshot.C266 | - | V4 CLOSED. Preserve the current proven pipeline hook; do not rewire or duplicate into C1. |
| c273 | C273 divergence detection | SEMANTIC_LAYER | ACTIVE_CONNECTED | periphery/language/pre_reasoning_calibrator.py | Brody real response pipeline | pre_reasoning_snapshot.C273 | - | V4 CLOSED. Preserve the current proven pipeline hook; do not rewire or duplicate into C1. |
| c274 | C274 pre-reasoning calibration | SEMANTIC_LAYER | ACTIVE_CONNECTED | periphery/language/pre_reasoning_calibrator.py | Brody real response pipeline | pre_reasoning_snapshot.C274 | - | V4 CLOSED. Preserve the current proven pipeline hook; do not rewire or duplicate into C1. |
| c275 | C275 pre-response calibration | SEMANTIC_LAYER | ACTIVE_CONNECTED | periphery/language/pre_response_calibrator.py | Brody real response pipeline | real_response_pipeline.c275 | - | V4 CLOSED. Preserve the current proven pipeline hook; do not rewire or duplicate into C1. |
| c276 | C276 pre-action calibration | SEMANTIC_LAYER | ACTIVE_CONNECTED | periphery/language/pre_action_calibrator.py | Brody real response pipeline | real_response_pipeline.c276 | - | V4 CLOSED. Preserve the current proven pipeline hook; do not rewire or duplicate into C1. |
| c277 | C277 final sense halo | SEMANTIC_LAYER | ACTIVE_CONNECTED | periphery/language/final_sense_halo.py | Brody real response pipeline | real_response_pipeline.c277 | - | V4 CLOSED. Preserve the current proven pipeline hook; do not rewire or duplicate into C1. |
| c278 | C278 action meaning validator | SEMANTIC_LAYER | ACTIVE_CONNECTED | periphery/language/action_meaning_validator.py | Brody real response pipeline | real_response_pipeline.c278 | - | V4 CLOSED. Preserve the current proven pipeline hook; do not rewire or duplicate into C1. |
| symbolic_signal | symbolic signal | COGNITIVE_SIGNAL | ACTIVE_CONNECTED | apps/obsidia_api/brody_cognitive_micro_core.py | brody_balance_engine._balance_symbolique, brody_point_cloud_21d_selector symbolic axis/layer, brody_real_cognitive_join compact ContextPacketV2 deep context | existing compact cognitive projection only; no dedicated C1 hook | CLOSED_BY_V5_SIGNAL_DEDUP_AUDIT | Keep absorbed in the existing compact path. Do not add a dedicated C1 projection without new distinct material evidence. |
| fractal_signal | fractal signal | COGNITIVE_SIGNAL | ACTIVE_CONNECTED | apps/obsidia_api/brody_cognitive_micro_core.py | brody_point_cloud_21d_selector fractal axis/layer, brody_real_cognitive_join compact ContextPacketV2 deep context | existing compact cognitive projection only; no dedicated C1 hook | CLOSED_BY_V5_SIGNAL_DEDUP_AUDIT | Keep absorbed in the existing compact path. Do not add a dedicated C1 projection without new distinct material evidence. |
| temporal_signal | temporal signal / temporal_detected | COGNITIVE_SIGNAL | ACTIVE_CONNECTED | apps/obsidia_api/brody_cognitive_micro_core.py | brody_point_cloud_21d_selector temporal axis/layer, brody_real_cognitive_join compact ContextPacketV2 deep context | existing compact cognitive projection only; no dedicated C1 hook | CLOSED_BY_V5_SIGNAL_DEDUP_AUDIT | Keep absorbed in the existing compact path. Do not add a dedicated C1 projection without new distinct material evidence. |
| prediction_signal | projection_not_prediction_signal | COGNITIVE_SIGNAL | ACTIVE_CONNECTED | apps/obsidia_api/brody_cognitive_micro_core.py | brody_balance_engine._balance_projection, brody_point_cloud_21d_selector projection axis/layer, brody_real_cognitive_join._micro_context risk flag MICRO_CORE:PREDICTION_CLAIM | existing compact cognitive projection only; no dedicated C1 hook | CLOSED_BY_V5_SIGNAL_DEDUP_AUDIT | Use projection_not_prediction_signal as the canonical runtime mechanism. Do not create a second prediction_signal component or C1 hook. |
| weak_signal_path | weak-signal path | COGNITIVE_SIGNAL | ACTIVE_CONNECTED | apps/obsidia_api/brody_cognitive_micro_core.py | brody_balance_engine._balance_signal_faible, brody_point_cloud_21d_selector weak-layer voting, brody_real_cognitive_join compact ContextPacketV2 deep context | existing compact cognitive projection only; no dedicated C1 hook | CLOSED_BY_V5_SIGNAL_DEDUP_AUDIT | Keep absorbed in the existing compact path. Do not add a dedicated C1 projection without new distinct material evidence. |
| data_purity | Data Purity | GOVERNANCE_SIGNAL | ACTIVE_CONNECTED | periphery/data_purity_agent.py | C1 | C1 | - | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| brody_full_context | Brody full context | OUTPUT_LAYER | ACTIVE_CONNECTED | apps/obsidia_api/routes/brody.py | True Voice | brody_full_context | - | Keep boundary readonly and update registry after any dependency/provenance audit. |
| true_voice | True Voice | OUTPUT_LAYER | ACTIVE_CONNECTED | apps/obsidia_api/brody_true_voice_adapter.py | final answer | true_voice_snapshot | - | Keep boundary readonly and update registry after any dependency/provenance audit. |

## READY TO WIRE

| ID | NAME | TYPE | STATUS | CURRENT LOCATION | CURRENT CONSUMER | TARGET | BLOCKER | NEXT ACTION |
|---|---|---|---|---|---|---|---|---|

## PARTIAL / RECONCILE

| ID | NAME | TYPE | STATUS | CURRENT LOCATION | CURRENT CONSUMER | TARGET | BLOCKER | NEXT ACTION |
|---|---|---|---|---|---|---|---|---|
| source_registry | Source registry | KNOWLEDGE_INDEX | ACTIVE_PARTIAL | runtime_wiring/source_registry/source_file_registry.json | source runtime, source-pack routing | runtime_wiring.source_registry.registry_loader | - | Keep readonly; do not register source files as runtime modules. |
| atlas | ATLAS | KNOWLEDGE_INDEX | ACTIVE_PARTIAL | runtime_wiring/source_runtime/source_family_selector.py | source-pack routing | source-pack routing -> C1 compact projection | - | Audit any new ATLAS family before allowing it into source routing. |
| capability_routing | Capability routing | CAPABILITY | ACTIVE_PARTIAL | runtime_wiring/source_runtime/capability_path_router.py | source runtime, workbench preview | capability router | - | Keep advisory; do not use as authorization. |
| capability_registry | Capability registry | CAPABILITY | ACTIVE_PARTIAL | runtime_wiring/source_runtime/capability_taxonomy.py | capability routing | capability taxonomy | - | Audit for duplicate labels before expansion. |
| semantic_plan | semantic plan | SEMANTIC_LAYER | ACTIVE_PARTIAL | apps/obsidia_api/brody_semantic_plan.py | Obsidure native engineering consumer | obsidure_native_engineering_consumer -> semantic_plan | - | Keep semantic_plan on the Obsidure engineering/build path. Do not inject it into C1 without new runtime evidence. |
| semantic_representation | semantic representation | SEMANTIC_LAYER | PARTIAL_NEEDS_RECONCILIATION | periphery/language/language_router.py | Brody pipeline | [UNRESOLVED TARGET] | No distinct normal-path runtime stage proven | Historical/parallel identity audit only. Not a blocker for the canonical Brody -> C1 -> response path. |
| cic | CIC / cognitive invariants | SEMANTIC_LAYER | ACTIVE_PARTIAL | apps/obsidia_api/brody_cic_context_adapter.py | Brody readonly response payload/debug surface | _brody_attach_cic_readonly_context_v0 -> cic_readonly_context | - | Preserve readonly/debug binding. No C1 promotion without new material-effect evidence. |
| reverse_os | Reverse OS | LANGUAGE_LAYER | ACTIVE_PARTIAL | apps/obsidia_api/brody_existing_reverse_os_bridge.py | C1 / output layer | reverse_os_projection / ir_candidate | - | Keep separated from KX108 authority; audit exact hook before wiring. |
| os_trad | OS Trad | LANGUAGE_LAYER | ACTIVE_PARTIAL | apps/obsidia_api/os_adapters/os_trad_adapter.py | source routing / output layer | OS_TRAD_REVERSE_OS source family | - | Keep separated from KX108 authority; audit exact hook before wiring. |
| verbatia | VERBATIA | LANGUAGE_LAYER | ACTIVE_PARTIAL | apps/obsidia_api/brody_cognitive_modules_adapter.py | True Voice | True Voice | Runtime implementation and compact hook audit required. | Keep separated from KX108 authority; audit exact hook before wiring. |
| sigma | Sigma | GOVERNANCE_SIGNAL | ACTIVE_PARTIAL | sigma/ | Sigma/meta input | Sigma/meta input | - | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| sigma_monitor | Sigma Monitor | METACOGNITION | ACTIVE_PARTIAL | sigma/sigma_monitor.py | Sigma/meta input | Sigma/meta input | - | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| proof_of_governance | ProofOfGovernance | GOVERNANCE_SIGNAL | ACTIVE_PARTIAL | periphery/math_core/proof_of_governance.py | Sigma/meta input | Sigma/meta input | - | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| thermodynamics | thermodynamics | SCIENCE_REASONING | ACTIVE_PARTIAL | apps/obsidia_api/brody_thermodynamics_signal.py | Brody readonly observer | Brody readonly observer | - | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| flux_energy | flux / energy | SCIENCE_REASONING | ACTIVE_PARTIAL | apps/obsidia_api/brody_balance_engine.py | Brody readonly observer | Brody readonly observer | - | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| timeverse | Timeverse | WORLD_MODEL | ACTIVE_PARTIAL | periphery/timeverse.py | Brody readonly observer | Brody readonly observer | - | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| causal_dynamics | causal dynamics | COGNITIVE_SIGNAL | ACTIVE_PARTIAL | apps/obsidia_api/brody_balance_engine.py | C1 candidate | C1 candidate | - | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| world_model | world model | WORLD_MODEL | ACTIVE_PARTIAL | periphery/world_calls/ | domain adapter / world calls | domain adapter / world calls | - | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| physical_world_model | physical world model | WORLD_MODEL | ACTIVE_PARTIAL | periphery/world_calls/world_action_bus.py | world action dry-run | world action dry-run | - | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| peripheral_mesh | Peripheral Mesh | ADAPTER | ACTIVE_PARTIAL | periphery/ | Brody/Sigma/domain adapters | Brody/Sigma/domain adapters | - | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| oie | OIE | SCIENCE_REASONING | ACTIVE_PARTIAL | tests/test_oie_obsidia_vs_gemini_power_v0_7.py | diagnostic only | diagnostic only | - | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| qwen_local_evidence | Qwen local evidence path | ADAPTER | ACTIVE_PARTIAL | tests/cli/test_obsidia_qwen_local_evidence_v0.py | evidence path | evidence path | Resolve exact hook or dependency before wiring. | Keep boundary readonly and update registry after any dependency/provenance audit. |
| obsidure | Obsidure cognitive/code boundary | ADAPTER | ACTIVE_PARTIAL | periphery/agents/agent_obsidure.py | code proposal/apply boundary | code proposal/apply boundary | Resolve exact hook or dependency before wiring. | Keep boundary readonly and update registry after any dependency/provenance audit. |
| domain_adapters | domain adapters | ADAPTER | ACTIVE_PARTIAL | sigma/domains/ | Sigma/domain context | Sigma/domain context | Resolve exact hook or dependency before wiring. | Keep boundary readonly and update registry after any dependency/provenance audit. |
| brody_capabilities_intent | Brody capabilities intent | CAPABILITY | ACTIVE_PARTIAL | apps/obsidia_api/brody_capabilities_intent.py | Brody capability response path | is_brody_capabilities_query / build_brody_capabilities_response | Add dedicated integration-test evidence if this path is later promoted from ACTIVE_PARTIAL. | Keep distinct from canonical intent. Do not route this specialized classifier into C1 as a second intent. |

## BLOCKED

| ID | NAME | TYPE | STATUS | CURRENT LOCATION | CURRENT CONSUMER | TARGET | BLOCKER | NEXT ACTION |
|---|---|---|---|---|---|---|---|---|
| lyapunov | Lyapunov | SCIENCE_REASONING | BLOCKED_BY_PROOF | periphery/math_core/lyapunov.py | - | [UNRESOLVED TARGET] | formal proof gap | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| openjarvis | OpenJarvis/Jarvis cognitive surface | ADAPTER | BLOCKED_BY_DEPENDENCY | tests/cli/test_openjarvis_cognitive_pilot_v0.py | CLI/surface | CLI/surface | missing openjarvis package in current environment | Keep boundary readonly and update registry after any dependency/provenance audit. |

## DOCUMENTED / NOT RUNTIME

| ID | NAME | TYPE | STATUS | CURRENT LOCATION | CURRENT CONSUMER | TARGET | BLOCKER | NEXT ACTION |
|---|---|---|---|---|---|---|---|---|
| ssr | SSR | LANGUAGE_LAYER | DOCUMENTED_NOT_RUNTIME | _source_packs/REVERSE_OS_INTERLANGUAGE_CANON_V1/evidence/interlanguage_transduction_v1.md | - | [UNRESOLVED TARGET] | Runtime implementation and compact hook audit required. | Keep as documented provenance. Do not create runtime SSR solely to satisfy historical architecture documents. |
| lu_mh | LU-MH | LANGUAGE_LAYER | DOCUMENTED_NOT_RUNTIME | _source_packs/REVERSE_OS_INTERLANGUAGE_CANON_V1/evidence/architecture_narrative_reverse_os.txt | - | [UNRESOLVED TARGET] | Runtime implementation and compact hook audit required. | Keep separated from KX108 authority; audit exact hook before wiring. |
| clavage | Clavage | LANGUAGE_LAYER | DOCUMENTED_NOT_RUNTIME | _source_packs/REVERSE_OS_INTERLANGUAGE_CANON_V1/evidence/architecture_protocoles_os_cognitif.txt | - | [UNRESOLVED TARGET] | Runtime implementation and compact hook audit required. | Keep separated from KX108 authority; audit exact hook before wiring. |
| oban | OBAN | LANGUAGE_LAYER | DOCUMENTED_NOT_RUNTIME | _source_packs/REVERSE_OS_INTERLANGUAGE_CANON_V1/evidence/architecture_protocoles_os_cognitif.txt | - | [UNRESOLVED TARGET] | Runtime implementation and compact hook audit required. | Keep separated from KX108 authority; audit exact hook before wiring. |
| shannon | Shannon | SCIENCE_REASONING | DOCUMENTED_NOT_RUNTIME | _source_discovery/OBSIDIA_NPL_PACK_AUDIO_ENTROPY_AUDIT_V1/ | - | [UNRESOLVED TARGET] | Proof/runtime boundary audit required before wiring. | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| negentropy | negentropy | SCIENCE_REASONING | DOCUMENTED_NOT_RUNTIME | _source_discovery/OBSIDIA_NPL_PACK_AUDIO_ENTROPY_AUDIT_V1/ | - | [UNRESOLVED TARGET] | Proof/runtime boundary audit required before wiring. | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |

## LEGACY / SUPERSEDED

| ID | NAME | TYPE | STATUS | CURRENT LOCATION | CURRENT CONSUMER | TARGET | BLOCKER | NEXT ACTION |
|---|---|---|---|---|---|---|---|---|
| symbolic_fractal_memory | symbolic/fractal memory (historical) | DOCUMENTED_CONCEPT | SUPERSEDED | - | - | NONE_DOCUMENT_ONLY | CLOSED_BY_V5_SIGNAL_DEDUP_AUDIT | Keep only as historical/migration provenance. Do not create a runtime memory authority, Native Memory bridge, MEMZUM modification, or C1 projection from this name. |
| graphiti | Graphiti residual memory layer | LEGACY | SUPERSEDED | apps/obsidia_api/brody_graphiti_guard.py | NONE_DOCUMENT_ONLY | NONE_DOCUMENT_ONLY | - | Keep boundary readonly and update registry after any dependency/provenance audit. |

## UNKNOWN / NEEDS AUDIT

| ID | NAME | TYPE | STATUS | CURRENT LOCATION | CURRENT CONSUMER | TARGET | BLOCKER | NEXT ACTION |
|---|---|---|---|---|---|---|---|---|
| branches | Branches | KNOWLEDGE_INDEX | SOURCE_FOUND_IMPLEMENTATION_UNKNOWN | periphery/OBSIDIA_V4_STRUCTURED_FULL/ | - | SOURCE_ROUTING | No per-child runtime contract proven | Register child only when it has distinct code or audited adapter target. |
| subbranches | Subbranches | KNOWLEDGE_INDEX | SOURCE_FOUND_IMPLEMENTATION_UNKNOWN | periphery/OBSIDIA_V4_STRUCTURED_FULL/ | - | SOURCE_ROUTING | No per-child runtime contract proven | Register child only when it has distinct code or audited adapter target. |
| pepites | Pepites | KNOWLEDGE_INDEX | SOURCE_FOUND_IMPLEMENTATION_UNKNOWN | periphery/OBSIDIA_V4_STRUCTURED_FULL/ | - | SOURCE_ROUTING | No per-child runtime contract proven | Register child only when it has distinct code or audited adapter target. |
| cognitive_layer_router | Cognitive Layer Router | SEMANTIC_LAYER | SOURCE_FOUND_IMPLEMENTATION_UNKNOWN | runtime_wiring/source_runtime/capability_path_router.py | - | [UNRESOLVED TARGET] | No distinct runtime symbol/caller proven, No test under this component identity | Identity archaeology only; determine whether this historical name maps to an existing router. Do not wire into C1. |
| rave | RAVE | LANGUAGE_LAYER | UNKNOWN | - | - | [UNRESOLVED TARGET] | Runtime implementation and compact hook audit required. | Keep separated from KX108 authority; audit exact hook before wiring. |
| aig_cmai | AIG / CMAI | DOCUMENTED_CONCEPT | UNKNOWN | - | - | [UNRESOLVED TARGET] | Proof/runtime boundary audit required before wiring. | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
