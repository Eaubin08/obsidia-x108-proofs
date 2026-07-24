namespace Obsidia
namespace P59KolmogorovComplexity

structure KolmogorovState where
  compressible : Bool
  redundant    : Bool

def complexity_low (k : KolmogorovState) : Prop :=
  k.compressible = true ∧ k.redundant = true

def complexity_hold (k : KolmogorovState) : Prop := ¬ complexity_low k

def canonical_state : KolmogorovState := { compressible := true, redundant := true }

theorem canonical_low : complexity_low canonical_state := ⟨rfl, rfl⟩

theorem not_compressible_hold (k : KolmogorovState) (h : k.compressible = false) :
    complexity_hold k := by
  intro hv; have hc := hv.1; simp [h] at hc

theorem not_redundant_hold (k : KolmogorovState) (h : k.redundant = false) :
    complexity_hold k := by
  intro hv; have hr := hv.2; simp [h] at hr

end P59KolmogorovComplexity
end Obsidia
