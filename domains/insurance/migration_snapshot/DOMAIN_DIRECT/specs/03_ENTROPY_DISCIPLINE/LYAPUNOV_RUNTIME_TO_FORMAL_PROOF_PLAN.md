# LYAPUNOV_RUNTIME_TO_FORMAL_PROOF_PLAN

Status: FORMAL_PROOF_PENDING
Authority: KX108_ONLY

Source Paths:
- `periphery/math_core/lyapunov.py`
- `periphery/math_core/proof_of_governance.py`

Source Status: PYTHON_SPEC

Scope: Plan de formalisation Lean pour les métriques Lyapunov et ProofOfGovernance.

Allowed:
- "lyapunov.py est une spec Python — la formalisation Lean est future"
- "Plan 3+ : traduire lyapunov.py en Lean 4"

Forbidden:
- "Lyapunov est formellement prouvé en Lean"
- "ProofOfGovernance = preuve formelle"

Inputs: `periphery/math_core/lyapunov.py`, `proof_of_governance.py`
Outputs: Spec Lean future (Plan 3+)

Metrics: N/A

Invariants:
- Tant que `proofs/lean/` ne contient pas de preuve Lyapunov → FORMAL_PROOF_PENDING
- Python spec = approximation runtime — pas preuve formelle

X108 Boundary: KX108_ONLY
Tests Required: Python tests existants (tests/periphery/)
Proof Expected: FORMAL_PROOF_PENDING — cible Plan 3+
Runtime Status: PYTHON_SPEC
Claim-Scope Notes: Ne pas affirmer stabilité Lyapunov formelle tant que Plan 3+ non livré.
Open Questions: Qui formalise en Lean ? Quel calendrier ?
