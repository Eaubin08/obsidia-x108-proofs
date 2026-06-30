namespace Obsidia
namespace CapteursOndeLimite

-- Capteurs Onde Limite
-- Type: model — peripherique, non-decisionnel, runtime_bound=false

inductive CapteursOndeLimiteStep where
  | init
  | active
  | complete
  deriving DecidableEq

def step_valid (s : CapteursOndeLimiteStep) : Prop :=
  s = CapteursOndeLimiteStep.active ∨ s = CapteursOndeLimiteStep.complete

theorem init_not_valid : ¬ step_valid CapteursOndeLimiteStep.init := by
  intro h; rcases h with h | h <;> exact absurd h (by decide)

theorem active_valid : step_valid CapteursOndeLimiteStep.active := Or.inl rfl

theorem complete_valid : step_valid CapteursOndeLimiteStep.complete := Or.inr rfl

end CapteursOndeLimite
end Obsidia
