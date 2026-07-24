namespace Obsidia
namespace NuageFractal

-- Nuage Fractal
-- Type: model — peripherique, non-decisionnel, runtime_bound=false

inductive NuageFractalStep where
  | init
  | active
  | complete
  deriving DecidableEq

def step_valid (s : NuageFractalStep) : Prop :=
  s = NuageFractalStep.active ∨ s = NuageFractalStep.complete

theorem init_not_valid : ¬ step_valid NuageFractalStep.init := by
  intro h; rcases h with h | h <;> exact absurd h (by decide)

theorem active_valid : step_valid NuageFractalStep.active := Or.inl rfl

theorem complete_valid : step_valid NuageFractalStep.complete := Or.inr rfl

end NuageFractal
end Obsidia
