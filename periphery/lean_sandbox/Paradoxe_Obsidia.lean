namespace Obsidia
namespace ParadoxeObsidia

-- Paradoxe d'Obsidia
-- Type: law — peripherique, non-decisionnel, runtime_bound=false

structure ParadoxeObsidiaState where
  active    : Bool
  validated : Bool

def paradoxeobsidia_valide (s : ParadoxeObsidiaState) : Prop :=
  s.active = true ∧ s.validated = true

def paradoxeobsidia_hold (s : ParadoxeObsidiaState) : Prop := ¬ paradoxeobsidia_valide s

def canonical : ParadoxeObsidiaState := { active := true, validated := true }

theorem canonical_valide : paradoxeobsidia_valide canonical := ⟨rfl, rfl⟩

theorem not_active_hold (s : ParadoxeObsidiaState) (h : s.active = false) :
    paradoxeobsidia_hold s := by
  intro hv; have ha := hv.1; simp [h] at ha

theorem not_validated_hold (s : ParadoxeObsidiaState) (h : s.validated = false) :
    paradoxeobsidia_hold s := by
  intro hv; have hv2 := hv.2; simp [h] at hv2

end ParadoxeObsidia
end Obsidia
