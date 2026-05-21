# SWE_BENCH_WSL_GOLD_SMOKE_FREEZE

STATUS=VALIDATED_LOCAL_SMOKE_PASS

This freeze validates that SWE-bench can run from Ubuntu WSL on the Obsidia/X108 workstation.

Validated run:
- benchmark: SWE-bench Lite
- prediction mode: gold
- instance: sympy__sympy-20590
- total instances: 1
- completed: 1
- resolved: 1
- errors: 0

Boundary:
- benchmark only
- no training
- no fine-tuning
- no X108 kernel mutation
- decision authority remains KX108_ONLY
