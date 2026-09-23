# Cognitive Convergence Master Map

Verified head: `0b230112afeb317b8f8f279c00c664a9c2bc6830`

This map is generated from `COGNITIVE_CONVERGENCE_MASTER_REGISTRY.json`.
It is an architectural index, not proof of runtime readiness.

## Proven Current Flow

```text
input
-> semantics/intention
-> micro-core
-> balance
-> 21D
-> MEMZUM
-> Native Memory
-> 34D/MMONDE
-> source-routing projection
-> C1
-> ContextPacketV2 / IR
-> W1/W2
-> V1.4.12A
-> brody_full_context
-> True Voice
-> final answer
```

## ACTIVE + CONNECTED

| ID | NAME | TYPE | STATUS | CURRENT LOCATION | CURRENT CONSUMER | TARGET | BLOCKER | NEXT ACTION |
|---|---|---|---|---|---|---|---|---|
| c1_cognitive_join | C1 cognitive join | COGNITIVE_SIGNAL | ACTIVE_CONNECTED | apps/obsidia_api/routes/brody.py -> run_real_cognitive_join | ContextPacketV2, brody_full_context | run_real_cognitive_join(...) | - | Keep frozen; update this registry when new projections are added. |
| context_packet_v2 | ContextPacketV2 | PROVENANCE | ACTIVE_CONNECTED | apps/obsidia_api/brody_real_cognitive_join.py | routes/brody.py, V1.4.12A | ContextPacketV2.context_items / source_refs | - | Preserve compactness; add only symbolic markers or bounded refs. |
| ir_candidate | IR candidate | SEMANTIC_LAYER | ACTIVE_CONNECTED | apps/obsidia_api/brody_real_cognitive_join.py | brody_full_context, V1.4.12A | governed_cognitive_projection.ir_candidate | - | Keep readonly; do not promote raw IR into final authority. |
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
| source_pack_routing | source-pack routing | SOURCE_ROUTING | ACTIVE_CONNECTED | runtime_wiring/source_runtime/brody_source_context_bridge.py | C1 cognitive join, ContextPacketV2 | C1 optional precomputed input; ContextPacketV2.source_refs; True Voice source_pack_context | - | Keep raw source content out of C1; extend tests for new families. |
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
| semantic_query_router | semantic query/router | SEMANTIC_LAYER | ACTIVE_PARTIAL | apps/obsidia_api/brody_semantic_query_router.py | Brody pipeline | semantic query snapshot | - | Map whether this should feed C1 directly or remain response-pipeline context. |
| semantic_plan | semantic plan | SEMANTIC_LAYER | ACTIVE_PARTIAL | apps/obsidia_api/brody_semantic_plan.py | Brody pipeline | semantic plan snapshot | - | Map whether this should feed C1 directly or remain response-pipeline context. |
| semantic_representation | semantic representation | SEMANTIC_LAYER | PARTIAL_NEEDS_RECONCILIATION | periphery/language/language_router.py | Brody pipeline | [UNRESOLVED TARGET] | Prove compact non-sovereign payload and current caller count. | Map whether this should feed C1 directly or remain response-pipeline context. |
| intention | intention | SEMANTIC_LAYER | ACTIVE_PARTIAL | apps/obsidia_api/brody_capabilities_intent.py | Brody pipeline | C1 or capability router | Prove compact non-sovereign payload and current caller count. | Map whether this should feed C1 directly or remain response-pipeline context. |
| cognitive_layer_router | Cognitive Layer Router | SEMANTIC_LAYER | PARTIAL_NEEDS_RECONCILIATION | runtime_wiring/source_runtime/capability_path_router.py | Brody pipeline | C1 | Exact C1 hook unresolved, Runtime producer/caller path not yet proven | Audit actual producer, payload shape, caller count, and exact compact C1 hook before any wiring. |
| cic | CIC / cognitive invariants | SEMANTIC_LAYER | ACTIVE_PARTIAL | apps/obsidia_api/brody_cic_context_adapter.py | Brody pipeline | Brody/C1 readonly context | Prove compact non-sovereign payload and current caller count. | Map whether this should feed C1 directly or remain response-pipeline context. |
| c265 | C265 sense to symbolic integration | SEMANTIC_LAYER | ACTIVE_PARTIAL | periphery/language/pre_reasoning_calibrator.py | Brody real response pipeline | pre_reasoning_snapshot.C265 | - | Audit compact C1 projection if any stage is promoted before C1. |
| c266 | C266 symbolic alignment | SEMANTIC_LAYER | ACTIVE_PARTIAL | periphery/language/pre_reasoning_calibrator.py | Brody real response pipeline | pre_reasoning_snapshot.C266 | - | Audit compact C1 projection if any stage is promoted before C1. |
| c273 | C273 divergence detection | SEMANTIC_LAYER | ACTIVE_PARTIAL | periphery/language/pre_reasoning_calibrator.py | Brody real response pipeline | pre_reasoning_snapshot.C273 | - | Audit compact C1 projection if any stage is promoted before C1. |
| c274 | C274 pre-reasoning calibration | SEMANTIC_LAYER | ACTIVE_PARTIAL | periphery/language/pre_reasoning_calibrator.py | Brody real response pipeline | pre_reasoning_snapshot.C274 | - | Audit compact C1 projection if any stage is promoted before C1. |
| c275 | C275 pre-response calibration | SEMANTIC_LAYER | ACTIVE_PARTIAL | periphery/language/pre_response_calibrator.py | Brody real response pipeline | real_response_pipeline.c275 | - | Audit compact C1 projection if any stage is promoted before C1. |
| c276 | C276 pre-action calibration | SEMANTIC_LAYER | ACTIVE_PARTIAL | periphery/language/pre_action_calibrator.py | Brody real response pipeline | real_response_pipeline.c276 | - | Audit compact C1 projection if any stage is promoted before C1. |
| c277 | C277 final sense halo | SEMANTIC_LAYER | ACTIVE_PARTIAL | periphery/language/final_sense_halo.py | Brody real response pipeline | real_response_pipeline.c277 | - | Audit compact C1 projection if any stage is promoted before C1. |
| c278 | C278 action meaning validator | SEMANTIC_LAYER | ACTIVE_PARTIAL | periphery/language/action_meaning_validator.py | Brody real response pipeline | real_response_pipeline.c278 | - | Audit compact C1 projection if any stage is promoted before C1. |
| reverse_os | Reverse OS | LANGUAGE_LAYER | ACTIVE_PARTIAL | apps/obsidia_api/brody_existing_reverse_os_bridge.py | C1 / output layer | reverse_os_projection / ir_candidate | - | Keep separated from KX108 authority; audit exact hook before wiring. |
| os_trad | OS Trad | LANGUAGE_LAYER | ACTIVE_PARTIAL | apps/obsidia_api/os_adapters/os_trad_adapter.py | source routing / output layer | OS_TRAD_REVERSE_OS source family | - | Keep separated from KX108 authority; audit exact hook before wiring. |
| verbatia | VERBATIA | LANGUAGE_LAYER | ACTIVE_PARTIAL | apps/obsidia_api/brody_cognitive_modules_adapter.py | True Voice | True Voice | Runtime implementation and compact hook audit required. | Keep separated from KX108 authority; audit exact hook before wiring. |
| symbolic_signal | symbolic signal | COGNITIVE_SIGNAL | ACTIVE_PARTIAL | apps/obsidia_api/brody_cognitive_micro_core.py | - | micro_core / C1 | Exact dedicated hook unresolved, Potential duplicate projection of an existing micro-core signal | Dedup audit against micro_core. Do not wire separately unless missing material effect is proven. |
| fractal_signal | fractal signal | COGNITIVE_SIGNAL | PARTIAL_NEEDS_RECONCILIATION | apps/obsidia_api/brody_cognitive_micro_core.py | - | C1 / ContextPacketV2 | Exact target hook unresolved | Run targeted audit for payload shape and consumers. |
| temporal_signal | temporal signal | COGNITIVE_SIGNAL | PARTIAL_NEEDS_RECONCILIATION | apps/obsidia_api/brody_cognitive_micro_core.py | - | C1 / ContextPacketV2 | Exact target hook unresolved | Run targeted audit for payload shape and consumers. |
| prediction_signal | prediction signal | COGNITIVE_SIGNAL | PARTIAL_NEEDS_RECONCILIATION | apps/obsidia_api/brody_cognitive_micro_core.py | - | C1 / ContextPacketV2 | Exact target hook unresolved | Run targeted audit for payload shape and consumers. |
| weak_signal_path | weak-signal path | COGNITIVE_SIGNAL | ACTIVE_PARTIAL | apps/obsidia_api/brody_cognitive_micro_core.py | - | micro_core / C1 | Exact dedicated hook unresolved, Potential duplicate projection of an existing micro-core signal | Dedup audit against micro_core. Do not wire separately unless missing material effect is proven. |
| symbolic_fractal_memory | symbolic/fractal memory | COGNITIVE_SIGNAL | PARTIAL_NEEDS_RECONCILIATION | apps/obsidia_api/brody_cognitive_micro_core.py | - | C1 / ContextPacketV2 | Exact target hook unresolved | Run targeted audit for payload shape and consumers. |
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

