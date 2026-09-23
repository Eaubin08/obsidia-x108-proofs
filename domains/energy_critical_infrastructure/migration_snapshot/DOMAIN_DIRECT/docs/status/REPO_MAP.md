# Repository Map

Root:
- README.md
- P1_FREEZE_NOTE.md
- PUBLIC_STATUS.md
- REPO_MAP.md
- KNOWN_LIMITS.md
- run_all_proofs.ps1

Formal proof perimeter:
- proofs/lean/
- formal/tla/

Executable verification perimeter:
- proofs/verify_all.py
- proofs/verify_decision.py
- proofs/verifiers/

Public Sigma perimeter:
- sigma/run_pipeline.py
- sigma/sigma_monitor.py
- sigma/tests/
- sigma/examples/

QA perimeter:
- qa/cross-platform/test_rfc3161_cross_platform.py
- qa/cross-platform/test_rfc3161_anchor_schema.py

Expected public entry path:
1. read README.md
2. run .\run_all_proofs.ps1
3. inspect PUBLIC_STATUS.md
4. inspect P1_FREEZE_NOTE.md