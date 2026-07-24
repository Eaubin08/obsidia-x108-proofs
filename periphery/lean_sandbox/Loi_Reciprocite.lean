namespace Obsidia
namespace LoiReciprocite

-- Loi de Réciprocité
-- Type: law — peripherique, non-decisionnel, runtime_bound=false

structure LoiReciprociteState where
  active    : Bool
  validated : Bool

def loireciprocite_valide (s : LoiReciprociteState) : Prop :=
  s.active = true ∧ s.validated = true

def loireciprocite_hold (s : LoiReciprociteState) : Prop := ¬ loireciprocite_valide s

def canonical : LoiReciprociteState := { active := true, validated := true }

theorem canonical_valide : loireciprocite_valide canonical := ⟨rfl, rfl⟩

theorem not_active_hold (s : LoiReciprociteState) (h : s.active = false) :
    loireciprocite_hold s := by
  intro hv; have ha := hv.1; simp [h] at ha

theorem not_validated_hold (s : LoiReciprociteState) (h : s.validated = false) :
    loireciprocite_hold s := by
  intro hv; have hv2 := hv.2; simp [h] at hv2

end LoiReciprocite
end Obsidia
