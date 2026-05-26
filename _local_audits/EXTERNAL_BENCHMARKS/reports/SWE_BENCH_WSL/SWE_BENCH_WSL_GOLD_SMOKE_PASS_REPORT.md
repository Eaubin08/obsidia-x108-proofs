# SWE_BENCH_WSL_GOLD_SMOKE_PASS_REPORT

STATUS=PASS

BENCHMARK=SWE-bench Lite
RUN_ID=obsidia_x108_validate_gold_smoke_wsl
PREDICTIONS=gold
INSTANCE=sympy__sympy-20590

RESULTS:
TOTAL_INSTANCES=1
INSTANCES_SUBMITTED=1
INSTANCES_COMPLETED=1
INSTANCES_INCOMPLETE=0
INSTANCES_RESOLVED=1
INSTANCES_UNRESOLVED=0
EMPTY_PATCHES=0
ERRORS=0
UNSTOPPED_CONTAINERS=0
UNREMOVED_IMAGES=0

INTERPRETATION:
SWE-bench is now operational in Ubuntu WSL.
Native Windows failed because of missing Unix resource module.
WSL/Linux path is validated.

OBSIDIA/X108 STATUS:
NO_TRAINING=true
NO_FINE_TUNING=true
NO_WEIGHT_UPDATE=true
BENCHMARK_EXTERNAL_EVALUATION_ONLY=true
NO_KERNEL_MUTATION_BY_BENCHMARK=true
DECISION_AUTHORITY=KX108_ONLY

NEXT:
Run baseline agent.
Then run same agent through Obsidia/X108 governance wrapper.
Compare task success, unsafe mutation, unauthorized file edit, audit trace completeness and replayability.
