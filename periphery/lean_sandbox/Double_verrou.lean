namespace Obsidia
namespace Doubleverrou

-- Double-verrou
-- Type: protocol — peripherique, non-decisionnel, runtime_bound=false

inductive DoubleverrouStep where
  | init
  | active
  | complete
  deriving DecidableEq

def step_valid (s : DoubleverrouStep) : Prop :=
  s = DoubleverrouStep.active ∨ s = DoubleverrouStep.complete

theorem init_not_valid : ¬ step_valid DoubleverrouStep.init := by
  intro h; rcases h with h | h <;> exact absurd h (by decide)

theorem active_valid : step_valid DoubleverrouStep.active := Or.inl rfl

theorem complete_valid : step_valid DoubleverrouStep.complete := Or.inr rfl

end Doubleverrou
end Obsidia
