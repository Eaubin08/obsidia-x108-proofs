# PROOF_READINESS_GATE_SPEC
Status: SOURCE_ORGANIZED
Authority: KX108_ONLY
Source Paths:
- docs/PROOF_SCOPE.md\n- docs/V3_V4_GAP_ANALYSIS.md
Source Status: SOURCE_ORGANIZED
Scope: Gate de readiness avant claim de preuve.
Allowed:
- Lean proof = proofs/lean/ compilé\n- TLA+ = formal/tla/ TLC pass\n- Python = 194 tests pass
Forbidden:
- Python PASS = preuve formelle\n- Claim preuve sans source Lean
Inputs: Domain sources
Outputs: Spec contractuelle
Metrics: N/A
Invariants: KX108_ONLY pour toute décision
X108 Boundary: KX108_ONLY
Tests Required: À définir en Plan 3
Proof Expected: Python test
Runtime Status: SOURCE_CANON
Claim-Scope Notes: Voir 00_SCOPE_DISCIPLINE/
Open Questions: À préciser en Plan 3
