namespace Obsidia
namespace ACP

-- ACP — Action→Calibration→Progression
-- Type: protocol — peripherique, non-decisionnel, runtime_bound=false

inductive ACPStep where
  | init
  | active
  | complete
  deriving DecidableEq

def step_valid (s : ACPStep) : Prop :=
  s = ACPStep.active ∨ s = ACPStep.complete

theorem init_not_valid : ¬ step_valid ACPStep.init := by
  intro h; rcases h with h | h <;> exact absurd h (by decide)

theorem active_valid : step_valid ACPStep.active := Or.inl rfl

theorem complete_valid : step_valid ACPStep.complete := Or.inr rfl

end ACP
end Obsidia
