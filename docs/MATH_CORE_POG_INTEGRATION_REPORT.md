# Math Core / Proof of Governance Integration Report — V4

**Date:** 2026-05-19

## Overview

The Math Core layer provides a Python-level specification of the Lyapunov Governance Function and Proof of Governance. These are **not Lean-proven** — they are Python specifications used for runtime governance scoring.

## Lyapunov Governance Function

```
L(x) = α*ΔE + β*ΔC + γ*V_inst + δ*Δτ - η*I_ctrl

α=0.25  ΔE    = thermo debt (energy imbalance)
β=0.20  ΔC    = computational debt
γ=0.30  V_inst = instantaneous violence / instability
δ=0.15  Δτ    = timeline drift
η=0.10  I     = intent / control correction

Stable set S: |L(x)| < 0.05
Partition X_B: V_inst > 0.5  → BLOCK
Partition X_H: Δτ > 0.5     → HOLD
Partition X_A: L stable      → ALLOW
```

## Proof of Governance

```
ProofOfGovernance(x) iff:
  (1) J_Θ(θ) ∈ Ω  — theta.x108_gate ∈ {ALLOW, HOLD, BLOCK}
  AND
  (2) L(x) = 0     — lyapunov.is_stable = True
  AND
  (3) Verify(ticket) — OS3 ticket has non-empty input_hash, output_hash, trace_hash, merkle_root
```

## Multi-Agent Consensus

Priority: BLOCK > HOLD > ALLOW. A single BLOCK from any agent blocks the consensus result.

## Files

- `periphery/math_core/governed_state.py`
- `periphery/math_core/lyapunov.py`
- `periphery/math_core/governance_partition.py`
- `periphery/math_core/proof_of_governance.py`
- `periphery/math_core/multi_agent_consensus.py`
- `periphery/math_core/trust_path.py`
