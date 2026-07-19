namespace Obsidia
namespace P42

-- Seuil admissibilite G1
-- Type: law — peripherique, non-decisionnel, runtime_bound=false

structure P42State where
  active    : Bool
  validated : Bool

def p42_valide (s : P42State) : Prop :=
  s.active = true ∧ s.validated = true

def p42_hold (s : P42State) : Prop := ¬ p42_valide s

def canonical : P42State := { active := true, validated := true }

theorem canonical_valide : p42_valide canonical := ⟨rfl, rfl⟩

theorem not_active_hold (s : P42State) (h : s.active = false) :
    p42_hold s := by
  intro hv; have ha := hv.1; simp [h] at ha

theorem not_validated_hold (s : P42State) (h : s.validated = false) :
    p42_hold s := by
  intro hv; have hv2 := hv.2; simp [h] at hv2

end P42
end Obsidia
