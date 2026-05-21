OBSIDIA_X108_EXTERNAL_BIGTECH_BENCHMARKS_WORKSPACE

X108_ROOT=C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs
BENCH_ROOT=C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\_external_benchmarks
AUDIT_ROOT=C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\_local_audits\EXTERNAL_BENCHMARKS

NO_TRAINING=true
NO_FINE_TUNING=true
NO_WEIGHT_UPDATE=true
SAME_BASE_MODEL=true
SAME_TASK_SET=true
SAME_PROMPT_BUDGET=true

RUN_A=baseline_agent
RUN_B=baseline_agent_plus_obsidia_x108_governance

PRIMARY_ORDER:
1. SWE-bench
2. Terminal-Bench
3. BFCL
4. AgentDojo
5. tau-bench / tau3-bench
6. WebArena
7. GAIA
8. OSWorld

INVARIANTS:
DECISION_AUTHORITY=KX108_ONLY
NO_KERNEL_MUTATION_BY_BENCHMARK=true
BENCHMARKS_ARE_EXTERNAL_EVALUATION_ONLY=true
NO_TRAINING=true
NO_FINE_TUNING=true
