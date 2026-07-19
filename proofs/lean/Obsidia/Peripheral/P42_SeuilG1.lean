namespace Obsidia
namespace P42SeuilG1

structure SeuilState where
  value     : Nat
  threshold : Nat

def above_threshold (s : SeuilState) : Prop :=
  s.threshold < s.value

def below_or_equal (s : SeuilState) : Prop :=
  s.value ≤ s.threshold

theorem trichotomy (s : SeuilState) :
    above_threshold s ∨ below_or_equal s := by
  unfold above_threshold below_or_equal; omega

theorem not_both (s : SeuilState) :
    ¬ (above_threshold s ∧ below_or_equal s) := by
  intro ⟨h1, h2⟩; exact Nat.not_le.mpr h1 h2

theorem below_not_above (s : SeuilState) (h : below_or_equal s) :
    ¬ above_threshold s := by
  intro ha; exact Nat.not_le.mpr ha h

end P42SeuilG1
end Obsidia
