namespace Obsidia
namespace P62Attracteur

structure AttractorState where
  kernel_gravity : Bool
  converging     : Bool

def attracted (a : AttractorState) : Prop :=
  a.kernel_gravity = true ∧ a.converging = true

def not_attracted (a : AttractorState) : Prop := ¬ attracted a

def canonical_attractor : AttractorState := { kernel_gravity := true, converging := true }

theorem canonical_attracted : attracted canonical_attractor := ⟨rfl, rfl⟩

theorem no_gravity_not_attracted (a : AttractorState) (h : a.kernel_gravity = false) :
    not_attracted a := by
  intro hv; have hg := hv.1; simp [h] at hg

theorem not_converging_not_attracted (a : AttractorState) (h : a.converging = false) :
    not_attracted a := by
  intro hv; have hc := hv.2; simp [h] at hc

end P62Attracteur
end Obsidia
