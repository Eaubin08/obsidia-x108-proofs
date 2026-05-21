# Math Core Module

**Status:** FIRST_CLASS_X108_MODULE — COMPUTATIONAL ONLY
**Source:** `periphery/math_core/` (6 modules)
**Tests:** `tests/periphery/test_lyapunov_*.py` + `tests/periphery/test_proof_of_governance.py`

## Modules

| Module | Role |
|--------|------|
| `governed_state.py` | GovernedStateVector + DecisionEnvelopeTheta |
| `lyapunov.py` | Lyapunov stability computation |
| `proof_of_governance.py` | ProofOfGovernance — validates theta/omega mapping |
| `multi_agent_consensus.py` | Multi-agent consensus priority |
| `trust_path.py` | Trust path computation |
| `governance_partition.py` | Governance partition logic |

## Sovereignty Invariants
- Math core is computational, never decisional
- PoG validates but does not authorize
- No module emits ACT
