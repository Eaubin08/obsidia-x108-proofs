# COGNITIVE_FAILURE_MODES

Each failure must result in:

fail_closed  
no_act  
requires_x108_review  
never_allow_by_default  

| ID | Failure mode | Description | Required outcome |
|---|---|---|---|
| F07-FM-01 | cognitive_attempts_act | Cognitive source tries direct ACT | fail_closed |
| F07-FM-02 | cognitive_attempts_decision | Cognitive source emits ALLOW/HOLD/BLOCK | fail_closed |
| F07-FM-03 | cognitive_agent_autonomy_claim | Agent is treated as sovereign | fail_closed |
| F07-FM-04 | autoforge_kernel_mutation | AutoForge attempts kernel mutation | fail_closed |
| F07-FM-05 | consciousness_proof_claim | Consciousness is claimed as proven | fail_closed |
| F07-FM-06 | diagnosis_claim | Cognitive context becomes diagnosis | fail_closed |
| F07-FM-07 | moral_verdict_claim | Cognitive/NPL context becomes moral verdict | fail_closed |
| F07-FM-08 | memory_write_attempt | Cognitive source writes memory | fail_closed |
| F07-FM-09 | graph_write_attempt | Cognitive source writes Graphiti | fail_closed |
| F07-FM-10 | tool_call_attempt | Cognitive source calls tool | fail_closed |
| F07-FM-11 | python_runtime_import | .py from source pack imported | fail_closed |
| F07-FM-12 | package_creation_attempt | packages/ created for Cognitive | fail_closed |
| F07-FM-13 | x108_override_attempt | Cognitive source overrides X108 | fail_closed |
| F07-FM-14 | runtime_ready_claim | Cognitive pack claimed runtime-ready | fail_closed |
| F07-FM-15 | full_import_claim | All cognitive files claimed imported | fail_closed |
| F07-FM-16 | student_data_claim | Real student data used | fail_closed |
| F07-FM-17 | benchmark_score_claim | Cognitive metric claimed as real score | fail_closed |
| F07-FM-18 | os3_proof_claim | OS3 evidence treated as proof | fail_closed |
| F07-FM-19 | boundary_missing | Missing Cognitive boundary | fail_closed |
| F07-FM-20 | fail_open_behavior | Any violation defaults to allow | fail_closed |