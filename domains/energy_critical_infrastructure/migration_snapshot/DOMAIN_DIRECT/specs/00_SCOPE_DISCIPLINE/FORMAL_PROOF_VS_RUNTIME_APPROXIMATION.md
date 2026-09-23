# FORMAL_PROOF_VS_RUNTIME_APPROXIMATION

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `docs/PROOF_SCOPE.md`
- `periphery/math_core/lyapunov.py`
- `periphery/math_core/proof_of_governance.py`
- `periphery/math_core/governed_state.py`

Source Status: SOURCE_CANON + PYTHON_SPEC

Scope:
Distinguer clairement preuve formelle (Lean 4 / TLA+) et approximation runtime Python.

Allowed:
- "Lean 4 proofs sont dans proofs/lean/ — LEAN_PROVEN"
- "TLA+ specs sont dans formal/tla/ — FORMAL_TLA"
- "Lyapunov, PoG, governed_state sont des specs Python — PYTHON_SPEC"
- "FORMAL_PROOF_PENDING pour math_core/"

Forbidden:
- "Lyapunov est formellement prouvé en Lean"
- "ProofOfGovernance = preuve formelle"
- "Python PASS = LEAN_PROVEN"
- "runtime approximation = preuve"

Inputs: PROOF_SCOPE_SOURCE.md + LYAPUNOV_POG_SOURCE.md

Outputs: Tableau de correspondance type de preuve ↔ fichier ↔ claim autorisé

Metrics: N/A

Invariants:
- LEAN_PROVEN ≠ PYTHON_SPEC
- FORMAL_TLA ≠ RUNTIME_CODE
- "194 tests pass" ≠ "formellement prouvé"

X108 Boundary: KX108_ONLY

Tests Required:
- Vérifier que les docs publiques n'utilisent pas "prouvé" pour du Python

Proof Expected: LEAN_PROVEN pour noyau X108 uniquement

Runtime Status: DOC_ONLY

Claim-Scope Notes:
Le plan de formalisation Lean pour Lyapunov/PoG est dans 03_ENTROPY_DISCIPLINE/LYAPUNOV_RUNTIME_TO_FORMAL_PROOF_PLAN.md

Open Questions:
- Quand sera lancée la formalisation Lean de math_core/ ?
