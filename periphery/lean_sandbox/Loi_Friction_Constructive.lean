namespace Obsidia
namespace LoiFrictionConstructive

-- Loi de la Friction Constructive
-- Type: law — peripherique, non-decisionnel, runtime_bound=false

structure LoiFrictionConstructiveState where
  active    : Bool
  validated : Bool

def loifrictionconstructive_valide (s : LoiFrictionConstructiveState) : Prop :=
  s.active = true ∧ s.validated = true

def loifrictionconstructive_hold (s : LoiFrictionConstructiveState) : Prop := ¬ loifrictionconstructive_valide s

def canonical : LoiFrictionConstructiveState := { active := true, validated := true }

theorem canonical_valide : loifrictionconstructive_valide canonical := ⟨rfl, rfl⟩

theorem not_active_hold (s : LoiFrictionConstructiveState) (h : s.active = false) :
    loifrictionconstructive_hold s := by
  intro hv; have ha := hv.1; simp [h] at ha

theorem not_validated_hold (s : LoiFrictionConstructiveState) (h : s.validated = false) :
    loifrictionconstructive_hold s := by
  intro hv; have hv2 := hv.2; simp [h] at hv2

end LoiFrictionConstructive
end Obsidia
