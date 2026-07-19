namespace Obsidia
namespace ReseauPheromones

-- Réseau de Phéromones
-- Type: algorithm — peripherique, non-decisionnel, runtime_bound=false

structure ReseauPheromonesState where
  active    : Bool
  validated : Bool

def reseaupheromones_valide (s : ReseauPheromonesState) : Prop :=
  s.active = true ∧ s.validated = true

def reseaupheromones_hold (s : ReseauPheromonesState) : Prop := ¬ reseaupheromones_valide s

def canonical : ReseauPheromonesState := { active := true, validated := true }

theorem canonical_valide : reseaupheromones_valide canonical := ⟨rfl, rfl⟩

theorem not_active_hold (s : ReseauPheromonesState) (h : s.active = false) :
    reseaupheromones_hold s := by
  intro hv; have ha := hv.1; simp [h] at ha

theorem not_validated_hold (s : ReseauPheromonesState) (h : s.validated = false) :
    reseaupheromones_hold s := by
  intro hv; have hv2 := hv.2; simp [h] at hv2

end ReseauPheromones
end Obsidia
