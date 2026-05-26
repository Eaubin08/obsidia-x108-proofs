# BFCL_METADATA_AND_COMMAND_HELP_SMOKE_PASS_REPORT

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
BFCL_GENERATE_HELP=PASS
BFCL_EVALUATE_HELP=PASS
BFCL_RESULTS_HELP=PASS

NON_BLOCKING_ISSUE:
BFCL_VERSION_COMMAND=FAIL
CAUSE=PackageNotFoundError for metadata name "bfcl"
INTERPRETATION=CLI metadata bug. Installed package is bfcl-eval.

AVAILABLE_COMMANDS:
models
test-categories
generate
results
evaluate
scores
version

PRIMARY_TEST_CATEGORY_FOR_NEXT_STEP:
simple_python

BOUNDARY:
NO_TRAINING=true
NO_FINE_TUNING=true
NO_KERNEL_MUTATION_BY_BENCHMARK=true
BENCHMARK_EXTERNAL_EVALUATION_ONLY=true
DECISION_AUTHORITY=KX108_ONLY

INTERPRETATION:
BFCL is operational for metadata discovery and command-level benchmark preparation.
This validates the tool-calling benchmark harness availability, not yet model performance or Obsidia governance superiority.

NEXT:
Run a first simple_python generation/evaluation using a configured API key and one model.
