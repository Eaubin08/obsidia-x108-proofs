# Proof Index - Obsidia X-108

> Date: 2026-05-30 | Lean toolchain: leanprover/lean4:v4.28.0

## Formal proofs - Lean 4 (LEAN_PROVEN)

These theorems are present in the repo and compile under `lake build`. They constitute the formal foundation of the X108 kernel.

| Theorem | File | Property |
|---|---|---|
| `X108_no_act_before_tau` | `proofs/lean/Obsidia/TemporalKernel.lean:17` | No ACT emitted before tau elapses (irr=true, elapsed<tau -> HOLD) |
| `X108_after_tau_equals_base` | `proofs/lean/Obsidia/TemporalKernel.lean:26` | After tau, kernel output equals the base decision function |
| `X108_kernel_never_blocks` | `proofs/lean/Obsidia/TemporalKernel.lean:37` | Kernel never emits BLOCK (only HOLD or ACT possible) |
| `X108_reversible_equals_base` | `proofs/lean/Obsidia/TemporalKernel.lean:51` | Reversible decisions (irr=false) always equal base |
| `X108_irreversible_after_tau_equals_base` | `proofs/lean/Obsidia/TemporalKernel.lean:56` | Irreversible after tau elapsed equals base |
| `D1_determinism` | `proofs/lean/Obsidia/Basic.lean` | Decision function is deterministic |
| `E2_no_act_below_threshold` | `proofs/lean/Obsidia/Basic.lean` | No ACT emitted below decision threshold theta |
| `Refinement.x108_never_blocks` | `proofs/lean/Obsidia/Refinement.lean` | Refined kernel never blocks |
| `Refinement.refined_not_block` | `proofs/lean/Obsidia/Refinement.lean` | Refined decision is not BLOCK |
| `P15_Immutability_Strong` | `proofs/lean/Obsidia/Sensitivity.lean` | Merkle immutability (strong form) |
| `P13_Immutability` | `proofs/lean/Obsidia/Seal.lean` | Seal immutability |
| `aggregate4_fail_closed` | `proofs/lean/Obsidia/Consensus.lean` | Consensus fails closed under quorum loss |
| `canonicalize_preserves_nonneg` | `proofs/lean/Obsidia/TemporalBridge.lean` | Canonicalization preserves non-negativity |
| `skew_negative_implies_hold` | `proofs/lean/Obsidia/TemporalBridge.lean` | Negative temporal skew implies HOLD |

See [LEAN_THEOREMS.md](LEAN_THEOREMS.md) for verbatim TemporalKernel.lean source.

### Verify locally

```bash
cd proofs/lean
lake build
# Expect: exit 0, no errors

lake env lean Obsidia/TemporalKernel.lean
# Expect: no output (clean compilation)
```

---

## Python test validation (PYTHON_TEST_ONLY)

These properties are validated by automated tests, not by Lean formal proofs.

| Property | Test file(s) | Approx. count | Status (2026-05-30) |
|---|---|---|---|
| `KX108_ONLY` in all Sigma packets | `tests/sigma/test_f62_*.py` | 650+ | PASS |
| No ACT from Sigma layer | `tests/sigma/test_f73_*.py` | - | PASS |
| No ACT from Brody | `tests/api/test_brody_authority_escalation_no_act.py` | - | PASS |
| `readonly=True` in Sigma responses | `tests/api/test_f63_*.py` | 195 | PASS |
| Bus sovereignty (`KX108_ONLY`) | `tests/api/test_f65_*.py` | 85 | PASS |
| `graphiti_write=False` in all outputs | `tests/sigma/test_f70_*.py` | - | PASS |
| `memory_write=False` in all outputs | `tests/api/test_no_memory_write_api.py` | - | PASS |
| Compact contract (`deep_snapshots_omitted`) | `tests/api/test_output_envelope_*.py` | 9 | PASS |
| Auth + rate-limit (F76b) | `tests/api/test_f76b_auth_rate_limit_*.py` | 14 | PASS |
| Brody voice_source priority (memory chain) | `tests/api/test_brody_true_voice_memory_chain_final_answer.py` | 4 | PASS |
| Blockchain fraud-check envelope | `tests/api/test_output_envelope_blockchain_fraud_check.py` | 9 | PASS |

**Full tests/api: 1973 PASS, 0 failed (2026-05-30, 8566.23s / 2:22:46). Targeted non-regression: 1203 PASS, 0 failed (2026-05-30, 196.49s).**

---

## TLA+ specifications

| Spec | File | Status |
|---|---|---|
| X108 temporal safety | `formal/tla/X108_MC.tla` | FORMAL_TLA - specification present |
| Distributed X108 | `formal/tla/DistributedX108.tla` | FORMAL_TLA - specification present |
| RFC3161 spec | `formal/tla/RFC3161Spec.tla` | FORMAL_TLA - specification present |
| TLA verification spec | `formal/tla/TLAVerificationSpec.tla` | FORMAL_TLA - specification present |

**Note:** TLC was not re-executed in this session. Do not claim "TLA+ verified" without re-running TLC:

```bash
java -jar tla2tools.jar -config formal/tla/X108_MC.cfg formal/tla/X108_MC.tla
```

---

## RFC3161 timestamps

- Directory: `traces/rfc3161/`
- Format: `.tsq` (requests), `.tsr` (responses), `verify.json` (results)
- Status this session: file presence not re-verified. Do not claim "RFC3161 current" without running `openssl ts -verify`.

---

## Merkle seals

- Verification script: `proofs/verify_merkle.py`
- Lean theorem: `P15_Immutability_Strong` in `Sensitivity.lean`
- Status this session: NOT re-verified. Do not claim "Merkle current" without re-running `verify_merkle.py`.

---

## What is NOT formally proven (Lean)

The following properties are validated by Python tests only:

- Sigma packet sovereignty (`KX108_ONLY`) - PYTHON_TEST_ONLY
- Bus bridge sovereignty - PYTHON_TEST_ONLY
- Brody no-ACT - PYTHON_TEST_ONLY
- `graphiti_write=False` at runtime - PYTHON_TEST_ONLY
- `P107 Lyapunov stability` - DOC_ONLY (no tests)
- `P161 Calibration energetique` - DOC_ONLY (no tests)

These are explicitly declared as FUTURE_FORMAL_TARGET in `docs/architecture/F74_F77_FINALIZATION_AUDIT.md`.

---

_Obsidia X-108 Proof Index | 2026-05-30 | KX108_ONLY | No commit / No push_