## BLOCKED

| ID | NAME | TYPE | STATUS | CURRENT LOCATION | CURRENT CONSUMER | TARGET | BLOCKER | NEXT ACTION |
|---|---|---|---|---|---|---|---|---|
| lyapunov | Lyapunov | SCIENCE_REASONING | BLOCKED_BY_PROOF | periphery/math_core/lyapunov.py | - | [UNRESOLVED TARGET] | formal proof gap | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| openjarvis | OpenJarvis/Jarvis cognitive surface | ADAPTER | BLOCKED_BY_DEPENDENCY | tests/cli/test_openjarvis_cognitive_pilot_v0.py | CLI/surface | CLI/surface | missing openjarvis package in current environment | Keep boundary readonly and update registry after any dependency/provenance audit. |

## DOCUMENTED / NOT RUNTIME

| ID | NAME | TYPE | STATUS | CURRENT LOCATION | CURRENT CONSUMER | TARGET | BLOCKER | NEXT ACTION |
|---|---|---|---|---|---|---|---|---|
| ssr | SSR | LANGUAGE_LAYER | DOCUMENTED_NOT_RUNTIME | _source_packs/REVERSE_OS_INTERLANGUAGE_CANON_V1/evidence/interlanguage_transduction_v1.md | - | [UNRESOLVED TARGET] | Runtime implementation and compact hook audit required. | Keep separated from KX108 authority; audit exact hook before wiring. |
| lu_mh | LU-MH | LANGUAGE_LAYER | DOCUMENTED_NOT_RUNTIME | _source_packs/REVERSE_OS_INTERLANGUAGE_CANON_V1/evidence/architecture_narrative_reverse_os.txt | - | [UNRESOLVED TARGET] | Runtime implementation and compact hook audit required. | Keep separated from KX108 authority; audit exact hook before wiring. |
| clavage | Clavage | LANGUAGE_LAYER | DOCUMENTED_NOT_RUNTIME | _source_packs/REVERSE_OS_INTERLANGUAGE_CANON_V1/evidence/architecture_protocoles_os_cognitif.txt | - | [UNRESOLVED TARGET] | Runtime implementation and compact hook audit required. | Keep separated from KX108 authority; audit exact hook before wiring. |
| oban | OBAN | LANGUAGE_LAYER | DOCUMENTED_NOT_RUNTIME | _source_packs/REVERSE_OS_INTERLANGUAGE_CANON_V1/evidence/architecture_protocoles_os_cognitif.txt | - | [UNRESOLVED TARGET] | Runtime implementation and compact hook audit required. | Keep separated from KX108 authority; audit exact hook before wiring. |
| shannon | Shannon | SCIENCE_REASONING | DOCUMENTED_NOT_RUNTIME | _source_discovery/OBSIDIA_NPL_PACK_AUDIO_ENTROPY_AUDIT_V1/ | - | [UNRESOLVED TARGET] | Proof/runtime boundary audit required before wiring. | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
| negentropy | negentropy | SCIENCE_REASONING | DOCUMENTED_NOT_RUNTIME | _source_discovery/OBSIDIA_NPL_PACK_AUDIO_ENTROPY_AUDIT_V1/ | - | [UNRESOLVED TARGET] | Proof/runtime boundary audit required before wiring. | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |

