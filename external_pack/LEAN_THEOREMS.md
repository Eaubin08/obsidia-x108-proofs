# Lean 4 Theorems - Obsidia X-108 Temporal Kernel

> Source: `proofs/lean/Obsidia/TemporalKernel.lean`
> Toolchain: `leanprover/lean4:v4.28.0`
> Lakefile: `proofs/lean/lakefile.lean`

This file contains the verbatim Lean 4 source of `TemporalKernel.lean`, which establishes the five core theorems of the X108 temporal safety kernel.

## Verbatim source

```lean
import Obsidia.Basic

namespace Obsidia
namespace TemporalKernel

def beforeTau (tau : Nat) (elapsed : Nat) (irr : Bool) : Bool :=
  irr && decide (elapsed < tau)

def decideX108 (tau : Nat) (metrics : Metrics) (theta : Rat) (irr : Bool) (elapsed : Nat) : Decision :=
  match beforeTau tau elapsed irr with
  | true  => Decision.HOLD
  | false => decision metrics theta

def decide3X108 (tau : Nat) (metrics : Metrics) (theta : Rat) (irr : Bool) (elapsed : Nat) : Decision3 :=
  liftDecision (decideX108 tau metrics theta irr elapsed)

theorem X108_no_act_before_tau (tau : Nat) (metrics : Metrics) (theta : Rat) (irr : Bool) (elapsed : Nat)
    (hIrr : irr = true)
    (h : elapsed < tau) :
    decideX108 tau metrics theta irr elapsed = Decision.HOLD := by
  unfold decideX108 beforeTau
  have hlt : decide (elapsed < tau) = true := decide_eq_true h
  rw [hIrr, hlt]
  rfl

theorem X108_after_tau_equals_base (tau : Nat) (metrics : Metrics) (theta : Rat) (irr : Bool) (elapsed : Nat)
    (h : Not (beforeTau tau elapsed irr = true)) :
    decideX108 tau metrics theta irr elapsed = decision metrics theta := by
  unfold decideX108
  cases hb : beforeTau tau elapsed irr with
  | true =>
      exfalso
      exact h hb
  | false =>
      rfl

theorem X108_kernel_never_blocks (tau : Nat) (metrics : Metrics) (theta : Rat) (irr : Bool) (elapsed : Nat) :
    Not (decide3X108 tau metrics theta irr elapsed = Decision3.BLOCK) := by
  intro h
  unfold decide3X108 at h
  cases hd : decideX108 tau metrics theta irr elapsed with
  | HOLD =>
      rw [hd] at h
      change Decision3.HOLD = Decision3.BLOCK at h
      cases h
  | ACT =>
      rw [hd] at h
      change Decision3.ACT = Decision3.BLOCK at h
      cases h

theorem X108_reversible_equals_base (tau : Nat) (metrics : Metrics) (theta : Rat) (elapsed : Nat) :
    decideX108 tau metrics theta false elapsed = decision metrics theta := by
  unfold decideX108 beforeTau
  rfl

theorem X108_irreversible_after_tau_equals_base (tau : Nat) (metrics : Metrics) (theta : Rat) (elapsed : Nat)
    (h : tau <= elapsed) :
    decideX108 tau metrics theta true elapsed = decision metrics theta := by
  apply X108_after_tau_equals_base
  intro hb
  unfold beforeTau at hb
  have hfalse : decide (elapsed < tau) = false := decide_eq_false (Nat.not_lt.mpr h)
  rw [hfalse] at hb
  cases hb

#print axioms Obsidia.TemporalKernel.X108_no_act_before_tau
#print axioms Obsidia.TemporalKernel.X108_after_tau_equals_base
#print axioms Obsidia.TemporalKernel.X108_kernel_never_blocks
#print axioms Obsidia.TemporalKernel.X108_reversible_equals_base
#print axioms Obsidia.TemporalKernel.X108_irreversible_after_tau_equals_base

end TemporalKernel
end Obsidia
```

## Theorem summary

| Theorem | What it establishes |
|---|---|
| `X108_no_act_before_tau` | For irreversible decisions, if elapsed < tau, the kernel outputs HOLD. No ACT before the temporal threshold. |
| `X108_after_tau_equals_base` | Once beforeTau is false, the kernel output is identical to the base decision function. |
| `X108_kernel_never_blocks` | The 3-valued lifted decision (`decide3X108`) never returns BLOCK. Only HOLD or ACT are reachable. |
| `X108_reversible_equals_base` | When `irr=false` (reversible), the kernel always equals the base function, regardless of tau or elapsed. |
| `X108_irreversible_after_tau_equals_base` | When elapsed >= tau, an irreversible decision equals the base function. |

## Verify independently

```bash
cd proofs/lean
lake build

# Verify axiom dependencies (should show only propext, funext, Classical axioms)
lake env lean Obsidia/TemporalKernel.lean
```

## Scope declaration

These 5 theorems cover the **temporal X108 kernel only**. They do not prove:
- Sigma layer sovereignty (PYTHON_TEST_ONLY)
- Bus bridge sovereignty (PYTHON_TEST_ONLY)
- Brody no-ACT (PYTHON_TEST_ONLY)
- Graphiti write isolation (PYTHON_TEST_ONLY)

See [PROOF_INDEX.md](PROOF_INDEX.md) for the full proof landscape.

---

_Obsidia X-108 Lean Theorems | 2026-05-30 | KX108_ONLY | Verbatim source - no edits_

