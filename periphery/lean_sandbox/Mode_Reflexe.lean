namespace Obsidia
namespace ModeReflexe

-- Mode Réflexe
-- Type: model — peripherique, non-decisionnel, runtime_bound=false

inductive ModeReflexeStep where
  | init
  | active
  | complete
  deriving DecidableEq

def step_valid (s : ModeReflexeStep) : Prop :=
  s = ModeReflexeStep.active ∨ s = ModeReflexeStep.complete

theorem init_not_valid : ¬ step_valid ModeReflexeStep.init := by
  intro h; rcases h with h | h <;> exact absurd h (by decide)

theorem active_valid : step_valid ModeReflexeStep.active := Or.inl rfl

theorem complete_valid : step_valid ModeReflexeStep.complete := Or.inr rfl

end ModeReflexe
end Obsidia
