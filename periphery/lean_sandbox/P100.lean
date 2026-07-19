namespace Obsidia
namespace P100

-- Stabilite Lyapunov decroissance
-- Type: formula — peripherique, non-decisionnel, runtime_bound=false

structure P100State where
  active    : Bool
  validated : Bool

def p100_valide (s : P100State) : Prop :=
  s.active = true ∧ s.validated = true

def p100_hold (s : P100State) : Prop := ¬ p100_valide s

def canonical : P100State := { active := true, validated := true }

theorem canonical_valide : p100_valide canonical := ⟨rfl, rfl⟩

theorem not_active_hold (s : P100State) (h : s.active = false) :
    p100_hold s := by
  intro hv; have ha := hv.1; simp [h] at ha

theorem not_validated_hold (s : P100State) (h : s.validated = false) :
    p100_hold s := by
  intro hv; have hv2 := hv.2; simp [h] at hv2

end P100
end Obsidia
