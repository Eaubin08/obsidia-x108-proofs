namespace Obsidia
namespace LoiAccelerationMaitrisee

-- Loi d'Accélération Maîtrisée
-- Type: law — peripherique, non-decisionnel, runtime_bound=false

structure LoiAccelerationMaitriseeState where
  active    : Bool
  validated : Bool

def loiaccelerationmaitrisee_valide (s : LoiAccelerationMaitriseeState) : Prop :=
  s.active = true ∧ s.validated = true

def loiaccelerationmaitrisee_hold (s : LoiAccelerationMaitriseeState) : Prop := ¬ loiaccelerationmaitrisee_valide s

def canonical : LoiAccelerationMaitriseeState := { active := true, validated := true }

theorem canonical_valide : loiaccelerationmaitrisee_valide canonical := ⟨rfl, rfl⟩

theorem not_active_hold (s : LoiAccelerationMaitriseeState) (h : s.active = false) :
    loiaccelerationmaitrisee_hold s := by
  intro hv; have ha := hv.1; simp [h] at ha

theorem not_validated_hold (s : LoiAccelerationMaitriseeState) (h : s.validated = false) :
    loiaccelerationmaitrisee_hold s := by
  intro hv; have hv2 := hv.2; simp [h] at hv2

end LoiAccelerationMaitrisee
end Obsidia
