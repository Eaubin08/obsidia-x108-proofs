import Obsidia.CryptoAssumptions

namespace Obsidia

 def merkle2 (a b : Hash) : Hash :=
  H a b

theorem merkle2_left_mutation
  (a a' b : Hash)
  (h : a ≠ a') :
  merkle2 a b ≠ merkle2 a' b := by
  unfold merkle2
  intro h_eq
  apply h
  exact H_injective_left h_eq

theorem merkle2_right_mutation
  (a b b' : Hash)
  (h : b ≠ b') :
  merkle2 a b ≠ merkle2 a b' := by
  unfold merkle2
  intro h_eq
  apply h
  exact H_injective_right h_eq

end Obsidia
