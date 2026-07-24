namespace Obsidia
namespace SimulationMentale

-- Simulation Mentale
-- Type: protocol — peripherique, non-decisionnel, runtime_bound=false

inductive SimulationMentaleStep where
  | init
  | active
  | complete
  deriving DecidableEq

def step_valid (s : SimulationMentaleStep) : Prop :=
  s = SimulationMentaleStep.active ∨ s = SimulationMentaleStep.complete

theorem init_not_valid : ¬ step_valid SimulationMentaleStep.init := by
  intro h; rcases h with h | h <;> exact absurd h (by decide)

theorem active_valid : step_valid SimulationMentaleStep.active := Or.inl rfl

theorem complete_valid : step_valid SimulationMentaleStep.complete := Or.inr rfl

end SimulationMentale
end Obsidia
