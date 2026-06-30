namespace Obsidia
namespace MemoireFractale

-- Mémoire Fractale
-- Type: model — peripherique, non-decisionnel, runtime_bound=false

inductive MemoireFractaleStep where
  | init
  | active
  | complete
  deriving DecidableEq

def step_valid (s : MemoireFractaleStep) : Prop :=
  s = MemoireFractaleStep.active ∨ s = MemoireFractaleStep.complete

theorem init_not_valid : ¬ step_valid MemoireFractaleStep.init := by
  intro h; rcases h with h | h <;> exact absurd h (by decide)

theorem active_valid : step_valid MemoireFractaleStep.active := Or.inl rfl

theorem complete_valid : step_valid MemoireFractaleStep.complete := Or.inr rfl

end MemoireFractale
end Obsidia
