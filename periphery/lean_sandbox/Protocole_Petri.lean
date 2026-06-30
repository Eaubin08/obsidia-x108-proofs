namespace Obsidia
namespace ProtocolePetri

-- Protocole Petri
-- Type: protocol — peripherique, non-decisionnel, runtime_bound=false

inductive ProtocolePetriStep where
  | init
  | active
  | complete
  deriving DecidableEq

def step_valid (s : ProtocolePetriStep) : Prop :=
  s = ProtocolePetriStep.active ∨ s = ProtocolePetriStep.complete

theorem init_not_valid : ¬ step_valid ProtocolePetriStep.init := by
  intro h; rcases h with h | h <;> exact absurd h (by decide)

theorem active_valid : step_valid ProtocolePetriStep.active := Or.inl rfl

theorem complete_valid : step_valid ProtocolePetriStep.complete := Or.inr rfl

end ProtocolePetri
end Obsidia