## LEGACY / SUPERSEDED

| ID | NAME | TYPE | STATUS | CURRENT LOCATION | CURRENT CONSUMER | TARGET | BLOCKER | NEXT ACTION |
|---|---|---|---|---|---|---|---|---|
| graphiti | Graphiti residual memory layer | LEGACY | SUPERSEDED | apps/obsidia_api/brody_graphiti_guard.py | NONE_DOCUMENT_ONLY | NONE_DOCUMENT_ONLY | - | Keep boundary readonly and update registry after any dependency/provenance audit. |

## UNKNOWN / NEEDS AUDIT

| ID | NAME | TYPE | STATUS | CURRENT LOCATION | CURRENT CONSUMER | TARGET | BLOCKER | NEXT ACTION |
|---|---|---|---|---|---|---|---|---|
| branches | Branches | KNOWLEDGE_INDEX | SOURCE_FOUND_IMPLEMENTATION_UNKNOWN | periphery/OBSIDIA_V4_STRUCTURED_FULL/ | - | SOURCE_ROUTING | No per-child runtime contract proven | Register child only when it has distinct code or audited adapter target. |
| subbranches | Subbranches | KNOWLEDGE_INDEX | SOURCE_FOUND_IMPLEMENTATION_UNKNOWN | periphery/OBSIDIA_V4_STRUCTURED_FULL/ | - | SOURCE_ROUTING | No per-child runtime contract proven | Register child only when it has distinct code or audited adapter target. |
| pepites | Pepites | KNOWLEDGE_INDEX | SOURCE_FOUND_IMPLEMENTATION_UNKNOWN | periphery/OBSIDIA_V4_STRUCTURED_FULL/ | - | SOURCE_ROUTING | No per-child runtime contract proven | Register child only when it has distinct code or audited adapter target. |
| rave | RAVE | LANGUAGE_LAYER | UNKNOWN | - | - | [UNRESOLVED TARGET] | Runtime implementation and compact hook audit required. | Keep separated from KX108 authority; audit exact hook before wiring. |
| aig_cmai | AIG / CMAI | DOCUMENTED_CONCEPT | UNKNOWN | - | - | [UNRESOLVED TARGET] | Proof/runtime boundary audit required before wiring. | Audit exact consumer and prove non-sovereign compact payload before any new C1 wiring. |
