namespace Obsidia
namespace P54TempsAbsolu

def precede (t1 t2 : Nat) : Prop := t1 < t2

theorem temps_monotone (t1 t2 : Nat) (h : precede t1 t2) : ¬ precede t2 t1 := by
  unfold precede at *; omega

theorem non_retour (t1 t2 : Nat) (h : precede t1 t2) : ¬ (t2 ≤ t1) := by
  unfold precede at *; omega

theorem temps_total (t1 t2 : Nat) : precede t1 t2 ∨ t1 = t2 ∨ precede t2 t1 := by
  unfold precede; omega

theorem zero_est_origine (t : Nat) : ¬ precede t 0 := by
  unfold precede; omega

end P54TempsAbsolu
end Obsidia
