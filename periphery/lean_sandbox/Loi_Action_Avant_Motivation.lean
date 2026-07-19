namespace Obsidia
namespace LoiActionAvantMotivation

-- Loi Action Avant Motivation
-- Type: law — peripherique, non-decisionnel, runtime_bound=false

structure LoiActionAvantMotivationState where
  active    : Bool
  validated : Bool

def loiactionavantmotivation_valide (s : LoiActionAvantMotivationState) : Prop :=
  s.active = true ∧ s.validated = true

def loiactionavantmotivation_hold (s : LoiActionAvantMotivationState) : Prop := ¬ loiactionavantmotivation_valide s

def canonical : LoiActionAvantMotivationState := { active := true, validated := true }

theorem canonical_valide : loiactionavantmotivation_valide canonical := ⟨rfl, rfl⟩

theorem not_active_hold (s : LoiActionAvantMotivationState) (h : s.active = false) :
    loiactionavantmotivation_hold s := by
  intro hv; have ha := hv.1; simp [h] at ha

theorem not_validated_hold (s : LoiActionAvantMotivationState) (h : s.validated = false) :
    loiactionavantmotivation_hold s := by
  intro hv; have hv2 := hv.2; simp [h] at hv2

end LoiActionAvantMotivation
end Obsidia
