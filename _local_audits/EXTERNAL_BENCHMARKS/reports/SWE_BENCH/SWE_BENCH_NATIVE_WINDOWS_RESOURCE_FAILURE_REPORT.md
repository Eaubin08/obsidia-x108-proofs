SWE_BENCH_NATIVE_WINDOWS_SMOKE_REPORT

STATUS=FAIL_EXPECTED_ON_NATIVE_WINDOWS
INSTALL_STATUS=PASS
SMOKE_STATUS=FAIL
ERROR=ModuleNotFoundError: No module named 'resource'

CAUSE:
SWE-bench harness imports Unix/Linux resource module.
This module is not available in native Windows Python.

INTERPRETATION:
This is not an Obsidia/X108 failure.
This is not a kernel failure.
This is not a benchmark logic failure.
This is an OS/runtime compatibility boundary.

NEXT:
Run SWE-bench smoke through WSL/Linux or Linux container.

INVARIANTS:
DECISION_AUTHORITY=KX108_ONLY
NO_KERNEL_MUTATION_BY_BENCHMARK=true
BENCHMARKS_ARE_EXTERNAL_EVALUATION_ONLY=true
NO_TRAINING=true
NO_FINE_TUNING=true
