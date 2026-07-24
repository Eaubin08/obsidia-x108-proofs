namespace Obsidia
namespace Balance_math

structure BalanceState where
  left : Nat
  right : Nat
  tolerance : Nat

def delta (s : BalanceState) : Nat :=
  if s.left <= s.right then s.right - s.left else s.left - s.right

def balanced (s : BalanceState) : Prop :=
  delta s <= s.tolerance

def exact_balance (s : BalanceState) : Prop :=
  s.left = s.right

def balance_admissible (s : BalanceState) : Prop :=
  exact_balance s ∨ balanced s

theorem exact_balance_implies_balanced
    (s : BalanceState)
    (h : exact_balance s) :
    balanced s := by
  unfold balanced
  unfold delta
  unfold exact_balance at h
  rw [h]
  simp

theorem balance_admissible_from_exact
    (s : BalanceState)
    (h : exact_balance s) :
    balance_admissible s :=
  Or.inl h

theorem balance_admissible_from_balanced
    (s : BalanceState)
    (h : balanced s) :
    balance_admissible s :=
  Or.inr h

end Balance_math
end Obsidia
