namespace Obsidia
namespace BoucleEtincelle

-- Boucle Étincelle
-- Type: protocol — peripherique, non-decisionnel, runtime_bound=false

inductive BoucleEtincelleStep where
  | init
  | active
  | complete
  deriving DecidableEq

def step_valid (s : BoucleEtincelleStep) : Prop :=
  s = BoucleEtincelleStep.active ∨ s = BoucleEtincelleStep.complete

theorem init_not_valid : ¬ step_valid BoucleEtincelleStep.init := by
  intro h; rcases h with h | h <;> exact absurd h (by decide)

theorem active_valid : step_valid BoucleEtincelleStep.active := Or.inl rfl

theorem complete_valid : step_valid BoucleEtincelleStep.complete := Or.inr rfl

end BoucleEtincelle
end Obsidia
