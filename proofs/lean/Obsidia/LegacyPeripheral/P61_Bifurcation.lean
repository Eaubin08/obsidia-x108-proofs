namespace Obsidia
namespace P61Bifurcation

structure BifurcState where
  critical_value : Nat
  threshold      : Nat

def bifurcation_maitrisee (b : BifurcState) : Prop :=
  b.critical_value ≤ b.threshold

def bifurcation_active (b : BifurcState) : Prop :=
  ¬ bifurcation_maitrisee b

def canonical_bifurc : BifurcState := { critical_value := 0, threshold := 1 }

theorem canonical_maitrisee : bifurcation_maitrisee canonical_bifurc := Nat.zero_le 1

theorem above_threshold_active (b : BifurcState) (h : b.threshold < b.critical_value) :
    bifurcation_active b := by
  intro hm; exact Nat.not_le.mpr h hm

theorem below_threshold_maitrisee (b : BifurcState) (h : b.critical_value ≤ b.threshold) :
    bifurcation_maitrisee b := h

end P61Bifurcation
end Obsidia
