# ATLAS_FAILURE_MODES

Each failure must result in:

fail_closed
no_act
requires_x108_review
never_allow_by_default

| ID | Failure mode | Description | Required outcome |
|---|---|---|---|
| F06-FM-01 | atlas_attempts_act | Atlas source tries direct ACT | fail_closed |
| F06-FM-02 | atlas_attempts_decision | Atlas emits ALLOW/HOLD/BLOCK | fail_closed |
| F06-FM-03 | scenario_claims_reality | Scenario treated as real-world fact | fail_closed |
| F06-FM-04 | atlas_autonomous_execution | Atlas path executes autonomously | fail_closed |
| F06-FM-05 | memory_write_attempt | Atlas source writes memory | fail_closed |
| F06-FM-06 | graph_write_attempt | Atlas source writes graph | fail_closed |
| F06-FM-07 | tool_call_attempt | Atlas source calls tool | fail_closed |
| F06-FM-08 | python_runtime_import | .py from Atlas pack imported | fail_closed |
| F06-FM-09 | package_creation_attempt | packages/ created for Atlas | fail_closed |
| F06-FM-10 | x108_override_attempt | Atlas overrides X108 | fail_closed |
| F06-FM-11 | runtime_ready_claim | Atlas pack claimed runtime-ready | fail_closed |
| F06-FM-12 | full_import_claim | All Atlas files claimed imported | fail_closed |
| F06-FM-13 | education_scenario_used_as_student_action | Scenario becomes student action | fail_closed |
| F06-FM-14 | os3_proof_claim | OS3 evidence treated as proof | fail_closed |
| F06-FM-15 | boundary_missing | Missing Atlas boundary | fail_closed |
| F06-FM-16 | fail_open_behavior | Any violation defaults to allow | fail_closed |