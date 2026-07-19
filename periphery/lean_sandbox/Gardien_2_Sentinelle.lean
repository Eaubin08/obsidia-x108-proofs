namespace Obsidia
namespace Gardien2Sentinelle

-- Gardien 2 Sentinelle
-- Type: model — peripherique, non-decisionnel, runtime_bound=false

inductive Gardien2SentinelleStep where
  | init
  | active
  | complete
  deriving DecidableEq

def step_valid (s : Gardien2SentinelleStep) : Prop :=
  s = Gardien2SentinelleStep.active ∨ s = Gardien2SentinelleStep.complete

theorem init_not_valid : ¬ step_valid Gardien2SentinelleStep.init := by
  intro h; rcases h with h | h <;> exact absurd h (by decide)

theorem active_valid : step_valid Gardien2SentinelleStep.active := Or.inl rfl

theorem complete_valid : step_valid Gardien2SentinelleStep.complete := Or.inr rfl

end Gardien2Sentinelle
end Obsidia
