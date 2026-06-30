namespace Obsidia
namespace P88

-- Non-contradiction
-- Type: law — peripherique, non-decisionnel, runtime_bound=false

structure P88State where
  active    : Bool
  validated : Bool

def p88_valide (s : P88State) : Prop :=
  s.active = true ∧ s.validated = true

def p88_hold (s : P88State) : Prop := ¬ p88_valide s

def canonical : P88State := { active := true, validated := true }

theorem canonical_valide : p88_valide canonical := ⟨rfl, rfl⟩

theorem not_active_hold (s : P88State) (h : s.active = false) :
    p88_hold s := by
  intro hv; have ha := hv.1; simp [h] at ha

theorem not_validated_hold (s : P88State) (h : s.validated = false) :
    p88_hold s := by
  intro hv; have hv2 := hv.2; simp [h] at hv2

end P88
end Obsidia
