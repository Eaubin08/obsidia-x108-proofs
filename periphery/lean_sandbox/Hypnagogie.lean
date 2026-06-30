namespace Obsidia
namespace Hypnagogie

-- Hypnagogie
-- Type: protocol — peripherique, non-decisionnel, runtime_bound=false

inductive HypnagogieStep where
  | init
  | active
  | complete
  deriving DecidableEq

def step_valid (s : HypnagogieStep) : Prop :=
  s = HypnagogieStep.active ∨ s = HypnagogieStep.complete

theorem init_not_valid : ¬ step_valid HypnagogieStep.init := by
  intro h; rcases h with h | h <;> exact absurd h (by decide)

theorem active_valid : step_valid HypnagogieStep.active := Or.inl rfl

theorem complete_valid : step_valid HypnagogieStep.complete := Or.inr rfl

end Hypnagogie
end Obsidia
