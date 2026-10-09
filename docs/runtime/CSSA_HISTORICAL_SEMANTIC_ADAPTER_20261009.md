# CSSA historical → Universal semantic adaptation, V0

2026-10-09. CSSA branch only: `feat/cssa-v01-active`.

## Implemented

`periphery/cssa_historical_semantic_adapter_v0.py` accepts actual historical F3F/F3G dataclass-shaped assessments from six source types: `StressAssessmentV0`, `ContractAssessmentV0`, `ComplianceAssessmentV0`, `InstitutionalAssessmentV0`, `RootCauseAssessmentV0`, `BuvetteAssessmentV0`. Captures source family, source identifier, date, owner role, evidence references, original expected gate, contradictions, unknowns, risks, and resource conflict indicator; produces a CSSA-only semantic work proposal.

The original assessment is **not** a native case, and its `expected_gate=ALLOW` **cannot authorize a mutation**. Every projected case remains `HOLD` or `BLOCK` with `canonical_intake_allowed=False`, `action_candidate=None`, `approved_by=None`, `allowed_to_act=False`, `KX108_ONLY`. This is an intentional **read-only contract boundary** rather than a counterfeit E2E integration. No source is copied into the Universal runtime. An adapter to a fully evidence-bound native intake must be separately engineered and gated before claiming a F3G→native E2E proof.

## Evidence and test scope

Historical source GitHub: `Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-`, branch `feat/f3g-j-cssa-matchday-buvette-restauration-v0`. Exact historical function signatures and original model names are recorded in `CSSA_F3F_F3G_UNIVERSAL_EXACT_CONTRACT_MATRIX_20261009.md`. Tests in `tests/test_cssa_historical_semantic_adapter_v0.py` use **structural test replicas** of source dataclasses to check the projection boundary, not imported original implementations or reruns of the 904-event season.

13 new tests; prior user-verified baseline 152 passed, 1 skipped. Expected focused total 165 passed, 1 skipped **only if tests pass on Windows**. Do not claim current pass until actually executed. Tests for source implementation in its original repo, exact HEAD pinning, richer field mapping, safe native intake, and eleven-role matrix are still pending.

## Next work

Resolve original source HEAD, test in an isolated clone using original fixtures; implement an explicit transport and evidence/binding handshake between repo outputs and native intake. Do not autogenerate dates, external targets, source authority, human approval, or ACTION. Refuse to convert F3G métier `ALLOW` into KX108 authority. Keep no real club connection/no network/no main push.
