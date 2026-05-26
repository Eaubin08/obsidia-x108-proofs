# BFCL_METADATA_SMOKE_PASS_REPORT

STATUS=PASS_WITH_VERSION_COMMAND_BUG

BENCHMARK=BFCL
PACKAGE=bfcl-eval
PINNED_VERSION=2025.12.17

VALIDATED:
BFCL_INSTALL=PASS
BFCL_IMPORT=PASS
SOUNDFILE_PATCH=PASS
BFCL_CLI_HELP=PASS
BFCL_MODELS=PASS
BFCL_TEST_CATEGORIES=PASS

NON_BLOCKING_ISSUE:
BFCL_VERSION_COMMAND=FAIL
CAUSE=PackageNotFoundError for package metadata name "bfcl"
INTERPRETATION=CLI metadata bug, not benchmark blocker.
The installed package is bfcl-eval.

AVAILABLE_COMMANDS:
models
test-categories
generate
results
evaluate
scores
version

KEY_CATEGORIES:
simple_python
simple_java
simple_javascript
multiple
parallel
parallel_multiple
irrelevance
live_simple
live_multiple
live_parallel
live_irrelevance
multi_turn_base
multi_turn_miss_func
multi_turn_miss_param
multi_turn_long_context
memory_kv
memory_vector
memory_rec_sum
web_search_base
web_search_no_snippet
format_sensitivity

BOUNDARY:
NO_TRAINING=true
NO_FINE_TUNING=true
NO_KERNEL_MUTATION_BY_BENCHMARK=true
BENCHMARK_EXTERNAL_EVALUATION_ONLY=true
DECISION_AUTHORITY=KX108_ONLY

INTERPRETATION:
BFCL is operational enough for metadata exploration and future function-calling/tool-calling benchmark runs.
This validates benchmark availability, not yet model performance or Obsidia governance superiority.

NEXT:
Inspect generate/evaluate/results help.
Then run a micro BFCL simple_python generation/evaluation if API key/model configuration is available.
