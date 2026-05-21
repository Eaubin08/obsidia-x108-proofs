# BRODY_BENCHMARK_BINDING_MATRIX

STATUS=PLANNED_BINDING_LAYER
NO_EXTERNAL_LLM=true
NO_TRAINING=true
NO_FINE_TUNING=true
DECISION_AUTHORITY=KX108_ONLY

## Current benchmark status

| Benchmark | Harness status | Brody binding status | Next adapter |
|---|---:|---:|---|
| SWE-bench | VALIDATED_LOCAL_SMOKE_PASS | NOT_BOUND_TO_BRODY | swebench_brody_predictions_adapter |
| Terminal-Bench | VALIDATED_LOCAL_SMOKE_PASS | NOT_BOUND_TO_BRODY | terminal_bench_brody_custom_agent |
| BFCL | METADATA_AND_COMMAND_HELP_READY | NOT_BOUND_TO_BRODY | bfcl_brody_result_adapter |
| AgentDojo | NOT_STARTED | NOT_BOUND_TO_BRODY | agentdojo_brody_security_adapter |
| tau-bench / tau3 | NOT_STARTED | NOT_BOUND_TO_BRODY | taubench_brody_policy_adapter |
| WebArena | NOT_STARTED | NOT_BOUND_TO_BRODY | webarena_brody_action_guard |
| GAIA | NOT_STARTED | NOT_BOUND_TO_BRODY | gaia_brody_tool_context_adapter |
| OSWorld | NOT_STARTED | NOT_BOUND_TO_BRODY | osworld_brody_desktop_guard |

## Binding principle

Benchmark test case
-> Brody adapter
-> Brody local readonly response
-> normalization into benchmark format
-> benchmark evaluator
-> audit report
-> manifest
-> freeze

## Boundary

Brody can:
- read context
- answer
- propose
- refuse
- emit structured candidate output

Brody cannot:
- decide ACT
- mutate X108
- claim kernel authority
- call tools without permission
- bypass X108

## Priority

1. BFCL Brody adapter
2. Terminal-Bench Brody custom agent
3. SWE-bench Brody predictions adapter
4. AgentDojo Brody security adapter
5. tau-bench policy adapter
