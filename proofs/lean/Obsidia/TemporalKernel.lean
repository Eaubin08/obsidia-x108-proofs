import Obsidia.Basic

namespace Obsidia
namespace TemporalKernel

def beforeTau (τ : Nat) (elapsed : Nat) (irr : Bool) : Bool :=
  irr && decide (elapsed < τ)

def decideX108 (τ : Nat) (metrics : Metrics) (theta : Rat) (irr : Bool) (elapsed : Nat) : Decision :=
  match beforeTau τ elapsed irr with
  | true  => Decision.HOLD
  | false => decision metrics theta

def decide3X108 (τ : Nat) (metrics : Metrics) (theta : Rat) (irr : Bool) (elapsed : Nat) : Decision3 :=
  liftDecision (decideX108 τ metrics theta irr elapsed)

theorem X108_no_act_before_tau (τ : Nat) (metrics : Metrics) (theta : Rat) (irr : Bool) (elapsed : Nat)
    (hIrr : irr = true)
    (h : elapsed < τ) :
    decideX108 τ metrics theta irr elapsed = Decision.HOLD := by
  unfold decideX108 beforeTau
  have hlt : decide (elapsed < τ) = true := decide_eq_true h
  rw [hIrr, hlt]
  rfl

theorem X108_after_tau_equals_base (τ : Nat) (metrics : Metrics) (theta : Rat) (irr : Bool) (elapsed : Nat)
    (h : Not (beforeTau τ elapsed irr = true)) :
    decideX108 τ metrics theta irr elapsed = decision metrics theta := by
  unfold decideX108
  cases hb : beforeTau τ elapsed irr with
  | true =>
      exfalso
      exact h hb
  | false =>
      rfl

theorem X108_kernel_never_blocks (τ : Nat) (metrics : Metrics) (theta : Rat) (irr : Bool) (elapsed : Nat) :
    Not (decide3X108 τ metrics theta irr elapsed = Decision3.BLOCK) := by
  intro h
  unfold decide3X108 at h
  cases hd : decideX108 τ metrics theta irr elapsed with
  | HOLD =>
      rw [hd] at h
      change Decision3.HOLD = Decision3.BLOCK at h
      cases h
  | ACT =>
      rw [hd] at h
      change Decision3.ACT = Decision3.BLOCK at h
      cases h

theorem X108_reversible_equals_base (τ : Nat) (metrics : Metrics) (theta : Rat) (elapsed : Nat) :
    decideX108 τ metrics theta false elapsed = decision metrics theta := by
  unfold decideX108 beforeTau
  rfl

theorem X108_irreversible_after_tau_equals_base (τ : Nat) (metrics : Metrics) (theta : Rat) (elapsed : Nat)
    (h : τ ≤ elapsed) :
    decideX108 τ metrics theta true elapsed = decision metrics theta := by
  apply X108_after_tau_equals_base
  intro hb
  unfold beforeTau at hb
  have hfalse : decide (elapsed < τ) = false := decide_eq_false (Nat.not_lt.mpr h)
  rw [hfalse] at hb
  cases hb

#print axioms Obsidia.TemporalKernel.X108_no_act_before_tau
#print axioms Obsidia.TemporalKernel.X108_after_tau_equals_base
#print axioms Obsidia.TemporalKernel.X108_kernel_never_blocks
#print axioms Obsidia.TemporalKernel.X108_reversible_equals_base
#print axioms Obsidia.TemporalKernel.X108_irreversible_after_tau_equals_base

end TemporalKernel
end Obsidia
