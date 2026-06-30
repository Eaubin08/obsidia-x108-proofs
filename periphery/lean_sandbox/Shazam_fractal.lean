namespace Obsidia
namespace Shazamfractal

-- Shazam Fractal
-- Type: algorithm — peripherique, non-decisionnel, runtime_bound=false

structure ShazamfractalState where
  active    : Bool
  validated : Bool

def shazamfractal_valide (s : ShazamfractalState) : Prop :=
  s.active = true ∧ s.validated = true

def shazamfractal_hold (s : ShazamfractalState) : Prop := ¬ shazamfractal_valide s

def canonical : ShazamfractalState := { active := true, validated := true }

theorem canonical_valide : shazamfractal_valide canonical := ⟨rfl, rfl⟩

theorem not_active_hold (s : ShazamfractalState) (h : s.active = false) :
    shazamfractal_hold s := by
  intro hv; have ha := hv.1; simp [h] at ha

theorem not_validated_hold (s : ShazamfractalState) (h : s.validated = false) :
    shazamfractal_hold s := by
  intro hv; have hv2 := hv.2; simp [h] at hv2

end Shazamfractal
end Obsidia
