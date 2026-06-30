namespace Obsidia
namespace P107

-- Stabilite Lyapunov delta-epsilon
-- Type: model — peripherique, non-decisionnel, runtime_bound=false

inductive P107Step where
  | init
  | active
  | complete
  deriving DecidableEq

def step_valid (s : P107Step) : Prop :=
  s = P107Step.active ∨ s = P107Step.complete

theorem init_not_valid : ¬ step_valid P107Step.init := by
  intro h; rcases h with h | h <;> exact absurd h (by decide)

theorem active_valid : step_valid P107Step.active := Or.inl rfl

theorem complete_valid : step_valid P107Step.complete := Or.inr rfl

end P107
end Obsidia
