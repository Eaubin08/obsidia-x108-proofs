namespace Obsidia
namespace P149Narration

structure NarrationState where
  all_valid : Bool
  traceable : Bool

def narration_valide (n : NarrationState) : Prop :=
  n.all_valid = true ∧ n.traceable = true

def narration_hold (n : NarrationState) : Prop := ¬ narration_valide n

def canonical_narration : NarrationState := { all_valid := true, traceable := true }

theorem canonical_valide : narration_valide canonical_narration := ⟨rfl, rfl⟩

theorem all_fail_hold (n : NarrationState) (h : n.all_valid = false) :
    narration_hold n := by
  intro hv; have ha := hv.1; simp [h] at ha

theorem not_traceable_hold (n : NarrationState) (h : n.traceable = false) :
    narration_hold n := by
  intro hv; have ht := hv.2; simp [h] at ht

end P149Narration
end Obsidia
