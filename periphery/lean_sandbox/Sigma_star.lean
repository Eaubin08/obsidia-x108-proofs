namespace Obsidia
namespace Sigmastar

-- Sigma★ Vérité Fractale
-- Type: formula — peripherique, non-decisionnel, runtime_bound=false

structure SigmastarState where
  active    : Bool
  validated : Bool

def sigmastar_valide (s : SigmastarState) : Prop :=
  s.active = true ∧ s.validated = true

def sigmastar_hold (s : SigmastarState) : Prop := ¬ sigmastar_valide s

def canonical : SigmastarState := { active := true, validated := true }

theorem canonical_valide : sigmastar_valide canonical := ⟨rfl, rfl⟩

theorem not_active_hold (s : SigmastarState) (h : s.active = false) :
    sigmastar_hold s := by
  intro hv; have ha := hv.1; simp [h] at ha

theorem not_validated_hold (s : SigmastarState) (h : s.validated = false) :
    sigmastar_hold s := by
  intro hv; have hv2 := hv.2; simp [h] at hv2

end Sigmastar
end Obsidia
